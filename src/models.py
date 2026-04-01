from pydantic import BaseModel
from typing import Optional, List


class NormalizedRequirement(BaseModel):
    requirement_id: str
    title: str
    description: str
    acceptance_criteria: str
    repro_steps: str
    tags: List[str]
    source_url: Optional[str] = None
    source_type: str