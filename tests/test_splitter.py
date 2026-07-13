"""
Tests for splitters/heading_splitter.py.

No LLM, no network, no API cost — this only checks that markdown text
gets cut into the right pieces based on # / ## / ### headings. Run this
BEFORE spending any API budget on the LLM-dependent parts, since a bug
here would silently corrupt every downstream step.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from splitters.heading_splitter import HeadingSplitter


SAMPLE_MARKDOWN = """# Attention Is All You Need

Some intro text before any section heading.

## 1. Introduction

Transformers rely on attention mechanisms.

## 2. Methodology

We propose a new architecture called the Transformer.

## 3. Experiments

We evaluate on WMT 2014 English-German translation.

## 4. Limitations

Our approach requires significant compute for training.
"""


def test_splits_by_heading():
    splitter = HeadingSplitter()
    sections = splitter.split(SAMPLE_MARKDOWN)

    assert "Attention Is All You Need" in sections
    assert "1. Introduction" in sections
    assert "2. Methodology" in sections
    assert "3. Experiments" in sections
    assert "4. Limitations" in sections


def test_section_content_is_correct():
    splitter = HeadingSplitter()
    sections = splitter.split(SAMPLE_MARKDOWN)

    assert "new architecture" in sections["2. Methodology"]
    assert "WMT 2014" in sections["3. Experiments"]
    assert "significant compute" in sections["4. Limitations"]


def test_no_preamble_key_when_paper_starts_at_heading():
    markdown = "# Title\n\n## Section One\ncontent"
    splitter = HeadingSplitter()
    sections = splitter.split(markdown)

    assert "preamble" not in sections


if __name__ == "__main__":
    test_splits_by_heading()
    test_section_content_is_correct()
    test_no_preamble_key_when_paper_starts_at_heading()
    print("All heading_splitter tests passed.")
