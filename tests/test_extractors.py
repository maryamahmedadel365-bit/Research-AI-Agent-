"""
Tests for extractors/*.py.

Same fake-LLM approach as test_classifier.py — no real API calls. These
tests focus on the logic that's easy to get wrong: making sure each
extractor only reads the section(s) assigned to its category (not the
whole paper), and that LimitationsExtractor's fallback scan kicks in when
the classifier found nothing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extractors.limitations_extractor import LimitationsExtractor
from extractors.methods_extractor import MethodsExtractor
from extractors.title_extractor import TitleExtractor


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    """Records the last prompt it received and returns a fixed response —
    lets tests assert on WHAT was sent, not just what came back."""

    def __init__(self, fixed_text: str):
        self.fixed_text = fixed_text
        self.last_prompt = None

    def invoke(self, prompt: str) -> FakeResponse:
        self.last_prompt = prompt
        return FakeResponse(self.fixed_text)


def test_title_extractor_needs_no_llm():
    extractor = TitleExtractor()
    sections = {"Attention Is All You Need": "...", "1. Introduction": "..."}
    title = extractor.extract(sections, category_map={})

    assert title == "Attention Is All You Need"


def test_methods_extractor_only_sees_methods_sections():
    llm = FakeLLM(fixed_text="Uses a Transformer architecture.")
    extractor = MethodsExtractor(llm)

    sections = {
        "1. Introduction": "unrelated background text",
        "2. Methodology": "the actual method description",
    }
    category_map = {"methods": ["2. Methodology"]}

    result = extractor.extract(sections, category_map)

    assert result == "Uses a Transformer architecture."
    # The prompt sent to the LLM should contain ONLY the scoped section,
    # not the unrelated Introduction text.
    assert "the actual method description" in llm.last_prompt
    assert "unrelated background text" not in llm.last_prompt


def test_limitations_extractor_uses_classifier_result_when_present():
    llm = FakeLLM(fixed_text="Limited to English-German translation.")
    extractor = LimitationsExtractor(llm)

    sections = {"5. Discussion": "only evaluated on one language pair"}
    category_map = {"limitations": ["5. Discussion"]}

    result = extractor.extract(sections, category_map)

    assert result == "Limited to English-German translation."


def test_limitations_extractor_falls_back_when_classifier_found_nothing():
    llm = FakeLLM(fixed_text="Inferred limitation from conclusion.")
    extractor = LimitationsExtractor(llm)

    sections = {
        "1. Introduction": "...",
        "6. Conclusion": "future work should explore larger datasets",
    }
    category_map = {"limitations": []}  # classifier found no dedicated section

    result = extractor.extract(sections, category_map)

    assert result == "Inferred limitation from conclusion."
    assert "future work should explore larger datasets" in llm.last_prompt


def test_limitations_extractor_returns_placeholder_when_truly_nothing_found():
    llm = FakeLLM(fixed_text="should not be called")
    extractor = LimitationsExtractor(llm)

    sections = {"1. Introduction": "..."}
    category_map = {"limitations": []}

    result = extractor.extract(sections, category_map)

    assert result == "Not explicitly discussed."
    assert llm.last_prompt is None  # confirms no API call was made


if __name__ == "__main__":
    test_title_extractor_needs_no_llm()
    test_methods_extractor_only_sees_methods_sections()
    test_limitations_extractor_uses_classifier_result_when_present()
    test_limitations_extractor_falls_back_when_classifier_found_nothing()
    test_limitations_extractor_returns_placeholder_when_truly_nothing_found()
    print("All extractor tests passed (no real API calls made).")
