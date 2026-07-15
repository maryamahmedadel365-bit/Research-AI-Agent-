import re
from typing import Dict

HEADING_PATTERN = re.compile(r"^#{1,3}\s+(.*)")


class HeadingSplitter:
    def split(self, markdown: str) -> Dict[str, str]:
        sections: Dict[str, str] = {}
        current_heading = "preamble"
        current_lines = []

        for line in markdown.splitlines():
            match = HEADING_PATTERN.match(line)
            if match:
                sections[current_heading] = "\n".join(current_lines).strip()
                raw_heading = match.group(1).strip()
                clean_heading = re.sub(r'[*_]', '', raw_heading).strip()
                current_heading = clean_heading
                current_lines = []
            else:
                current_lines.append(line)

        sections[current_heading] = "\n".join(current_lines).strip()

        # Drop the preamble key if it ended up empty (paper started right at a heading)
        if not sections.get("preamble"):
            sections.pop("preamble", None)

        return sections