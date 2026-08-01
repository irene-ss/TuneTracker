# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern. My `Scorer`/`score_song` logic had one fixed weighting formula
(genre +1.5, mood +1.4, energy ×1.5, acoustic +0.5). I wanted 2–3 interchangeable
ranking strategies — Genre-First, Mood-First, Energy-Focused — that a user can pick
at runtime, without `Recommender` knowing which one is active.

**How did AI help you brainstorm or implement it?**

I asked Claude for a clean way to swap ranking formulas at runtime. It suggested the
Strategy pattern with:

- A `RankingStrategy` abstract base class exposing a single method,
  `score(user, song) -> (score, reasons)` — the only contract `Recommender` depends on.
- The three strategies implemented as one `WeightedStrategy` class parameterized by a
  weight vector (since all that differs between them is the weights), with
  `GenreFirst` / `MoodFirst` / `EnergyFocused` subclasses giving them names.
- Dependency injection: the strategy is passed into `Recommender.__init__`, with a
  default that reproduces the original formula so nothing breaks.
- A `STRATEGIES` registry (name string → class) as the *only* place that knows the
  concrete strategy classes, so runtime selection stays isolated from `Recommender`.

The key insight AI pointed out: because `Recommender` only calls `.score()`, I could
later swap in a totally different scorer (even an ML model) without changing
`Recommender` at all.

**How does the pattern appear in your final code?**

_Planned (before Phase 2):_ in [src/recommender.py](src/recommender.py) —
`RankingStrategy` (ABC), `WeightedStrategy` + the three concrete strategies, a
`STRATEGIES` registry, and a `Recommender` that holds a `strategy` and only calls
`self.strategy.score(user, song)` inside `recommend()` / `explain_recommendation()`.

_Confirmed after Phase 2:_ implemented in [src/recommender.py](src/recommender.py):
`RankingStrategy` (ABC with abstract `score()`), a shared `WeightedStrategy` base, and
the three concrete strategies `GenreFirstStrategy` (genre 2.0), `MoodFirstStrategy`
(mood 2.0), and `EnergyFocusedStrategy` (energy 2.5, genre/mood 0.5). `Recommender`
holds a `strategy` and only calls `self.strategy.score(user, song)` — it never
branches on which strategy is active. A `STRATEGIES` registry maps runtime name
strings to classes; `BalancedStrategy` is the default and preserves the original
weighting so existing tests still pass (verified: `2 passed`).
