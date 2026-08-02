"""
Text retrieval over song descriptions.

Retriever indexes each song's description (plus title and artist) with a TF-IDF
vectorizer and ranks songs against a free-text query by cosine similarity.

Design goals:
- Dependency-light: scikit-learn only. No internet-dependent embedding API, so the
  index is fully reproducible for anyone cloning the repo.
- Deterministic: TF-IDF over local text yields the same results on every machine.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from logging_config import log_retrieval


# Default location of the descriptions file, resolved relative to the repo root
# (this file lives in src/, so its parent's parent is the project root).
DEFAULT_DESCRIPTIONS_PATH = Path(__file__).resolve().parent.parent / "data" / "song_descriptions.json"


@dataclass
class RetrievalResult:
    """A single ranked match returned by Retriever.search()."""
    song_id: str
    title: str
    artist: str
    description: str
    score: float


class Retriever:
    """
    TF-IDF + cosine-similarity retriever over song descriptions.

    Usage:
        retriever = Retriever.from_json("data/song_descriptions.json")
        results = retriever.search("something calm for studying", k=3)
        for r in results:
            print(r.title, r.score)
    """

    def __init__(self, songs: List[Dict]):
        """
        Args:
            songs: list of dicts, each with keys id, title, artist, description.
        """
        if not songs:
            raise ValueError("Retriever needs at least one song to index.")

        self.songs = songs
        self._corpus = [self._document(song) for song in songs]

        # TF-IDF over unigrams + bigrams, English stop words removed. sublinear_tf
        # dampens the effect of very repetitive terms. Everything is local and
        # deterministic — no external models or network calls.
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(self._corpus)

    @staticmethod
    def _document(song: Dict) -> str:
        """Combine the searchable fields of a song into one text document."""
        return " ".join(
            str(song.get(field, ""))
            for field in ("title", "artist", "description")
        )

    @classmethod
    def from_json(cls, path: Optional[str | Path] = None) -> "Retriever":
        """
        Build a Retriever from a song_descriptions.json file.

        The JSON is expected to map song_id -> {title, artist, description}.
        """
        json_path = Path(path) if path is not None else DEFAULT_DESCRIPTIONS_PATH
        with open(json_path, encoding="utf-8") as handle:
            raw: Dict[str, Dict] = json.load(handle)

        songs = [
            {
                "id": song_id,
                "title": entry.get("title", ""),
                "artist": entry.get("artist", ""),
                "description": entry.get("description", ""),
            }
            for song_id, entry in raw.items()
        ]
        return cls(songs)

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        """
        Return the top-k songs most similar to a free-text query.

        Results are sorted by cosine similarity (descending). Songs with zero
        similarity (no shared vocabulary with the query) are omitted.
        """
        if not query or not query.strip():
            return []
        if k <= 0:
            return []

        query_vec = self.vectorizer.transform([query])
        # cosine_similarity returns a 1 x n_songs matrix; take the first row.
        scores = cosine_similarity(query_vec, self.matrix)[0]

        # Rank indices by score, highest first, dropping zero-similarity matches.
        ranked = sorted(
            range(len(self.songs)),
            key=lambda i: scores[i],
            reverse=True,
        )

        results: List[RetrievalResult] = []
        for i in ranked:
            if scores[i] <= 0.0:
                break
            song = self.songs[i]
            results.append(
                RetrievalResult(
                    song_id=str(song["id"]),
                    title=song["title"],
                    artist=song["artist"],
                    description=song["description"],
                    score=float(scores[i]),
                )
            )
            if len(results) >= k:
                break

        log_retrieval(query, results)
        return results


def _demo() -> None:
    """Quick manual check: python src/retriever.py"""
    retriever = Retriever.from_json()
    for query in ["calm music for studying", "high energy workout", "romantic acoustic evening"]:
        print(f"\nQuery: {query!r}")
        print("-" * 50)
        for result in retriever.search(query, k=3):
            print(f"  {result.score:.3f}  {result.title} by {result.artist}")


if __name__ == "__main__":
    _demo()
