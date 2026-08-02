"""
Grounded, one-sentence explanations for a recommendation.

Given a song's retrieved description (from retriever.py) and its numeric scoring
reasons (from recommender.py), produce ONE grounded sentence explaining why the
song fits the user.

Two paths:
1. LLM path — calls Claude (Anthropic) to phrase a natural sentence grounded in
   the description and the scoring reasons.
2. Template fallback — if the anthropic SDK isn't installed, no API key is set,
   or the API call fails for any reason, build the sentence from a template that
   still quotes the retrieved description. The app never breaks on a missing key.

The fallback keeps the project reproducible for anyone cloning the repo: it runs
with zero configuration, and the LLM path is a drop-in upgrade when a key exists.
"""

from __future__ import annotations

import os
from typing import List, Optional

from logging_config import log_fallback, log_error

# Default model per project convention; override via ExplainerConfig or env.
DEFAULT_MODEL = "claude-opus-5"


class ExplainerConfig:
    """Configuration for the explainer's LLM path."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        max_tokens: int = 1024,
    ):
        self.model = model
        # Fall back to the standard env var if no key is passed explicitly.
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = max_tokens


def _first_sentence(text: str) -> str:
    """Return the first sentence of a description, trimmed of trailing space."""
    text = (text or "").strip()
    if not text:
        return ""
    for end in (". ", "! ", "? "):
        idx = text.find(end)
        if idx != -1:
            return text[: idx + 1].strip()
    return text


def build_template_explanation(
    description: str,
    reasons: List[str],
    title: Optional[str] = None,
) -> str:
    """
    Build a grounded explanation without an LLM.

    Always quotes the retrieved description so the output stays grounded in real
    text rather than inventing detail. This is the reproducible default path.
    """
    name = f"'{title}'" if title else "This track"
    # Strip trailing sentence punctuation so the quote embeds cleanly (avoids '..').
    quoted = _first_sentence(description).rstrip(".!?").strip()

    reason_clause = ""
    if reasons:
        # Turn ["Genre match +2.00", "Energy similarity +0.98"] into readable prose.
        cleaned = [r.split(" +")[0].strip().lower() for r in reasons if r.strip()]
        cleaned = [c for c in cleaned if c]
        if len(cleaned) == 1:
            reason_clause = f"it matches your taste on {cleaned[0]}"
        elif cleaned:
            reason_clause = (
                f"it matches your taste on {', '.join(cleaned[:-1])} and {cleaned[-1]}"
            )

    if quoted and reason_clause:
        return f"{name} fits because {reason_clause}, and it's described as \"{quoted}.\""
    if quoted:
        return f"{name} fits your taste; it's described as \"{quoted}.\""
    if reason_clause:
        return f"{name} fits because {reason_clause}."
    return f"{name} is a reasonable match for your preferences."


def _llm_explanation(
    description: str,
    reasons: List[str],
    title: Optional[str],
    config: ExplainerConfig,
) -> str:
    """
    Ask Claude for one grounded sentence. Raises on any failure so the caller
    can fall back — never returns a partial or unvalidated result.
    """
    import anthropic  # local import so the SDK is an optional dependency

    client = anthropic.Anthropic(api_key=config.api_key)

    song_label = title or "the song"
    reason_lines = "\n".join(f"- {r}" for r in reasons) if reasons else "- (none)"
    prompt = (
        f"You are explaining a music recommendation in ONE sentence.\n\n"
        f"Song: {song_label}\n"
        f"Retrieved description: \"{description.strip()}\"\n"
        f"Numeric scoring reasons (why our recommender ranked it):\n{reason_lines}\n\n"
        f"Write exactly one natural, grounded sentence telling the user why this song "
        f"fits them. Ground it in the description and the scoring reasons above — do not "
        f"invent facts not present in them. Respond with only the sentence, no preamble."
    )

    message = client.messages.create(
        model=config.model,
        max_tokens=config.max_tokens,
        # Disable thinking + low effort: this is a trivial one-sentence task, so we
        # avoid spending (and truncating against) the token budget on reasoning.
        thinking={"type": "disabled"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = " ".join(
        block.text for block in message.content if getattr(block, "type", None) == "text"
    ).strip()
    if not text:
        raise ValueError("Empty response from Claude")
    return text


def generate_explanation(
    description: str,
    reasons: List[str],
    title: Optional[str] = None,
    config: Optional[ExplainerConfig] = None,
) -> str:
    """
    Generate one grounded sentence explaining a recommendation.

    Tries the Claude LLM path first; on ANY failure (no SDK, no API key, network
    error, empty response) falls back to a template that still quotes the
    retrieved description. Always returns a usable sentence.
    """
    config = config or ExplainerConfig()

    # No key → skip the LLM path entirely and use the template.
    if not config.api_key:
        log_fallback("explainer", "no ANTHROPIC_API_KEY; using template")
        return build_template_explanation(description, reasons, title)

    try:
        return _llm_explanation(description, reasons, title, config)
    except Exception as exc:
        # Missing SDK, auth error, rate limit, network failure, bad response —
        # all degrade gracefully to the grounded template. Log both the error and
        # the fact that we fell back.
        log_error("explainer", exc)
        log_fallback("explainer", f"LLM call failed ({type(exc).__name__}); using template")
        return build_template_explanation(description, reasons, title)


def _demo() -> None:
    """Quick manual check: python src/explainer.py"""
    description = (
        "A soft, highly acoustic lo-fi piece with a slow tempo and gentle, "
        "rainy-day calm. Best suited for deep focus, quiet reading, or relaxation."
    )
    reasons = ["Genre match +2.00", "Mood match +1.00", "Energy similarity +0.95"]
    print(generate_explanation(description, reasons, title="Library Rain"))


if __name__ == "__main__":
    _demo()
