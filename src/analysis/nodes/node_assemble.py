from ..state import PipelineState


def make_assemble_node(assembler):
    def assemble_node(state: PipelineState) -> dict:
        fields = {
            "title": state.get("title", ""),
            "methods": state.get("methods", ""),
            "experiments": state.get("experiments", ""),
            "limitations": state.get("limitations", ""),
            "summary": state.get("summary", ""),
            "url": state.get("url", ""),
        }
        try:
            paper_summary = assembler.assemble(fields)
        except Exception as e:
            return {"errors": [f"assemble: {e}"]}
        return {"paper_summary": paper_summary.model_dump()}

    return assemble_node