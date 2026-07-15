import operator
from typing import Annotated, Dict, List, TypedDict


class PipelineState(TypedDict, total=False):

    pdf_path: str
    url: str
    
    markdown: str
    
    sections: Dict[str, str]
    
    category_map: Dict[str, List[str]]
    
    title: str
    methods: str
    experiments: str
    limitations: str
    summary: str
    
    paper_summary: dict
    
    notion_page_id: str
    
    errors: Annotated[List[str], operator.add]


def initial_state(pdf_path: str, url: str = "") -> PipelineState:
    return PipelineState(pdf_path=pdf_path, url=url, errors=[])