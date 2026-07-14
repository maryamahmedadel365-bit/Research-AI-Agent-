from ..state import PipelineState


def make_extract_methods_node(extractor):
    def extract_methods_node(state: PipelineState) -> dict:
        sections = state.get("sections", {})
        category_map = state.get("category_map", {})
        try:
            methods = extractor.extract(sections, category_map)
        except Exception as e:
            return {"errors": [f"extract_methods: {e}"]}
        return {"methods": methods}

    return extract_methods_node