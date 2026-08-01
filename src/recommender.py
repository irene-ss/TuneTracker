from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read the songs CSV and return a list of song dictionaries."""
    import csv

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "acousticness": float(row["acousticness"]),
                    "popularity": float(row.get("popularity", 0.0)),
                    "duration": float(row.get("duration", 0.0)),
                }
            )

    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song against user preferences and return the score plus reasons."""
    score = 0.0
    reasons: List[str] = []

    preferred_genre = str(user_prefs.get("genre", "")).strip().lower()
    preferred_mood = str(user_prefs.get("mood", "")).strip().lower()
    target_energy = float(user_prefs.get("energy", 0.5))

    song_genre = str(song.get("genre", "")).strip().lower()
    song_mood = str(song.get("mood", "")).strip().lower()
    song_energy = float(song.get("energy", 0.5))

    if preferred_genre and song_genre == preferred_genre:
        score += 1.5
        reasons.append("Genre match +1.5")

    if preferred_mood and song_mood == preferred_mood:
        score += 1.4
        reasons.append("Mood match +1.4")

    energy_distance = abs(song_energy - target_energy)
    energy_score = max(0.0, 1.5 * (1.0 - energy_distance))
    score += energy_score
    reasons.append(f"Energy similarity +{energy_score:.2f}")

    if user_prefs.get("likes_acoustic") and float(song.get("acousticness", 0.0)) >= 0.7:
        score += 0.5
        reasons.append("Acoustic preference bonus +0.5")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top k recommendations."""
    scored_songs: List[Tuple[Dict, float, str]] = [
        (
            song,
            score,
            "; ".join(reasons) if reasons else "No strong matches found."
        )
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    ranked_songs = sorted(
        scored_songs,
        key=lambda item: (-item[1], item[0].get("title", ""))
    )
    return ranked_songs[:k]
