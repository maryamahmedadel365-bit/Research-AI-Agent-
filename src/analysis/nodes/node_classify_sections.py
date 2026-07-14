from state import PipelineState


def make_classify_sections_node(classifier):
    def classify_sections_node(state: PipelineState) -> dict:
        sections = state.get("sections")
        if not sections:
            return {"errors": ["classify_sections: no sections in state"]}
        try:
            category_map = classifier.classify(sections)
        except Exception as e:
            return {"errors": [f"classify_sections: {e}"]}
        return {"category_map": category_map}

    return classify_sections_node