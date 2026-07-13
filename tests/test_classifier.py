"""
Tests for classifiers/llm_classifier.py.

Uses a FAKE LLM (a tiny stand-in object) instead of a real ChatOpenAI
or ChatOllama instance. This is only possible because
LlmSectionClassifier depends on the LLM's INTERFACE (an object with
.with_structured_output().invoke()), not a specific provider — the same
reason config.py can swap providers without touching this file. Running
this test costs $0 and requires no API key.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifiers.llm_classifier import CategoryMap, LlmSectionClassifier


class FakeStructuredLLM:
    """Stands in for llm.with_structured_output(CategoryMap) — returns a
    fixed CategoryMap instead of actually calling an API."""

    def __init__(self, fixed_response: CategoryMap):
        self.fixed_response = fixed_response
        self.last_prompt = None  # lets a test inspect what would've been sent

    def invoke(self, prompt: str) -> CategoryMap:
        self.last_prompt = prompt
        return self.fixed_response


class FakeLLM:
    """Stands in for a real ChatOpenAI/ChatOllama object."""

    def __init__(self, fixed_response: CategoryMap):
        self._structured = FakeStructuredLLM(fixed_response)

    def with_structured_output(self, schema):
        return self._structured


def test_classify_returns_category_map():
    fixed = CategoryMap(
        methods=["2. Methodology"],
        experiments=["3. Experiments"],
        limitations=["4. Discussion"],
        other=["1. Introduction"],
    )
    classifier = LlmSectionClassifier(llm=FakeLLM(fixed))

    sections = {
        "1. Introduction": "...",
        "2. Methodology": "...",
        "3. Experiments": "...",
        "4. Discussion": "...",
    }
    result = classifier.classify(sections)

    assert result["methods"] == ["2. Methodology"]
    assert result["experiments"] == ["3. Experiments"]
    assert result["limitations"] == ["4. Discussion"]
    assert result["other"] == ["1. Introduction"]


def test_classify_sends_all_headings_in_prompt():
    fixed = CategoryMap(methods=[], experiments=[], limitations=[], other=[])
    llm = FakeLLM(fixed)
    classifier = LlmSectionClassifier(llm=llm)

    sections = {"Intro": "...", "Methods": "..."}
    classifier.classify(sections)

    sent_prompt = llm._structured.last_prompt
    assert "Intro" in sent_prompt
    assert "Methods" in sent_prompt


if __name__ == "__main__":
    test_classify_returns_category_map()
    test_classify_sends_all_headings_in_prompt()
    print("All llm_classifier tests passed (no real API calls made).")