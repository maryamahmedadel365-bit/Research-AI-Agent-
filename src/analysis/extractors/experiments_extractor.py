from typing import Dict, List

EXTRACT_PROMPT = """Below is the experiments/results section of a research paper.
Describe the experimental setup, datasets/benchmarks used, and headline
results in 2-4 concise sentences.

---
{content}
---"""


class ExperimentsExtractor:
    field_name = "experiments"

    def __init__(self, llm):
        self.llm = llm

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        headings = category_map.get("experiments", [])
        content = "\n\n".join(sections.get(h, "") for h in headings).strip()
        if not content:
            return ""
        response = self.llm.invoke(EXTRACT_PROMPT.format(content=content))
        return response.content