from typing import Dict, List

from pydantic import BaseModel


class CategoryMap(BaseModel):
    methods: List[str]
    experiments: List[str]
    limitations: List[str]
    other: List[str]


CLASSIFY_PROMPT = """Here are the section headings from a research paper, in order:

{heading_list}

Classify each heading into exactly one of: methods, experiments, limitations, other.
A heading can appear in only one category. If no heading clearly covers a category
(especially "limitations", which is often not its own section), pick the closest
fallback heading (e.g. Discussion or Conclusion) rather than leaving it empty."""


class LlmSectionClassifier:
    def __init__(self, llm):
        self.structured_llm = llm.with_structured_output(CategoryMap)

    def classify(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        heading_list = "\n".join(f"- {heading}" for heading in sections.keys())
        prompt = CLASSIFY_PROMPT.format(heading_list=heading_list)
        result = self.structured_llm.invoke(prompt)
        return result.model_dump()