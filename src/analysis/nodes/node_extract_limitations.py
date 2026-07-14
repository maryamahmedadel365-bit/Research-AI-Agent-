from state import PipelineState


def make_extract_limitations_node(extractor):
    def extract_limitations_node(state: PipelineState) -> dict:
        sections = state.get("sections", {})
        category_map = state.get("category_map", {})
        try:
            limitations = extractor.extract(sections, category_map)
        except Exception as e:
            return {"errors": [f"extract_limitations: {e}"]}
        return {"limitations": limitations}

    return extract_limitations_node