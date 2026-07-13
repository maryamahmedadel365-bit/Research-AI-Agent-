from models import PaperSummary


class ResultAssembler:
    def assemble(self, fields: dict) -> PaperSummary:
        return PaperSummary(
            title=fields.get("title", ""),
            methods=fields.get("methods", ""),
            experiments=fields.get("experiments", ""),
            limitations=fields.get("limitations", ""),
            summary=fields.get("summary", ""),
        )