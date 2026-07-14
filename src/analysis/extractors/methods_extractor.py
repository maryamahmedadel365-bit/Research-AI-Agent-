from typing import Dict, List

EXTRACT_PROMPT = """Below is the methodology section of a research paper.
Describe the core method/approach in 2-4 concise sentences.

---
{content}
---"""


class MethodsExtractor:
    field_name = "methods"

    def __init__(self, llm):
        self.llm = llm

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        headings = category_map.get("methods", [])
        content = "\n\n".join(sections.get(h, "") for h in headings).strip()
        if not content:
            return ""
        response = self.llm.invoke(EXTRACT_PROMPT.format(content=content))
        return response.content