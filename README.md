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
## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

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



