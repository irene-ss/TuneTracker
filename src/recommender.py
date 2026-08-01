from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

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

class RankingStrategy(ABC):
    """
    Abstract base for song ranking strategies (Strategy pattern).

    A strategy is the single unit of logic that Recommender depends on: given a
    user and a song, return a numeric score plus human-readable reasons. Concrete
    strategies differ only in how heavily they weight each attribute, so
    Recommender never needs to know which one is active.
    """
    name: str = "base"

    @abstractmethod
    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Return (score, reasons) for one song against one user's preferences."""
        ...


class WeightedStrategy(RankingStrategy):
    """
    Shared weighted scoring. Every concrete strategy is just a different set of
    weights over the same three signals (genre / mood / energy) plus a small
    shared acoustic bonus. Subclass and set the weights to change the emphasis.
    """
    genre_weight: float = 1.0
    mood_weight: float = 1.0
    energy_weight: float = 1.0
    acoustic_bonus: float = 0.5
    name: str = "weighted"

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        total = 0.0
        reasons: List[str] = []

        if user.favorite_genre.strip().lower() == song.genre.strip().lower():
            total += self.genre_weight
            reasons.append(f"Genre match +{self.genre_weight:.2f}")

        if user.favorite_mood.strip().lower() == song.mood.strip().lower():
            total += self.mood_weight
            reasons.append(f"Mood match +{self.mood_weight:.2f}")

        energy_distance = abs(song.energy - user.target_energy)
        energy_score = max(0.0, self.energy_weight * (1.0 - energy_distance))
        total += energy_score
        reasons.append(f"Energy similarity +{energy_score:.2f}")

        if user.likes_acoustic and song.acousticness >= 0.7:
            total += self.acoustic_bonus
            reasons.append(f"Acoustic preference bonus +{self.acoustic_bonus:.2f}")

        return total, reasons


class GenreFirstStrategy(WeightedStrategy):
    """Genre dominates; mood and energy are secondary."""
    name = "genre-first"
    genre_weight = 2.0
    mood_weight = 1.0
    energy_weight = 1.0


class MoodFirstStrategy(WeightedStrategy):
    """Mood dominates; genre and energy are secondary."""
    name = "mood-first"
    genre_weight = 1.0
    mood_weight = 2.0
    energy_weight = 1.0


class EnergyFocusedStrategy(WeightedStrategy):
    """Energy similarity dominates; genre and mood become small bonuses."""
    name = "energy-focused"
    genre_weight = 0.5
    mood_weight = 0.5
    energy_weight = 2.5


class BalancedStrategy(WeightedStrategy):
    """Default: preserves the project's original weighting formula."""
    name = "balanced"
    genre_weight = 1.5
    mood_weight = 1.4
    energy_weight = 1.5


# Runtime registry: the ONLY place that maps a user's choice to a concrete class,
# so strategy selection stays isolated from Recommender.
STRATEGIES: Dict[str, type] = {
    "genre-first": GenreFirstStrategy,
    "mood-first": MoodFirstStrategy,
    "energy-focused": EnergyFocusedStrategy,
    "balanced": BalancedStrategy,
}


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    Recommender is unaware of which ranking strategy is active — it only calls
    strategy.score(). Pass any RankingStrategy in; defaults to BalancedStrategy.
    """
    def __init__(self, songs: List[Song], strategy: Optional[RankingStrategy] = None):
        self.songs = songs
        self.strategy: RankingStrategy = strategy or BalancedStrategy()

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        ranked = sorted(
            self.songs,
            key=lambda song: (-self.strategy.score(user, song)[0], song.title),
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self.strategy.score(user, song)
        return "; ".join(reasons) if reasons else "No strong matches found."

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
