from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Question(BaseModel):
    id: str
    type: Literal["choice", "score", "bool"]
    question: str
    options: list[str] = Field(default_factory=list)
    min: float | None = None
    max: float | None = None


class SystemOneRequest(BaseModel):
    state: Any
    model: str = "local-llama"
    questions: list[Question]


class Decision(BaseModel):
    id: str
    type: str
    answer: Any
    score: float | None = None
    probabilities: dict[str, float] | None = None


class SystemOneResponse(BaseModel):
    id: str
    model: str
    decisions: list[Decision]
