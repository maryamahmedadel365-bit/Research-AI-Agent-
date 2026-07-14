from typing import Dict, List

SUMMARY_PROMPT = """Given the following extracted details about a research paper,
write a 3-5 sentence plain-language summary of the paper as a whole.

Title: {title}
Methods: {methods}
Experiments: {experiments}
Limitations: {limitations}"""


class SummaryExtractor:
    field_name = "summary"

    def __init__(self, llm):
        self.llm = llm

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        # Note: in practice this extractor is called with already-extracted
        # fields (title/methods/experiments/limitations) rather than raw
        # sections — see nodes/node_extract_summary.py for how those get
        # passed in via state instead of the sections/category_map args.
        raise NotImplementedError(
            "SummaryExtractor.extract() is invoked via its node wrapper, "
            "which passes already-extracted fields — see node_extract_summary.py"
        )

    def extract_from_fields(self, title: str, methods: str, experiments: str, limitations: str) -> str:
        prompt = SUMMARY_PROMPT.format(
            title=title, methods=methods, experiments=experiments, limitations=limitations
        )
        response = self.llm.invoke(prompt)
        return response.content