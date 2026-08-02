"""
Tests for the explainer: template fallback with no key, and graceful handling
when the LLM call fails. These tests never hit the network.
"""

import pytest

import explainer
from explainer import (
    generate_explanation,
    build_template_explanation,
    ExplainerConfig,
)

DESCRIPTION = "A soft, highly acoustic lo-fi piece with a slow tempo and rainy-day calm."
REASONS = ["Genre match +2.00", "Mood match +1.00", "Energy similarity +0.95"]


# --- Template fallback (no key) ---------------------------------------------

def test_no_key_uses_template_and_quotes_description(monkeypatch):
    """With no API key, the fallback runs and quotes the retrieved description."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = generate_explanation(DESCRIPTION, REASONS, title="Library Rain", config=ExplainerConfig())
    assert isinstance(result, str) and result.strip()
    # Grounded: it quotes text from the retrieved description.
    assert "acoustic lo-fi piece" in result
    assert "Library Rain" in result


def test_no_key_does_not_call_llm(monkeypatch):
    """The LLM path must not be invoked when there's no key."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def _boom(*args, **kwargs):
        raise AssertionError("_llm_explanation should not be called without a key")

    monkeypatch.setattr(explainer, "_llm_explanation", _boom)
    result = generate_explanation(DESCRIPTION, REASONS, title="Library Rain", config=ExplainerConfig())
    assert "acoustic lo-fi piece" in result


def test_template_quotes_description_directly():
    out = build_template_explanation(DESCRIPTION, REASONS, title="Library Rain")
    assert "acoustic lo-fi piece" in out
    assert out.startswith("'Library Rain'")


def test_template_handles_no_reasons():
    out = build_template_explanation(DESCRIPTION, [], title="Library Rain")
    assert isinstance(out, str) and out.strip()
    assert "acoustic lo-fi piece" in out


def test_template_handles_empty_everything():
    out = build_template_explanation("", [])
    assert isinstance(out, str) and out.strip()  # still returns a usable sentence


# --- Graceful handling on LLM failure ---------------------------------------

def test_api_failure_falls_back_without_crashing(monkeypatch):
    """A key is present but the LLM call raises -> return the template, no crash."""
    def _fail(*args, **kwargs):
        raise RuntimeError("simulated API failure")

    monkeypatch.setattr(explainer, "_llm_explanation", _fail)
    config = ExplainerConfig(api_key="sk-ant-fake-key")
    result = generate_explanation(DESCRIPTION, REASONS, title="Library Rain", config=config)
    assert isinstance(result, str) and result.strip()
    assert "acoustic lo-fi piece" in result  # fell back to the grounded template


def test_api_empty_response_falls_back(monkeypatch):
    """An empty/whitespace LLM response is treated as failure -> template."""
    def _empty(*args, **kwargs):
        raise ValueError("Empty response from Claude")

    monkeypatch.setattr(explainer, "_llm_explanation", _empty)
    config = ExplainerConfig(api_key="sk-ant-fake-key")
    result = generate_explanation(DESCRIPTION, REASONS, config=config)
    assert isinstance(result, str) and result.strip()


def test_llm_success_path_is_used_when_it_works(monkeypatch):
    """When the LLM path succeeds, its result is returned verbatim."""
    monkeypatch.setattr(
        explainer, "_llm_explanation", lambda *a, **k: "A crafted one-liner."
    )
    config = ExplainerConfig(api_key="sk-ant-fake-key")
    result = generate_explanation(DESCRIPTION, REASONS, config=config)
    assert result == "A crafted one-liner."
