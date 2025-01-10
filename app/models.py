# models.py
from pydantic import BaseModel
from typing import Optional, List, Dict

class PredictionInput(BaseModel):
    KatashikiIds: List[str]