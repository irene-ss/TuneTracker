# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  

TuneTracker 1.0 

---

## 2. Intended Use  

TuneTracker 1.0 is a simple music recommender designed for classroom exploration. It suggests songs based on a user’s preferred genre, mood, and energy level. It assumes that a listener wants songs that feel similar to a given taste profile, such as happy pop or intense rock.

---

## 3. How the Model Works  

The recommender looks at a few simple song features, including genre, mood, and energy level. It compares each song to the user’s preferred style and gives points when the song matches the requested genre or mood and when its energy is close to the target. Songs that fit better overall rise higher in the recommendation list.


---

## 4. Retrieval-Augmented Explanations (RAG)

Beyond attribute scoring, TuneTracker adds a lightweight retrieval-augmented layer so it can surface songs from a free-text query and explain *why* a song fits in natural language.

- **Retrieval.** Each song has a short text description covering its vibe, use-case, and similar artists. A `TfidfVectorizer` indexes these descriptions, and a free-text query (for example, "calm music for studying") is matched against them by cosine similarity to surface the most relevant songs. This runs entirely locally with no embedding API, so it behaves the same on any machine.
- **Augmented explanation.** For a recommended song, the system combines its retrieved description with the numeric scoring reasons and generates one grounded sentence. It uses a language model when an API key is available and otherwise falls back to a template that still quotes the retrieved description, so the explanation is always grounded in real text rather than invented detail.

This mirrors how larger retrieval-augmented systems work: retrieve relevant context first, then condition the generated text on that context instead of relying on the model's memory alone.

---

## 5. Data  

The model uses a small catalog of 20 songs. The dataset includes a mix of genres such as pop, lofi, rock, jazz, ambient, indie pop, hip-hop, metal, and country, along with a variety of moods like happy, chill, intense, relaxed, and dreamy. No new data was added or removed for this version.

One limitation of the dataset is that it does not cover every style of music or every kind of listener preference, so it is best suited for simple, classroom-style examples rather than full real-world recommendations.

---

## 6. Strengths  

This system works well for users whose taste is fairly clear and easy to describe. It gives sensible results for profiles such as high-energy pop, calm lofi, and intense rock because those preferences are closely tied to the features the model uses.

The scoring also does a good job of matching obvious patterns, such as preferring high-energy songs for energetic profiles and lower-energy songs for calm profiles. In many cases, the recommended songs feel intuitive and easy to explain.

---

## 7. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---
Limitations:
- It rewards exact genre and mood matches very strongly, so a user with broader tastes can get stuck seeing only very similar songs.
- The energy scoring is quite rigid. It uses an absolute energy gap and then gives no credit once the gap is large. That means a song can be unfairly ignored even if it is still a good fit for other reasons.

Retrieval and strategy-choice limitations:
- Retrieval is **lexical, not semantic**. TF-IDF matches on shared words, so a query like "study music" can miss a description that says "focus" or "concentration" unless those exact words appear. It has no understanding of synonyms or meaning.
- Retrieval quality is only as good as the **descriptions**. The song descriptions are short and hand-written for this project, so a sparse, biased, or inaccurate description directly limits what a query can find and can quietly favor songs whose descriptions happen to use more common words.
- **Strategy choice changes the answer, and there is no single "correct" strategy.** The same profile produces different rankings under Genre-First, Mood-First, and Energy-Focused. The system does not know which one a user actually wants, so the responsibility for picking the right lens falls on the user, and a poor choice can bury good matches.
- Because the explanation is grounded in the retrieved description and the scoring reasons, a weak retrieval or a mismatched strategy still yields a fluent, confident-sounding sentence — which can make a questionable recommendation *look* well justified.

## 8. Evaluation  

I tested three example profiles: High-Energy Pop, Chill Lofi, and Deep Intense Rock. I looked at whether the recommendations changed in a way that matched each profile’s mood and energy.

- High-Energy Pop vs. Chill Lofi: The pop profile preferred upbeat, brighter songs with higher energy, while the lofi profile shifted toward softer, lower-energy songs with a calmer mood. This makes sense because the two profiles are asking for very different emotional experiences.
- High-Energy Pop vs. Deep Intense Rock: The pop profile favored songs that felt lively and polished, while the rock profile leaned toward songs with a stronger, more intense feel. This makes sense because the rock profile wants more force and urgency, not just a high-energy sound.
- Chill Lofi vs. Deep Intense Rock: The lofi profile chose quieter, more relaxed songs, while the rock profile picked songs that felt louder and more aggressive. This makes sense because one profile is about calm focus and the other is about intensity and drive.

### Testing Results

Beyond the qualitative profile comparison above, I measured reliability with an automated test suite (`python -m pytest`). Summary of results:

