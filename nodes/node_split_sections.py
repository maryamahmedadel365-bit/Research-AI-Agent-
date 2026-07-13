from state import PipelineState


def make_split_sections_node(splitter):
    def split_sections_node(state: PipelineState) -> dict:
        markdown = state.get("markdown")
        if not markdown:
            return {"errors": ["split_sections: no markdown in state"]}
        try:
            sections = splitter.split(markdown)
        except Exception as e:
            return {"errors": [f"split_sections: {e}"]}
        return {"sections": sections}

    return split_sections_node