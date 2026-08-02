# 🎵 TuneTracker

**A content-based music recommender with free-text retrieval and grounded, AI-generated explanations.**

TuneTracker takes a listener's taste profile *and* a plain-English query, then does three things: retrieves songs whose descriptions match the query (TF-IDF + cosine similarity), ranks the catalog against the profile using a user-selectable scoring strategy, and generates a one-sentence explanation of why the top pick fits. It matters because it demonstrates, in a small and fully reproducible package, the core moves of a modern recommender: content-based scoring, retrieval-augmented generation (RAG), a swappable ranking policy, and a graceful degradation path when an external AI service isn't available.

---

## Original Project (Modules 1–3)

This project began as the **Music Recommender Simulation**, a content-based recommender built in Modules 1–3. Its original goal was to represent songs and a user "taste profile" as data and score each song with a **single fixed weighting formula** — rewarding a genre match, a mood match, and closeness in energy — then return the top matches with human-readable reasons. It worked on a small local CSV catalog and could rank songs for a handful of hardcoded profiles (e.g. High-Energy Pop, Chill Lofi, Deep Intense Rock).

TuneTracker extends that foundation with three interchangeable ranking strategies, free-text retrieval over song descriptions, AI-generated explanations with a safe fallback, structured logging, a test suite, and a Streamlit UI.

---

## Architecture Overview

The system is a four-stage pipeline; each stage is an independent module under `src/`, and two front ends (a CLI and a Streamlit app) drive it.

```
free-text query ─► Retriever (TF-IDF)      ─► retrieved context
taste profile   ─► Recommender + Strategy  ─► ranked results ─► Explainer ─► grounded sentence
                                                                    ▲
                                          all events (query / retrieval / fallback / error)
                                                        └─► logs/app.log
```

| Stage | Module | Responsibility |
|-------|--------|----------------|
| **Scoring** | `recommender.py` | `Song` / `UserProfile` dataclasses and a `Recommender` that ranks the catalog. Uses the **Strategy pattern**: a `RankingStrategy` interface with three concrete strategies (`GenreFirstStrategy`, `MoodFirstStrategy`, `EnergyFocusedStrategy`). The `Recommender` never knows which is active — it just calls `strategy.score()`. |
| **Retrieval** | `retriever.py` | Indexes each song's text description (`data/song_descriptions.json`) with scikit-learn's `TfidfVectorizer` and returns the top-k matches for a free-text query by cosine similarity. Fully local — no embedding API. |
| **Explanation** | `explainer.py` | Turns a retrieved description + a song's numeric scoring reasons into one grounded sentence. Tries Claude first; falls back to a template that still quotes the retrieved text. |
| **Logging** | `logging_config.py` | Records every query, retrieval, fallback, and error to `logs/app.log`. |

Front ends: `src/main.py` (CLI, runs retrieval and scoring side by side) and `app.py` (Streamlit UI with a mode selector, query box, and results display, pipeline cached via `st.cache_resource`). A diagram is in `diagrams/architecture.mmd`.

---

## Setup Instructions

**1. (Optional) Create and activate a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate      # Mac or Linux
.venv\Scripts\activate         # Windows
```

**2. Install dependencies** (includes `scikit-learn` for retrieval; `anthropic` is optional and only used for the LLM explanation path):

```bash
pip install -r requirements.txt
```

**3. (Optional) Set an API key for LLM explanations.** Without it, the explainer automatically uses a grounded template — no setup required.

```bash
export ANTHROPIC_API_KEY=sk-ant-...      # Mac or Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."    # Windows PowerShell
```

**4. Run it** (from the project root, so `data/` resolves):

```bash
python src/main.py                  # CLI
python -m streamlit run app.py      # Streamlit UI
python -m pytest                    # test suite
```

> **Tip:** use `python -m streamlit ...`, not the bare `streamlit ...`. If you have more than one Python installed, the bare command can launch under a different interpreter that lacks the dependencies (a `ModuleNotFoundError`). Running through `python -m` keeps the app and its packages on one interpreter.

---

## Sample Interactions

### 1. Free-text retrieval (query → retrieved context)

Retrieval is text-based and independent of the taste profile. The same catalog answers two different queries sensibly:

```
QUERY: "calm lo-fi beats for studying"
   0.219  Midnight Coding - LoRoom
   0.191  Library Rain - Paper Lanterns
   0.146  Focus Flow - LoRoom

QUERY: "high energy workout"
   0.211  Gym Hero - Max Pulse
   0.137  Beat Street - Rhythm Cartel
   0.129  Sunrise City - Neon Echo
```

### 2. Mode comparison (same profile, three strategies)

Switching the ranking mode reorders the results for the **same** High-Energy Pop profile (`genre=pop, mood=happy, energy=0.8`). The top pick holds, but the runners-up shift:

```
--- Genre-First (genre weighted 2.0) ---
1. Sunrise City    (pop/happy)        score 3.98
2. I Just Might    (pop/playful)      score 2.99   <- another pure genre match
3. Stateside       (pop/bright)       score 2.94

