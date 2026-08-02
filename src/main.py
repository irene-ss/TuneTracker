"""
Command line runner for the Music Recommender Simulation.

Demonstrates two independent pieces working side by side:

1. Retrieval (retriever.py) — a free-text query is matched against song
   descriptions via TF-IDF + cosine similarity. Text-based, ignores the profile.
2. Scoring (recommender.py) — the structured UserProfile is ranked by an
   interchangeable strategy (Strategy pattern). Attribute-based, ignores the query.

For each profile we print the retrieved docs first, then the ranked list, so you
can see retrieval working independent of scoring.
"""

from typing import Dict, List

from recommender import (
    load_songs,
    Song,
    UserProfile,
    Recommender,
    STRATEGIES,
)
from retriever import Retriever
from logging_config import setup_logging, log_query, log_error


def to_song(row: Dict) -> Song:
    """Convert a load_songs() dict into a Song dataclass.

    The CSV has no `danceability` column, so it defaults to 0.0.
    """
    return Song(
        id=int(row["id"]),
        title=row["title"],
        artist=row["artist"],
        genre=row["genre"],
        mood=row["mood"],
        energy=float(row["energy"]),
        tempo_bpm=float(row["tempo_bpm"]),
        valence=float(row["valence"]),
        danceability=float(row.get("danceability", 0.0)),
        acousticness=float(row["acousticness"]),
    )


def to_profile(prefs: Dict) -> UserProfile:
    """Convert a simple prefs dict into a UserProfile dataclass."""
    return UserProfile(
        favorite_genre=prefs["genre"],
        favorite_mood=prefs["mood"],
        target_energy=prefs["energy"],
        likes_acoustic=prefs.get("likes_acoustic", False),
    )


def print_retrieval(retriever: Retriever, query: str, k: int = 3) -> None:
    """Print the top-k retrieval matches for a free-text query."""
    print(f"  Retrieval for query: {query!r}")
    print("  " + "-" * 58)
    results = retriever.search(query, k=k)
    if not results:
        print("  (no text matches)")
    for index, result in enumerate(results, start=1):
        print(f"  {index}. {result.title} by {result.artist}  (similarity {result.score:.3f})")
    print()


def print_ranking(rec: Recommender, user: UserProfile, k: int = 5) -> None:
    """Print the top-k ranking for the recommender's current strategy."""
    print(f"  Scoring mode: {rec.strategy.name}")
    print("  " + "-" * 58)
    for index, song in enumerate(rec.recommend(user, k=k), start=1):
        score, _ = rec.strategy.score(user, song)
        print(f"  {index}. {song.title} by {song.artist}  (score {score:.2f})")
        print(f"     Reasons: {rec.explain_recommendation(user, song)}")
    print()


def choose_modes() -> List[str]:
    """Ask the user which mode(s) to run. Blank / 'all' compares every mode."""
    options = ", ".join(STRATEGIES.keys())
    choice = input(f"Pick a mode [{options}] or Enter for all: ").strip().lower()
    if not choice or choice == "all":
        return list(STRATEGIES.keys())
    if choice in STRATEGIES:
        return [choice]
    print(f"Unknown mode '{choice}', comparing all instead.")
    return list(STRATEGIES.keys())


def choose_query() -> str:
    """Ask for a free-text query to apply to every profile. Blank uses per-profile defaults."""
    return input("Free-text query (Enter to use each profile's default): ").strip()


def main() -> None:
    setup_logging()  # initialize logging to logs/app.log
    songs = [to_song(row) for row in load_songs("data/songs.csv")]
    retriever = Retriever.from_json()

    # Each profile pairs a structured preference dict with a default free-text query.
    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8},
         "upbeat energetic pop to start the day"),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.4},
         "calm lo-fi beats for studying and focus"),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.9},
         "intense heavy rock for an intense workout"),
    ]

    modes = choose_modes()
    query_override = choose_query()

    for profile_name, prefs, default_query in profiles:
        user = to_profile(prefs)
        query = query_override or default_query
        log_query(query, k=3, mode=",".join(modes))

        print(f"\n=== {profile_name} ===")
        print("=" * 60)

        # 1) Retrieval first — text-based, independent of the profile/scoring.
        # (retriever.search logs the retrieval itself.)
        print_retrieval(retriever, query, k=3)

        # 2) Scoring — attribute-based ranking, one block per selected strategy.
        for mode in modes:
            rec = Recommender(songs, STRATEGIES[mode]())
            print_ranking(rec, user, k=5)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Log any unhandled error before it surfaces to the console.
        log_error("main", exc)
        raise
