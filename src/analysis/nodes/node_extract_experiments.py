from state import PipelineState


def make_extract_experiments_node(extractor):
    def extract_experiments_node(state: PipelineState) -> dict:
        sections = state.get("sections", {})
        category_map = state.get("category_map", {})
        try:
            experiments = extractor.extract(sections, category_map)
        except Exception as e:
            return {"errors": [f"extract_experiments: {e}"]}
        return {"experiments": experiments}

    return extract_experiments_node