--- Mood-First (mood weighted 2.0) ---
1. Sunrise City    (pop/happy)        score 3.98
2. Rooftop Lights  (indie pop/happy)  score 2.96   <- a mood match jumps in
3. I Just Might    (pop/playful)      score 1.99

--- Energy-Focused (energy weighted 2.5) ---
1. Sunrise City    (pop/happy)        score 3.45
2. I Just Might    (pop/playful)      score 2.98
3. Rooftop Lights  (indie pop/happy)  score 2.90
```

### 3. Grounded explanation (template fallback, no API key)

For a `lofi / chill / energy 0.4 / prefers acoustic` profile under Energy-Focused, the top pick is *Midnight Coding*, and the explainer produces:

```
'Midnight Coding' fits because it matches your taste on genre match, mood match,
energy similarity and acoustic preference bonus, and it's described as "A mellow
lo-fi beat with warm, dusty textures and a relaxed late-night pulse."
```

This is the fallback path (no API key set) — note it still quotes the retrieved description, so the explanation stays grounded in real text rather than invented detail.

---

## Design Decisions

- **Strategy pattern for ranking.** The original project had one hardcoded formula. I refactored scoring behind a `RankingStrategy` interface so the weighting is chosen at runtime and the `Recommender` stays unaware of which strategy is active. *Trade-off:* more classes for what is currently just three different weight vectors — but it makes adding a new ranking policy (or swapping in an ML scorer later) a drop-in change instead of an edit to core logic.
- **TF-IDF retrieval instead of embeddings.** I deliberately chose scikit-learn TF-IDF over a hosted embedding API. *Trade-off:* retrieval is lexical, not semantic (it matches on shared words, not meaning), so "study music" won't match a description that only says "focus." In exchange, the whole system is dependency-light, deterministic, and reproducible on any clone with **no API key and no network** — which matters more for a portfolio project someone else will run.
- **LLM explanation with a mandatory fallback.** The explainer tries Claude for a natural sentence but falls back to a template on *any* failure (no key, auth error, network, empty response) — and the template still quotes the retrieved text. *Trade-off:* the template is less fluent than the LLM, but the app never breaks and never depends on a paid service to function.
- **Separation of retrieval and scoring.** Retrieval (text) and scoring (attributes) run independently and are displayed side by side rather than fused. This keeps each mechanism debuggable and makes it obvious in the UI that they answer different questions.
- **Centralized logging.** One `logging_config` module logs every query, retrieval, fallback, and error, so behavior is auditable after the fact instead of scattered across `print`s.

---

## Testing Summary

Full captured command outputs — a real `pytest` run, a CLI session, retrieval/explanation
examples, and a log snippet — are in [docs/reproducible_outputs.md](docs/reproducible_outputs.md)
(reproducible, not screenshots).

The suite (`python -m pytest`) has **33 tests across three files**, all green:

- **`test_recommender.py`** — verifies exact per-strategy scores against known weight vectors, the energy term's distance scaling (and its floor at 0), the acoustic bonus, and **rank determinism** (repeated calls return the same order; ties break alphabetically by title).
- **`test_retriever.py`** — checks retrieval relevance on a small deterministic corpus (a workout query ranks the workout song first), that zero-similarity queries return `[]`, and **empty-query handling** (`""`, whitespace, and `k=0` all return `[]`).
- **`test_explainer.py`** — confirms the fallback runs and quotes the description when there's no key, and that an LLM failure (monkeypatched) degrades gracefully instead of crashing. These tests never hit the network.

**What worked:** the deterministic, local design made everything testable without mocking a service — TF-IDF and the scoring math are pure functions of their inputs.

**What didn't (at first):** running the tests surfaced a real **environment bug** — the modules use flat imports, so `pytest` couldn't find them until I added a `conftest.py` that puts `src/` on the path. Separately, the Streamlit app threw `ModuleNotFoundError: sklearn` because the `streamlit` launcher was tied to a *different* Python interpreter than the one with the dependencies installed.

**What I learned:** most of the friction was environment and integration, not algorithm design. Deterministic components are dramatically easier to test than anything that depends on a network call, and designing the fallback path up front meant the "no API key" case was a tested feature rather than an afterthought.

---

## Reflection

Building TuneTracker made the gap between a *scoring function* and a *system* concrete: the interesting engineering was in the seams — swappable strategies, a retrieval layer that stays reproducible, and a fallback that keeps the product working when an AI service is unavailable. It also reframed "AI" for me as one component among many, valuable precisely when it's wrapped in guardrails (logging, tests, a deterministic default) rather than trusted blindly.

> The full **responsible-AI reflection** — how I collaborated with AI, one helpful and one flawed AI suggestion, and the system's limitations and biases — lives in the model card: [**model_card.md**](model_card.md).
