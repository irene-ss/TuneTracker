# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

---

Real‑world recommendation engines combine collaborative filtering (learning from other users’ behavior) and content‑based filtering (analyzing song attributes like mood, tempo, or energy). Platforms track signals such as likes, skips, replays, playlist additions, and listening duration to understand evolving taste. In this simplified version, we focus entirely on content‑based filtering: each song is scored based on how well its mood, genre, and energy match the user’s preferences, with mood carrying the strongest influence. This makes the system easy to understand while still reflecting how emotional tone often drives real listening choices.
formula used: 1.6⋅1[genre matches]+ 1.4⋅1[mood matches]+ 1.5⋅(1−∣energy of song − energy of user∣)This formula balances genre and mood as the primary signals while still rewarding energy similarity.
## Architecture

TuneTracker is a content-based recommender with a retrieval + explanation layer on
top. The pipeline has four stages, each in its own module under `src/`:

1. **Scoring — `recommender.py`.** `Song` and `UserProfile` dataclasses plus a
   `Recommender` that ranks songs against a profile. Scoring uses the **Strategy
   pattern**: a `RankingStrategy` interface with three interchangeable strategies —
   `GenreFirstStrategy`, `MoodFirstStrategy`, and `EnergyFocusedStrategy` — each a
   different weighting of genre / mood / energy. The `Recommender` never knows which
   strategy is active; it just calls `strategy.score()`.
2. **Retrieval — `retriever.py`.** A `Retriever` that indexes each song's text
   description (`data/song_descriptions.json`) with scikit-learn's `TfidfVectorizer`
   and returns the top-k matches for a free-text query by cosine similarity.
   Dependency-light and fully local (no embedding API), so it's reproducible on any
   clone.
3. **Explanation — `explainer.py`.** `generate_explanation()` turns a retrieved
   description plus a song's numeric scoring reasons into one grounded sentence. It
   tries an LLM (Claude) first and falls back to a template that still quotes the
   retrieved text when there's no API key or the call fails.
4. **Logging — `logging_config.py`.** Every query, retrieval, fallback, and error is
   written to `logs/app.log`.

Two front ends consume the pipeline:

- **`src/main.py`** — a CLI that runs retrieval and scoring side by side.
- **`app.py`** — a Streamlit UI with a mode selector, a query box, and a display of
  retrieved context + ranked results + explanation (pipeline cached with
  `st.cache_resource`).

Tests live in `tests/` (`test_recommender.py`, `test_retriever.py`,
`test_explainer.py`). See `diagrams/architecture.mmd` for a diagram.

```
free-text query ─► Retriever (TF-IDF)      ─► retrieved context
taste profile   ─► Recommender + Strategy  ─► ranked results ─► Explainer ─► grounded sentence
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies (includes `scikit-learn` for retrieval; `anthropic` is
   optional and only used for the LLM explanation path):

   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Set an API key for LLM explanations.** Without it, the explainer
   automatically uses a grounded template — no setup required.

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...      # Mac or Linux
   $env:ANTHROPIC_API_KEY = "sk-ant-..."    # Windows PowerShell
   ```

### Running the app

Run the CLI (from the project root, so `data/` resolves):

```bash
python src/main.py
```

Run the Streamlit UI:

```bash
python -m streamlit run app.py
```

> **Tip:** use `python -m streamlit ...` (not just `streamlit ...`). If you have more
> than one Python installed, the bare `streamlit` command may launch under a different
> interpreter that doesn't have the dependencies, giving a `ModuleNotFoundError`.
> Running through `python -m` guarantees the app and its packages share one interpreter.

### Running Tests

```bash
python -m pytest
```

Tests cover per-strategy scoring and rank determinism (`test_recommender.py`),
retrieval relevance and empty-query handling (`test_retriever.py`), and the
explainer's fallback behavior (`test_explainer.py`).

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
Loaded songs: 18
                   
Top recommendations
============================================================
1. Sunrise City by Neon Echo
   Score   : 4.37
   Reasons : Genre match +1.5; Mood match +1.4; Energy similarity +1.47
