from typing import Dict, List


class TitleExtractor:
    field_name = "title"

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        # The splitter's first real heading is almost always the paper title.
        for heading in sections.keys():
            if heading != "preamble":
                return heading
        return "Unknown Title"