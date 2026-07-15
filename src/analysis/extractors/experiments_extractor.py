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
        content_parts = []
        for h in headings:
            if h in sections:
                content_parts.append(sections[h])
            else:
                for section_h, text in sections.items():
                    if h.lower() in section_h.lower() or section_h.lower() in h.lower():
                        content_parts.append(text)
                        break
        
        content = "\n\n".join(content_parts).strip()
        if not content:
            return ""
        response = self.llm.invoke(EXTRACT_PROMPT.format(content=content))
        return response.content