------------------------------------------------------------
2. I Just Might by Bruno Mars
   Score   : 2.98
   Reasons : Genre match +1.5; Energy similarity +1.48
------------------------------------------------------------
3. Stateside by Zara Larson
   Score   : 2.91
   Reasons : Genre match +1.5; Energy similarity +1.41
------------------------------------------------------------
4. Rooftop Lights by Indigo Parade
   Score   : 2.84
   Reasons : Mood match +1.4; Energy similarity +1.44
------------------------------------------------------------
5. Gym Hero by Max Pulse
   Score   : 2.80
   Reasons : Genre match +1.5; Energy similarity +1.30
------------------------------------------------------------
```

-----------------------------------
OUTPUT OF DIVERSE PROFILE 
Loaded songs: 20

=== High-Energy Pop ===
Top recommendations
============================================================
1. Sunrise City by Neon Echo
   Score   : 4.37
   Reasons : Genre match +1.5; Mood match +1.4; Energy similarity +1.47
------------------------------------------------------------
2. I Just Might by Bruno Mars
   Score   : 2.98
   Reasons : Genre match +1.5; Energy similarity +1.48
------------------------------------------------------------
3. Stateside by Zara Larson
   Score   : 2.91
   Reasons : Genre match +1.5; Energy similarity +1.41
------------------------------------------------------------
4. Rooftop Lights by Indigo Parade
   Score   : 2.84
   Reasons : Mood match +1.4; Energy similarity +1.44
------------------------------------------------------------
5. Petal by Ariana Grande
   Score   : 2.82
   Reasons : Genre match +1.5; Energy similarity +1.32
------------------------------------------------------------

=== Chill Lofi ===
Top recommendations
============================================================
1. Midnight Coding by LoRoom
   Score   : 4.37
   Reasons : Genre match +1.5; Mood match +1.4; Energy similarity +1.47
------------------------------------------------------------
2. Library Rain by Paper Lanterns
   Score   : 4.32
   Reasons : Genre match +1.5; Mood match +1.4; Energy similarity +1.42
------------------------------------------------------------
3. Focus Flow by LoRoom
   Score   : 3.00
   Reasons : Genre match +1.5; Energy similarity +1.50
------------------------------------------------------------
4. Spacewalk Thoughts by Orbit Bloom
   Score   : 2.72
   Reasons : Mood match +1.4; Energy similarity +1.32
------------------------------------------------------------
5. Coffee Shop Stories by Slow Stereo
   Score   : 1.46
   Reasons : Energy similarity +1.46
------------------------------------------------------------

=== Deep Intense Rock ===
Top recommendations
============================================================
1. Storm Runner by Voltline
   Score   : 4.38
   Reasons : Genre match +1.5; Mood match +1.4; Energy similarity +1.48
------------------------------------------------------------
2. Gym Hero by Max Pulse
   Score   : 2.85
   Reasons : Mood match +1.4; Energy similarity +1.46
------------------------------------------------------------
3. Shadow Throne by Iron Veil
   Score   : 1.48
   Reasons : Energy similarity +1.48
------------------------------------------------------------
4. Beat Street by Rhythm Cartel
   Score   : 1.47
   Reasons : Energy similarity +1.47
------------------------------------------------------------
5. Stateside by Zara Larson
   Score   : 1.44
   Reasons : Energy similarity +1.44
----------------------------------------------------------

### Mode comparison — same profile, three strategies

The Strategy pattern lets a user switch ranking modes at runtime. Running the
**same** "High-Energy Pop" profile (`genre=pop, mood=happy, energy=0.8`) through all
three strategies reorders the results — watch how #2 and #3 change while the
top pick stays fixed:

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

`Sunrise City` tops every mode because it matches on all three signals, but the
runners-up shift: Genre-First rewards the other pop tracks, Mood-First pulls in a
`happy` indie-pop song over a same-genre one, and Energy-Focused ranks almost purely
on how close each song's energy is to the target.

---

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



