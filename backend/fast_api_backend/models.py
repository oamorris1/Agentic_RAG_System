from pydantic import BaseModel
from typing import List


class DocumentSummary(BaseModel):
    title: str
    summary: str



class FinalResult(BaseModel):
   user_query: str
   result: str

class FinalSummaryResult(BaseModel):
    result: str 
    
class CrewResult(BaseModel):
    final_result: FinalResult