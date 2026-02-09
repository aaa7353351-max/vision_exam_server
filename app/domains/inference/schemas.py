# app/domains/inference/schemas.py

from typing import List
from pydantic import BaseModel


class TopKItem(BaseModel):
    label: str
    score: float


class InferenceResponse(BaseModel):
    id: str
    model_name: str
    topk: List[TopKItem]


class InferenceListResponse(BaseModel):
    items: list
    skip: int
    limit: int
    count: int
