from state import PipelineState


def make_pdf_to_markdown_node(converter):
    def pdf_to_markdown_node(state: PipelineState) -> dict:
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            return {"errors": ["pdf_to_markdown: no pdf_path in state"]}
        try:
            markdown = converter.convert(pdf_path)
        except Exception as e:
            return {"errors": [f"pdf_to_markdown: {e}"]}
        return {"markdown": markdown}

    return pdf_to_markdown_node