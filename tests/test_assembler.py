"""
Tests for assembler/result_assembler.py.

No LLM, no network, no mocks needed at all — this class just reshapes a
plain dict into a PaperSummary object, so the test is straightforward
input/output checking.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assembler.result_assembler import ResultAssembler
from models import PaperSummary


def test_assembles_all_fields_correctly():
    assembler = ResultAssembler()
    fields = {
        "title": "Attention Is All You Need",
        "methods": "A new attention-based architecture.",
        "experiments": "Evaluated on WMT 2014 translation tasks.",
        "limitations": "Requires significant compute.",
        "summary": "This paper introduces the Transformer architecture.",
    }

    result = assembler.assemble(fields)

    assert isinstance(result, PaperSummary)
    assert result.title == fields["title"]
    assert result.methods == fields["methods"]
    assert result.experiments == fields["experiments"]
    assert result.limitations == fields["limitations"]
    assert result.summary == fields["summary"]


def test_missing_fields_default_to_empty_string():
    assembler = ResultAssembler()
    result = assembler.assemble({"title": "Only Title Provided"})

    assert result.title == "Only Title Provided"
    assert result.methods == ""
    assert result.experiments == ""
    assert result.limitations == ""
    assert result.summary == ""


if __name__ == "__main__":
    test_assembles_all_fields_correctly()
    test_missing_fields_default_to_empty_string()
    print("All result_assembler tests passed.")
