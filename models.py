from pydantic import BaseModel, Field

class PaperSummary(BaseModel):
    title: str = Field(description="The paper's title, exactly as written")
    methods: str = Field(description="Concise description of the methodology/approach used")
    experiments: str = Field(description="Concise description of experiments run and key results")
    limitations: str = Field(description="Limitations acknowledged or evident in the paper")
    summary: str = Field(description="A 3-5 sentence plain-language summary of the whole paper")