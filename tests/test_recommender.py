"""
Tests for the recommender: per-strategy scoring correctness and rank determinism.
"""

import pytest

from recommender import (
    Song,
    UserProfile,
    Recommender,
    GenreFirstStrategy,
    MoodFirstStrategy,
    EnergyFocusedStrategy,
    BalancedStrategy,
)


def make_song(id, title, genre, mood, energy, acousticness=0.2):
    """Build a Song with sensible defaults for the fields we don't test."""
    return Song(
        id=id,
        title=title,
        artist="Test Artist",
        genre=genre,
        mood=mood,
        energy=energy,
        tempo_bpm=120,
        valence=0.7,
        danceability=0.6,
        acousticness=acousticness,
    )


def make_small_recommender() -> Recommender:
    songs = [
        make_song(1, "Test Pop Track", "pop", "happy", 0.8, acousticness=0.2),
        make_song(2, "Chill Lofi Loop", "lofi", "chill", 0.4, acousticness=0.9),
    ]
    return Recommender(songs)


# --- Per-strategy scoring correctness ---------------------------------------

# A song that matches the user on genre AND mood, with exact energy (distance 0),
# so the energy term equals the strategy's energy_weight. No acoustic bonus.
FULL_MATCH_SONG = make_song(1, "Full Match", "pop", "happy", 0.8, acousticness=0.2)
FULL_MATCH_USER = UserProfile(
    favorite_genre="pop", favorite_mood="happy", target_energy=0.8, likes_acoustic=False
)


@pytest.mark.parametrize(
    "strategy, expected",
    [
        # genre + mood + energy(=weight*1)
        (GenreFirstStrategy(), 2.0 + 1.0 + 1.0),   # 4.0
        (MoodFirstStrategy(), 1.0 + 2.0 + 1.0),    # 4.0
        (EnergyFocusedStrategy(), 0.5 + 0.5 + 2.5),  # 3.5
        (BalancedStrategy(), 1.5 + 1.4 + 1.5),     # 4.4
    ],
)
def test_strategy_scores_full_match(strategy, expected):
    score, reasons = strategy.score(FULL_MATCH_USER, FULL_MATCH_SONG)
    assert score == pytest.approx(expected)
    assert reasons  # non-empty reasons on a full match


def test_energy_term_scales_with_distance():
    """Energy score = weight * (1 - |song.energy - target|), floored at 0."""
    user = UserProfile("rock", "intense", target_energy=0.5, likes_acoustic=False)
    song = make_song(1, "Off Energy", "pop", "chill", energy=0.9)  # no genre/mood match
    # EnergyFocused energy_weight=2.5, distance=0.4 -> 2.5*(1-0.4)=1.5
    score, _ = EnergyFocusedStrategy().score(user, song)
    assert score == pytest.approx(1.5)


def test_energy_score_never_negative():
    """A huge energy distance floors the energy term at 0, not below."""
    user = UserProfile("x", "y", target_energy=0.0, likes_acoustic=False)
    song = make_song(1, "Max Energy", "a", "b", energy=1.0)  # distance 1.0
    score, _ = EnergyFocusedStrategy().score(user, song)  # 2.5*(1-1.0)=0
    assert score == pytest.approx(0.0)


def test_acoustic_bonus_applied_only_when_wanted_and_present():
    user_wants = UserProfile("x", "y", target_energy=0.5, likes_acoustic=True)
    user_no = UserProfile("x", "y", target_energy=0.5, likes_acoustic=False)
    acoustic_song = make_song(1, "Acoustic", "a", "b", energy=0.5, acousticness=0.9)
    electric_song = make_song(2, "Electric", "a", "b", energy=0.5, acousticness=0.1)

    base = EnergyFocusedStrategy().score(user_no, acoustic_song)[0]
    with_bonus = EnergyFocusedStrategy().score(user_wants, acoustic_song)[0]
    assert with_bonus == pytest.approx(base + 0.5)  # +0.5 acoustic bonus

    # Wants acoustic but the song isn't acoustic enough -> no bonus.
    no_bonus = EnergyFocusedStrategy().score(user_wants, electric_song)[0]
    assert no_bonus == pytest.approx(EnergyFocusedStrategy().score(user_no, electric_song)[0])


def test_strategies_produce_different_scores():
    """The whole point of the pattern: strategies weight the same song differently."""
    gf = GenreFirstStrategy().score(FULL_MATCH_USER, FULL_MATCH_SONG)[0]
    ef = EnergyFocusedStrategy().score(FULL_MATCH_USER, FULL_MATCH_SONG)[0]
    assert gf != ef


# --- Rank determinism & ordering --------------------------------------------

def test_recommend_orders_by_score_descending():
    user = UserProfile("pop", "happy", target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)
    assert [s.title for s in results] == ["Test Pop Track", "Chill Lofi Loop"]
    assert results[0].genre == "pop" and results[0].mood == "happy"


def test_rank_is_deterministic_across_calls():
    """Repeated calls with the same inputs return the same order."""
    user = UserProfile("pop", "happy", target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    first = [s.id for s in rec.recommend(user, k=2)]
    for _ in range(5):
        assert [s.id for s in rec.recommend(user, k=2)] == first


def test_tie_break_is_alphabetical_by_title():
    """Equal-scoring songs are ordered by title (the sort's secondary key)."""
    user = UserProfile("pop", "happy", target_energy=0.8, likes_acoustic=False)
    # Two identical songs except title -> identical score -> title decides order.
    songs = [
        make_song(1, "Zebra Song", "pop", "happy", 0.8),
        make_song(2, "Apple Song", "pop", "happy", 0.8),
    ]
    rec = Recommender(songs)
    results = rec.recommend(user, k=2)
    assert [s.title for s in results] == ["Apple Song", "Zebra Song"]


def test_recommend_respects_k():
    user = UserProfile("pop", "happy", target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    assert len(rec.recommend(user, k=1)) == 1
    assert len(rec.recommend(user, k=2)) == 2


def test_default_strategy_is_balanced():
    rec = make_small_recommender()  # no strategy passed
    assert isinstance(rec.strategy, BalancedStrategy)


# --- Explanation -------------------------------------------------------------

def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile("pop", "happy", target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
