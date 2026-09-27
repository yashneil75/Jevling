from __future__ import annotations

from .models import Question


def make_tool_schema(questions: list[Question]) -> dict:
    properties = {}

    for q in questions:
        if q.type == "choice":
            properties[q.id] = {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "enum": q.options,
                    },
                    "probabilities": {
                        "type": "object",
                        "additionalProperties": {"type": "number"},
                    },
                },
                "required": ["answer", "probabilities"],
            }

        elif q.type == "bool":
            properties[q.id] = {
                "type": "object",
                "properties": {
                    "answer": {"type": "boolean"},
                    "probability_yes": {"type": "number"},
                },
                "required": ["answer", "probability_yes"],
            }

        elif q.type == "score":
            properties[q.id] = {
                "type": "object",
                "properties": {
                    "answer": {"type": "number"},
                },
                "required": ["answer"],
            }

    return {
        "type": "function",
        "function": {
            "name": "jev_decision",
            "description": (
                "Return the requested structured decisions. "
                "You MUST call this function."
            ),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(properties.keys()),
                "additionalProperties": False,
            },
        },
    }
