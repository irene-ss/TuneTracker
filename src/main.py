"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    profiles = [
        ("High-Energy Pop", {"genre": "pop", "mood": "happy", "energy": 0.8}),
        ("Chill Lofi", {"genre": "lofi", "mood": "chill", "energy": 0.4}),
        ("Deep Intense Rock", {"genre": "rock", "mood": "intense", "energy": 0.9}),
    ]

    for profile_name, user_prefs in profiles:
        print(f"\n=== {profile_name} ===")
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print("Top recommendations")
        print("=" * 60)
        for index, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{index}. {song['title']} by {song['artist']}")
            print(f"   Score   : {score:.2f}")
            print(f"   Reasons : {explanation}")
            print("-" * 60)


if __name__ == "__main__":
    main()
