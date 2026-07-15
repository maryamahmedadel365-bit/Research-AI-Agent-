from notion_client import Client

from ..schemas import PaperSummary


def _rich_text(content: str, limit: int = 2000) -> list:
    """Notion rich_text properties cap at ~2000 chars per block."""
    return [{"text": {"content": content[:limit]}}]


class NotionPageWriter:
    def __init__(self, notion_token: str, database_id: str):
        self.client = Client(auth=notion_token)
        self.database_id = database_id

    def write(self, result: PaperSummary) -> str:
        page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties={
                "Title": {"title": [{"text": {"content": result.title}}]},
                "Methods": {"rich_text": _rich_text(result.methods)},
                "Experiments": {"rich_text": _rich_text(result.experiments)},
                "Limitations": {"rich_text": _rich_text(result.limitations)},
                "Summary": {"rich_text": _rich_text(result.summary)},
            },
        )
        return page["id"]  # type: ignore

    def get_all_papers(self) -> list[PaperSummary]:
        response = self.client.databases.query(
            database_id=self.database_id,
            sorts=[{"timestamp": "created_time", "direction": "descending"}],
            page_size=50
        )
        
        papers = []
        for page in response.get("results", []):
            props = page.get("properties", {})
            
            def get_text(prop_name: str) -> str:
                prop = props.get(prop_name, {})
                if "title" in prop and prop["title"]:
                    return prop["title"][0].get("text", {}).get("content", "")
                if "rich_text" in prop and prop["rich_text"]:
                    return prop["rich_text"][0].get("text", {}).get("content", "")
                return ""
            
            # Since Notion only has these fields, we create a dummy PaperSummary 
            # Note: The frontend expects PaperSummaryResponse which has more fields, 
            # but we can just fill the available ones.
            paper = PaperSummary(
                title=get_text("Title"),
                methods=get_text("Methods"),
                experiments=get_text("Experiments"),
                limitations=get_text("Limitations"),
                summary=get_text("Summary")
            )
            # We inject the created time as an extra field if possible, but PaperSummary doesn't have it.
            # We'll just return it as a dict or PaperSummary.
            papers.append(paper)
            
        return papers