- **33 out of 33 automated tests passed** across three files — scoring correctness and rank determinism (`test_recommender.py`), retrieval relevance and empty-query handling (`test_retriever.py`), and the explainer's fallback behavior (`test_explainer.py`).
- **Retrieval** returned relevant hits on in-vocabulary queries (cosine similarity roughly 0.15–0.22, e.g. a "calm lo-fi beats for studying" query surfaced *Midnight Coding*, *Library Rain*, and *Focus Flow*) and correctly returned **nothing** for empty, whitespace-only, or out-of-vocabulary queries rather than producing junk.
- **Scoring** was deterministic: repeated runs on the same profile produced the same ranking, with ties broken alphabetically by title.
- **The explainer** degraded safely — it fell back to a grounded template when no API key was set, and it did **not crash** when the LLM call was forced to fail; instead it logged the error and still returned a usable, grounded sentence.

The main thing that did *not* work at first was environment setup rather than the algorithms (tests needed a `conftest.py` for imports, and the app initially failed on a mismatched Python interpreter) — reflected on further in Section 13. Full captured command outputs are in `docs/reproducible_outputs.md`.

---

## 9. Future Work  

I would like to improve the model by expanding the dataset to include many more styles of music, so it can better represent different listening tastes. I also want to add more user profiles to test how the system behaves for a wider range of people. In addition, I would make the algorithm more flexible so it is less likely to suggest repetitive songs and gives users a broader mix of recommendations.

---

## 10. Personal Reflection  

This project helped me understand how recommender systems work in a simple but meaningful way. I found it especially interesting to see how music apps use small signals like genre, mood, and energy to make recommendations that feel personal. I also learned that these systems can be useful, but they can also become too narrow or repetitive if they rely too heavily on a few features.

---

## 11. Working With AI

I used an AI assistant as a collaborator throughout this project — to brainstorm design patterns, refactor my scoring code, scaffold the retrieval and explanation layers, and write tests — while I reviewed, corrected, and made the final decisions. The most helpful suggestion was to restructure my single fixed scoring formula behind the Strategy pattern: an AI proposed a `RankingStrategy` interface with three interchangeable strategies so the ranking mode could be chosen at runtime while the `Recommender` stayed unaware of which one was active, which turned "add a new ranking mode" from a rewrite into a drop-in change. A flawed suggestion came when AI drafted the song descriptions: it confidently invented "similar artists" and other details that sounded plausible but were not always accurate, which I had to review and correct — a clear reminder that AI output can be fluent and wrong at the same time, and that a human has to verify anything it generates. Combined with the limitations described above (lexical-only retrieval, no single "correct" strategy, and explanations that sound convincing even when the underlying match is weak), this reinforced that AI is most trustworthy when it is wrapped in guardrails and human review rather than taken at face value.

---

## 12. Could This Be Misused, and How Would I Prevent That?

Even a small recommender carries misuse risks. The clearest one is that recommendation systems are often tuned to maximize engagement rather than genuine usefulness — a version of this that optimized for time-on-app instead of taste fit could deliberately narrow a listener into a repetitive "filter bubble." A second risk is that the AI-generated explanation is fluent and confident, so a user could mistake it for an objective judgment about a song rather than a justification built from a short description and a few numeric scores. A third is dataset misuse: because the descriptions are hand-written, someone could bias results simply by wording certain songs' descriptions to match more queries.

Several choices in this project reduce those risks. The system is **content-based only** — it uses song attributes and text descriptions, with **no behavioral tracking, likes, skips, or engagement signals**, so it cannot optimize against the user. The explanation layer always **discloses its grounding** (it quotes the retrieved description and lists the scoring reasons) and, in the model card and README, is explicitly framed as a justification, not a verdict. **Logging** records every query, retrieval, and fallback to `logs/app.log`, so recommendations are auditable after the fact rather than opaque. And the **ranking strategy is chosen by the user**, not hidden, so the weighting behind a result is transparent and changeable. To go further, I would add a diversity/novelty term to actively counter narrowing, and validation on description length and content to limit the "worded to win" failure mode.

---

## 13. What Surprised Me While Testing Reliability

The biggest surprise was that most of the failures I hit were **environment and integration problems, not algorithm bugs**. The scoring math and TF-IDF retrieval were pure functions of their inputs and passed cleanly, but my tests wouldn't run until I added a `conftest.py` to fix the import path, and the Streamlit app crashed with a `ModuleNotFoundError` because the `streamlit` launcher was tied to a *different* Python interpreter than the one where I'd installed the dependencies. Getting the plumbing right took more effort than getting the recommender right.

Two smaller things also stood out. First, designing the fallback up front meant the "no API key" case became a **tested feature** rather than a crash — my explainer tests confirm it degrades to a grounded template even when the LLM call is forced to fail, which made reliability feel like a design property instead of luck. Second, watching the retriever return an off-genre song (a lo-fi track surfacing for an energetic pop query) purely because of a few shared words made the **lexical, non-semantic nature of TF-IDF concrete** — a limitation I had written down in the abstract but only really understood once I saw a confident, wrong-feeling result come out of a passing system.

