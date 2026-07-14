from schemas import PaperSummary
from state import PipelineState


def make_notion_write_node(sink):
    def notion_write_node(state: PipelineState) -> dict:
        paper_summary_dict = state.get("paper_summary")
        if not paper_summary_dict:
            return {"errors": ["notion_write: no paper_summary in state"]}
        try:
            paper_summary = PaperSummary(**paper_summary_dict)
            page_id = sink.write(paper_summary)
        except Exception as e:
            return {"errors": [f"notion_write: {e}"]}
        return {"notion_page_id": page_id}

    return notion_write_node