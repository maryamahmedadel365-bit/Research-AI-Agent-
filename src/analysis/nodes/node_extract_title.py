from state import PipelineState


def make_extract_title_node(extractor):
    def extract_title_node(state: PipelineState) -> dict:
        sections = state.get("sections", {})
        category_map = state.get("category_map", {})
        try:
            title = extractor.extract(sections, category_map)
        except Exception as e:
            return {"errors": [f"extract_title: {e}"]}
        return {"title": title}

    return extract_title_node