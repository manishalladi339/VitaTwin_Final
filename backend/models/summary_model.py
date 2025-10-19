from pydantic import BaseModel
class SummaryIn(BaseModel):
    text: str
