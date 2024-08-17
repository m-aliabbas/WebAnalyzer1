from typing import List, Optional
from pydantic import BaseModel, Field, root_validator, ValidationError

class SentenceParser(BaseModel):
    originalContent: str = Field(..., description="Original Sentence with no correction")
    correctedSentence: str = Field(..., description="Corrected Sentence in English UK. Enclosed corrections in <b></b>.")

    @root_validator(pre=True)
    def fill_missing_fields(cls, values):
        values['correctedSentence'] = values.get('correctedSentence', '')
        return values

# Define ResponseModel to include sentences
class ResponseModel(BaseModel):
    sentences: List[SentenceParser]