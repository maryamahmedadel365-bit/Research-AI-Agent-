"""
Graph assembly.

This is the only file in the project that imports concrete
implementations (PyMuPdfMarkdownConverter, HeadingSplitter, etc.) — every
node file itself stays interface-only, and every implementation file
stays graph-agnostic. If you swap an implementation (e.g. Docling instead
of PyMuPdf, OpenAI instead of Ollama via config.py), this is the only
file that changes.

Edge structure:
  pdf_to_markdown -> split_sections -> classify_sections
  classify_sections fans out to 4 parallel extractors:
      -> extract_title, extract_methods, extract_experiments, extract_limitations
  all 4 feed into extract_summary (sequenced, not parallel — see
      extractors/summary_extractor.py for why)
  extract_summary -> assemble -> notion_write -> END
"""

import os

from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import END, StateGraph

from .assembler.result_assembler import ResultAssembler
from .classifiers.llm_classifier import LlmSectionClassifier
from .config import get_llm
from .converters.pymupdf_converter import PyMuPdfMarkdownConverter
from .extractors.experiments_extractor import ExperimentsExtractor
from .extractors.limitations_extractor import LimitationsExtractor
from .extractors.methods_extractor import MethodsExtractor
from .extractors.summary_extractor import SummaryExtractor
from .extractors.title_extractor import TitleExtractor
from .nodes.node_assemble import make_assemble_node
from .nodes.node_classify_sections import make_classify_sections_node
from .nodes.node_extract_experiments import make_extract_experiments_node
from .nodes.node_extract_limitations import make_extract_limitations_node
from .nodes.node_extract_methods import make_extract_methods_node
from .nodes.node_extract_summary import make_extract_summary_node
from .nodes.node_extract_title import make_extract_title_node
from .nodes.node_notion_write import make_notion_write_node
from .nodes.node_pdf_to_markdown import make_pdf_to_markdown_node
from .nodes.node_split_sections import make_split_sections_node
from .sinks.notion_sink import NotionPageWriter
from .splitters.heading_splitter import HeadingSplitter
from .state import PipelineState, initial_state


def _continue_or_stop(state: PipelineState) -> str:
    """Router used after each critical (non-parallel) step. If a prior node
    already recorded an error, jump straight to END instead of letting later
    nodes run on empty/partial state — this is what stops e.g.
    extract_summary from attempting a real API call after pdf_to_markdown
    already failed, which previously wasted a call and produced a
    confusing pileup of unrelated error messages."""
    if state.get("errors"):
        return "stop"
    return "continue"


def _classify_router(state: PipelineState):
    """Router for the fan-out point specifically. Unlike _continue_or_stop,
    this returns actual node names (or END) directly rather than a
    "continue"/"stop" label — LangGraph's path_map only maps a single
    returned key to a single destination, so branching to MULTIPLE parallel
    nodes at once has to be done by returning the list of destinations
    straight from the router function instead."""
    if state.get("errors"):
        return END
    return ["extract_title", "extract_methods", "extract_experiments", "extract_limitations"]


def build_graph():
    llm = get_llm()

    graph = StateGraph(PipelineState)  # type: ignore

    graph.add_node("pdf_to_markdown", make_pdf_to_markdown_node(PyMuPdfMarkdownConverter()))
    graph.add_node("split_sections", make_split_sections_node(HeadingSplitter()))
    graph.add_node("classify_sections", make_classify_sections_node(LlmSectionClassifier(llm)))

    graph.add_node("extract_title", make_extract_title_node(TitleExtractor()))
    graph.add_node("extract_methods", make_extract_methods_node(MethodsExtractor(llm)))
    graph.add_node("extract_experiments", make_extract_experiments_node(ExperimentsExtractor(llm)))
    graph.add_node("extract_limitations", make_extract_limitations_node(LimitationsExtractor(llm)))
    graph.add_node("extract_summary", make_extract_summary_node(SummaryExtractor(llm)))

    graph.add_node("assemble", make_assemble_node(ResultAssembler()))

    notion_sink = NotionPageWriter(
        notion_token=os.environ["NOTION_TOKEN"],
        database_id=os.environ["NOTION_DATABASE_ID"],
    )
    graph.add_node("notion_write", make_notion_write_node(notion_sink))

    graph.set_entry_point("pdf_to_markdown")

    graph.add_conditional_edges(
        "pdf_to_markdown", _continue_or_stop, {"continue": "split_sections", "stop": END}
    )
    graph.add_conditional_edges(
        "split_sections", _continue_or_stop, {"continue": "classify_sections", "stop": END}
    )

    # Fan-out: these 4 run in parallel, but only if classify_sections succeeded
    graph.add_conditional_edges("classify_sections", _classify_router)

    # Join + sequence: extract_summary waits for all 4 above, then runs
    graph.add_edge("extract_title", "extract_summary")
    graph.add_edge("extract_methods", "extract_summary")
    graph.add_edge("extract_experiments", "extract_summary")
    graph.add_edge("extract_limitations", "extract_summary")

    graph.add_edge("extract_summary", "assemble")
    graph.add_edge("assemble", "notion_write")
    graph.add_edge("notion_write", END)

    return graph.compile()


if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample_paper.pdf"
    app = build_graph()
    result = app.invoke(initial_state(pdf_path))

    if result.get("errors"):
        print("Errors:", result["errors"])
    else:
        print("Notion page created:", result.get("notion_page_id"))