"""
Tests for the retriever: retrieval relevance and empty-query handling.
"""

import pytest

from retriever import Retriever, RetrievalResult


def make_retriever() -> Retriever:
    """Small, deterministic corpus with two clearly-distinct documents."""
    songs = [
        {
            "id": "1",
            "title": "Rainy Study",
            "artist": "A",
            "description": "calm quiet rainy lofi beats for studying reading and deep focus",
        },
        {
            "id": "2",
            "title": "Gym Sprint",
            "artist": "B",
            "description": "loud fast high energy workout music for the gym and running",
        },
    ]
    return Retriever(songs)


# --- Retrieval relevance ----------------------------------------------------

def test_workout_query_ranks_gym_song_first():
    results = make_retriever().search("high energy gym workout", k=2)
    assert results[0].title == "Gym Sprint"


def test_study_query_ranks_study_song_first():
    results = make_retriever().search("calm music for studying and focus", k=2)
    assert results[0].title == "Rainy Study"


def test_results_sorted_by_descending_score():
    results = make_retriever().search("energy workout gym focus", k=2)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)


def test_result_is_retrievalresult_with_expected_fields():
    results = make_retriever().search("gym workout", k=1)
    assert len(results) == 1
    r = results[0]
    assert isinstance(r, RetrievalResult)
    assert r.song_id and r.title and isinstance(r.score, float)


def test_zero_similarity_results_are_omitted():
    """A query sharing no vocabulary with any doc returns nothing (not junk)."""
    results = make_retriever().search("xylophone zebra quantum")
    assert results == []


def test_k_limits_result_count():
    r = make_retriever()
    assert len(r.search("music", k=1)) <= 1


# --- Empty-query handling ---------------------------------------------------

def test_empty_query_returns_empty_list():
    assert make_retriever().search("") == []


def test_whitespace_query_returns_empty_list():
    assert make_retriever().search("   ") == []


def test_k_zero_returns_empty_list():
    assert make_retriever().search("gym workout", k=0) == []


def test_empty_corpus_raises():
    with pytest.raises(ValueError):
        Retriever([])


# --- Real data smoke test ---------------------------------------------------

def test_from_json_loads_and_retrieves():
    """The shipped song_descriptions.json indexes and returns relevant hits."""
    retriever = Retriever.from_json()  # default path -> data/song_descriptions.json
    assert len(retriever.songs) > 0
    results = retriever.search("high energy workout", k=3)
    assert results, "expected at least one hit for a workout query"
    assert any(r.title == "Gym Hero" for r in results)
