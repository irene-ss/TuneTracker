"""
Command line runner for the Music Recommender Simulation.

Demonstrates the Strategy pattern: the same songs and the same user profile are
ranked by interchangeable strategies (Genre-First, Mood-First, Energy-Focused).
Recommender never knows which strategy is active — it just calls strategy.score().
"""

from typing import Dict, List

from recommender import (
    load_songs,
    Song,
    UserProfile,
    Recommender,
    STRATEGIES,
)


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


def print_ranking(rec: Recommender, user: UserProfile, k: int = 5) -> None:
    """Print the top-k ranking for the recommender's current strategy."""
    print(f"  Mode: {rec.strategy.name}")
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


def main() -> None:
    songs = [to_song(row) for row in load_songs("data/songs.csv")]

    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8}),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.4}),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.9}),
    ]

    modes = choose_modes()

    for profile_name, prefs in profiles:
        user = to_profile(prefs)
        print(f"\n=== {profile_name} ===")
        print("=" * 60)
        # Run each selected strategy on the SAME profile so rankings are comparable.
        for mode in modes:
            rec = Recommender(songs, STRATEGIES[mode]())
            print_ranking(rec, user, k=5)


if __name__ == "__main__":
    main()
