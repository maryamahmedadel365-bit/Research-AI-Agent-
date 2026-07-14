from typing import Dict, List, Protocol


class IDocumentConverter(Protocol):
    """Node 1 contract: turn a source PDF into Markdown."""

    def convert(self, pdf_path: str) -> str:
        """Return the full document as Markdown, headings preserved."""
        ...


class ISectionSplitter(Protocol):
    """Node 2a contract: split markdown into the paper's OWN sections."""

    def split(self, markdown: str) -> Dict[str, str]:
        """Return {heading_text: section_content}, in document order."""
        ...


class ISectionClassifier(Protocol):
    """Node 2b contract: map natural sections to target categories."""

    def classify(self, sections: Dict[str, str]) -> Dict[str, List[str]]:
        """Return {category: [heading_text, ...]} for methods/experiments/
        limitations/other."""
        ...


class IFieldExtractor(Protocol):
    """Node 3.x contract: extract exactly one output field."""

    field_name: str

    def extract(self, sections: Dict[str, str], category_map: Dict[str, List[str]]) -> str:
        """Return the extracted text for this extractor's field."""
        ...


class IResultAssembler(Protocol):
    """Node 4 contract: combine field outputs into one structured object."""

    def assemble(self, fields: Dict[str, str]) -> object:
        ...


class IPageSink(Protocol):
    """Node 5 contract: write the final structured object somewhere (Notion, etc.)."""

    def write(self, result: object) -> str:
        """Return an identifier (e.g. page id) for the written record."""
        ...