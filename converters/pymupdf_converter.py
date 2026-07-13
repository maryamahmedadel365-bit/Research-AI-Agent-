import pymupdf4llm


class PyMuPdfMarkdownConverter:
    def convert(self, pdf_path: str) -> str:
        markdown = pymupdf4llm.to_markdown(pdf_path)
        if not markdown or not markdown.strip():
            raise ValueError(f"No extractable content found in PDF: {pdf_path}")
        return markdown