# Reproducible Execution Evidence

This file contains **real, captured output** from running TuneTracker — not screenshots.
Every block is preceded by the exact command, so anyone can re-run it from the project
root and reproduce the same results. Numbers are deterministic (local TF-IDF + fixed
scoring weights), so repeated runs match.

Environment: Python 3.14, run from the project root.

---

## 1. Test suite — 33/33 passing

```console
$ python -m pytest -q
.................................                                        [100%]
33 passed in 3.13s
```

Breakdown (from `python -m pytest -v`):

| Test file | Tests | Covers |
|---|---:|---|
| `tests/test_recommender.py` | 14 | per-strategy scoring correctness, energy-distance scaling, acoustic bonus, rank determinism, tie-break by title |
| `tests/test_retriever.py` | 11 | retrieval relevance, descending scores, zero-similarity omission, empty-query / whitespace / `k=0` handling, empty-corpus error |
| `tests/test_explainer.py` | 8 | no-key template fallback, graceful handling on LLM failure, success path |

---

## 2. CLI run — retrieval + scoring side by side

```console
$ printf "genre-first\ncalm lo-fi beats for studying\n" | python src/main.py
Loaded songs: 22
Pick a mode [genre-first, mood-first, energy-focused, balanced] or Enter for all: Free-text query (Enter to use each profile's default):
=== High-Energy Pop ===
============================================================
  Retrieval for query: 'calm lo-fi beats for studying'
  ----------------------------------------------------------
  1. Midnight Coding by LoRoom  (similarity 0.219)
  2. Library Rain by Paper Lanterns  (similarity 0.191)
  3. Focus Flow by LoRoom  (similarity 0.146)

  Scoring mode: genre-first
  ----------------------------------------------------------
  1. Sunrise City by Neon Echo  (score 3.98)
     Reasons: Genre match +2.00; Mood match +1.00; Energy similarity +0.98
  2. I Just Might by Bruno Mars  (score 2.99)
     Reasons: Genre match +2.00; Energy similarity +0.99
  3. Stateside by Zara Larson  (score 2.94)
     Reasons: Genre match +2.00; Energy similarity +0.94
  4. How You Like That by BLACKPINK  (score 2.90)
     Reasons: Genre match +2.00; Energy similarity +0.90
  5. Petal by Ariana Grande  (score 2.88)
     Reasons: Genre match +2.00; Energy similarity +0.88
```

Note how **retrieval** (text-based, driven by the query) and **scoring** (attribute-based,
driven by the profile) produce different top results — retrieval surfaces lo-fi/study
tracks, while genre-first scoring ranks the pop catalog. They are independent by design.

---

## 3. Mode comparison — same profile, three strategies

The Strategy pattern lets the ranking mode change at runtime. The **same** High-Energy Pop
profile (`genre=pop, mood=happy, energy=0.8`) reorders under each strategy — the top pick
holds, the runners-up shift.

```console
$ python -c "..."   # runs each strategy over the same profile (see command in repo history)
--- genre-first ---
1. Sunrise City (pop/happy)      score 3.98
2. I Just Might (pop/playful)    score 2.99
3. Stateside (pop/bright)        score 2.94
--- mood-first ---
1. Sunrise City (pop/happy)        score 3.98
2. Rooftop Lights (indie pop/happy) score 2.96   <- mood match jumps in
3. I Just Might (pop/playful)      score 1.99
--- energy-focused ---
1. Sunrise City (pop/happy)        score 3.45
2. I Just Might (pop/playful)      score 2.98
3. Rooftop Lights (indie pop/happy) score 2.90
```

---

## 4. Retrieval relevance — two queries, same catalog

```console
QUERY: "calm lo-fi beats for studying"
   0.219  Midnight Coding - LoRoom
   0.191  Library Rain - Paper Lanterns
   0.146  Focus Flow - LoRoom

QUERY: "high energy workout"
   0.211  Gym Hero - Max Pulse
   0.137  Beat Street - Rhythm Cartel
   0.129  Sunrise City - Neon Echo
```

Out-of-vocabulary and empty queries return nothing (verified by `tests/test_retriever.py`):

```console
search("xylophone zebra quantum")  -> []      # no shared vocabulary
search("")                          -> []      # empty query
search("   ")                       -> []      # whitespace only
search("gym workout", k=0)          -> []      # k = 0
```

---

## 5. Grounded explanation — fallback path (no API key set)

With no `ANTHROPIC_API_KEY`, the explainer skips the LLM and uses the grounded template,
which still quotes the retrieved description. Profile: `lofi / chill / energy 0.4 / prefers acoustic`,
strategy energy-focused, top pick *Midnight Coding*:

```console
'Midnight Coding' fits because it matches your taste on genre match, mood match,
energy similarity and acoustic preference bonus, and it's described as "A mellow
lo-fi beat with warm, dusty textures and a relaxed late-night pulse."
```

---

## 6. Interaction log — `logs/app.log`

Every query, retrieval, fallback, and error is logged (the live `logs/` directory is
gitignored; this is a captured snapshot). Sample lines from the CLI run above:

```log
2026-08-01 23:49:24 INFO    tunetracker | EVENT=query | text="calm lo-fi beats for studying" | k=3 | mode=genre-first
2026-08-01 23:49:24 INFO    tunetracker | EVENT=retrieval | query="calm lo-fi beats for studying" | hits=3 | results=[Midnight Coding:0.219, Library Rain:0.191, Focus Flow:0.146]
```

And a fallback event, captured when the explainer runs without an API key:

```log
WARNING tunetracker | EVENT=fallback | component=explainer | reason="no ANTHROPIC_API_KEY; using template"
```

---

## How to reproduce everything above

```bash
pip install -r requirements.txt
python -m pytest                                 # section 1
printf "genre-first\ncalm lo-fi beats for studying\n" | python src/main.py   # sections 2 & 4
python -m streamlit run app.py                   # interactive UI
Get-Content logs/app.log                          # section 6 (PowerShell)
```
