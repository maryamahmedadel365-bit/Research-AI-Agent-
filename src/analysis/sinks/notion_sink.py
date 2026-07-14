from notion_client import Client

from schemas import PaperSummary


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
        return page["id"]