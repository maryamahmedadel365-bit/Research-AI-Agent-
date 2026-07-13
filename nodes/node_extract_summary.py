from state import PipelineState


def make_extract_summary_node(extractor):
    def extract_summary_node(state: PipelineState) -> dict:
        try:
            summary = extractor.extract_from_fields(
                title=state.get("title", ""),
                methods=state.get("methods", ""),
                experiments=state.get("experiments", ""),
                limitations=state.get("limitations", ""),
            )
        except Exception as e:
            return {"errors": [f"extract_summary: {e}"]}
        return {"summary": summary}

    return extract_summary_node