"""
TuneTracker — Streamlit UI.

Ties the whole pipeline together:
- a mode selector for the 3 ranking strategies (Genre-First / Mood-First / Energy-Focused),
- a free-text query box for TF-IDF retrieval,
- and a display of retrieved context + ranked results + a grounded explanation.

The pipeline (songs, retriever, descriptions) is built once via st.cache_resource
so it doesn't reload on every Streamlit rerun.

Run from the project root:
    streamlit run app.py
"""

import sys
from pathlib import Path
from typing import Dict, List

# The src/ modules use flat imports (from recommender import ...), matching how
# the app runs. Put src/ on the path so those imports resolve here too.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from recommender import load_songs, Song, UserProfile, Recommender, STRATEGIES
from retriever import Retriever
from explainer import generate_explanation
from logging_config import setup_logging, log_query

DATA_DIR = ROOT / "data"

# Display label -> STRATEGIES key. The 3 interchangeable ranking strategies.
STRATEGY_LABELS = {
    "Genre-First": "genre-first",
    "Mood-First": "mood-first",
    "Energy-Focused": "energy-focused",
}


def to_song(row: Dict) -> Song:
    """Convert a load_songs() dict into a Song dataclass (danceability defaults to 0.0)."""
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


@st.cache_resource(show_spinner="Loading the recommendation pipeline…")
def load_pipeline():
    """
    Build the pipeline once and cache it across reruns.

    Returns (songs, retriever, desc_by_id, genres, moods). st.cache_resource keeps
    a single shared instance so the CSV, TF-IDF index, etc. aren't rebuilt on every
    interaction.
    """
    setup_logging()
    songs = [to_song(row) for row in load_songs(str(DATA_DIR / "songs.csv"))]
    retriever = Retriever.from_json(DATA_DIR / "song_descriptions.json")

    # id (as string) -> description, for building explanations.
    desc_by_id = {s["id"]: s["description"] for s in retriever.songs}

    genres = sorted({s.genre for s in songs})
    moods = sorted({s.mood for s in songs})
    return songs, retriever, desc_by_id, genres, moods


def main() -> None:
    st.set_page_config(page_title="TuneTracker", page_icon="🎵", layout="wide")
    st.title("🎵 TuneTracker")
    st.caption(
        "Free-text retrieval (TF-IDF) + strategy-based scoring, with a grounded explanation."
    )

    songs, retriever, desc_by_id, genres, moods = load_pipeline()

    # --- Sidebar: mode selector + profile -----------------------------------
    with st.sidebar:
        st.header("Controls")
        strategy_label = st.selectbox("Ranking mode", list(STRATEGY_LABELS.keys()))
        strategy_key = STRATEGY_LABELS[strategy_label]

        st.divider()
        st.subheader("Your taste profile")
        favorite_genre = st.selectbox("Favorite genre", genres,
                                      index=genres.index("pop") if "pop" in genres else 0)
        favorite_mood = st.selectbox("Favorite mood", moods,
                                     index=moods.index("happy") if "happy" in moods else 0)
        target_energy = st.slider("Target energy", 0.0, 1.0, 0.7, 0.05)
        likes_acoustic = st.checkbox("Prefer acoustic tracks", value=False)

        st.divider()
        top_k = st.slider("How many results", 1, 10, 5)

    user = UserProfile(
        favorite_genre=favorite_genre,
        favorite_mood=favorite_mood,
        target_energy=target_energy,
        likes_acoustic=likes_acoustic,
    )

    # --- Main: free-text query ----------------------------------------------
    query = st.text_input(
        "Free-text query",
        placeholder="e.g. calm lo-fi beats for studying",
    )

    rec = Recommender(songs, STRATEGIES[strategy_key]())

    col_retrieval, col_ranked = st.columns(2)

    # --- Retrieved context (text-based, independent of scoring) -------------
    with col_retrieval:
        st.subheader("🔎 Retrieved context")
        st.caption("TF-IDF + cosine similarity on the free-text query.")
        if query.strip():
            log_query(query, k=top_k, mode=strategy_key)
            hits = retriever.search(query, k=top_k)
            if hits:
                for h in hits:
                    st.markdown(f"**{h.title}** — {h.artist}  \n`similarity {h.score:.3f}`")
                    st.caption(h.description)
            else:
                st.info("No text matches for that query.")
        else:
            st.info("Enter a query above to see retrieved context.")

    # --- Ranked results (attribute-based scoring) ---------------------------
    with col_ranked:
        st.subheader(f"📊 Ranked results — {strategy_label}")
        st.caption("Scored against your taste profile by the selected strategy.")
        ranked = rec.recommend(user, k=top_k)
        for i, song in enumerate(ranked, start=1):
            score, reasons = rec.strategy.score(user, song)
            st.markdown(f"**{i}. {song.title}** — {song.artist}  \n`score {score:.2f}`")
            st.caption("; ".join(reasons))

    # --- Explanation for the top ranked song --------------------------------
    st.divider()
    st.subheader("💡 Why the top pick fits")
    if ranked:
        top = ranked[0]
        _, top_reasons = rec.strategy.score(user, top)
        description = desc_by_id.get(str(top.id), "")
        explanation = generate_explanation(
            description=description,
            reasons=top_reasons,
            title=top.title,
        )
        st.success(explanation)
        st.caption(
            "Uses Claude if ANTHROPIC_API_KEY is set; otherwise a grounded template "
            "that quotes the retrieved description."
        )
    else:
        st.info("No ranked results to explain.")


if __name__ == "__main__":
    main()
