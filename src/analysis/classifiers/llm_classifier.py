import json
import re
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
fallback heading (e.g. Discussion or Conclusion) rather than leaving it empty.

Return your answer as a JSON object with exactly these four keys:
"methods", "experiments", "limitations", "other"
Each value should be a list of heading strings.
Return ONLY the JSON object, no other text."""


def _extract_json(text: str) -> dict:
    """Extract a JSON object from LLM output that may contain extra text."""
    # Try to find JSON in code fences first
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        return json.loads(fence_match.group(1))
    # Try to find raw JSON object
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        return json.loads(brace_match.group(0))
    raise ValueError(f"No JSON found in LLM response: {text[:200]}")


class LlmSectionClassifier:
    def __init__(self, llm):
        self.llm = llm

    def classify(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        heading_list = "\n".join(f"- {heading}" for heading in sections.keys())
        prompt = CLASSIFY_PROMPT.format(heading_list=heading_list)
        response = self.llm.invoke(prompt)
        
        # response can be an AIMessage or a plain string
        text = response.content if hasattr(response, "content") else str(response)
        
        parsed = _extract_json(text)
        result = CategoryMap(**parsed)
        return result.model_dump()