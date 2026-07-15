from typing import Dict, List

EXTRACT_PROMPT = """Below is content from a research paper that may discuss its
limitations. Identify any limitations or weaknesses mentioned (stated
explicitly or reasonably inferred), in 2-4 concise sentences. If truly
none are present, respond with "Not explicitly discussed."

---
{content}
---"""

FALLBACK_HEADING_KEYWORDS = ("discussion", "conclusion", "future work")


class LimitationsExtractor:
    field_name = "limitations"

    def __init__(self, llm):
        self.llm = llm

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        headings = category_map.get("limitations", [])
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
            # Fallback: scan for likely headings the classifier may have missed.
            for heading, text in sections.items():
                if any(keyword in heading.lower() for keyword in FALLBACK_HEADING_KEYWORDS):
                    content += "\n\n" + text

        content = content.strip()
        if not content:
            return "Not explicitly discussed."

        response = self.llm.invoke(EXTRACT_PROMPT.format(content=content))
        return response.content