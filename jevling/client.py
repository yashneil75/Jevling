from __future__ import annotations

import json
import uuid

from llama_cpp import Llama

from .config import MODEL_FILE, MODEL_REPO
from .models import Decision, SystemOneRequest, SystemOneResponse
from .tool_schema import make_tool_schema

SYSTEM_PROMPT = """You are a structured decision engine.

Evaluate the supplied state against every question.

You MUST use the jev_decision tool.
Do not answer with normal assistant text.

For choice questions:
- choose exactly one supplied option
- probabilities must be numbers between 0 and 1
- probabilities should sum approximately to 1

For boolean questions:
- answer true or false
- probability_yes must be between 0 and 1

For score questions:
- return a numeric score within the supplied range when a range is provided.
"""


class JevlingClient:
    def __init__(
        self,
        repo_id: str = MODEL_REPO,
        filename: str = MODEL_FILE,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,
    ):
        self._llm = Llama.from_pretrained(
            repo_id=repo_id,
            filename=filename,
            chat_format="chatml-function-calling",
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )

    def decide(self, req: SystemOneRequest) -> SystemOneResponse:
        if not req.questions:
            raise ValueError("questions must not be empty")
        if len(req.questions) > 8:
            raise ValueError("maximum of 8 questions")

        tool = make_tool_schema(req.questions)
        user = self._build_user_message(req)

        result = self._llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            tools=[tool],
            tool_choice={
                "type": "function",
                "function": {"name": "jev_decision"},
            },
            temperature=0,
            max_tokens=2048,
        )

        message = result["choices"][0]["message"]
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            raise RuntimeError("Model did not produce the required tool call")

        call = tool_calls[0]
        if call["function"]["name"] != "jev_decision":
            raise RuntimeError("Unexpected tool call")

        try:
            arguments = json.loads(call["function"]["arguments"])
        except json.JSONDecodeError as exc:
            raise RuntimeError("Model produced invalid tool arguments") from exc

        return SystemOneResponse(
            id=f"decision-{uuid.uuid4()}",
            model=req.model,
            decisions=self._parse_decisions(req, arguments),
        )

    @staticmethod
    def _build_user_message(req: SystemOneRequest) -> str:
        question_text = [
            {
                "id": q.id,
                "type": q.type,
                "question": q.question,
                "options": q.options,
                "min": q.min,
                "max": q.max,
            }
            for q in req.questions
        ]
        return json.dumps(
            {"state": req.state, "questions": question_text},
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _parse_decisions(req: SystemOneRequest, arguments: dict) -> list[Decision]:
        decisions = []
        for q in req.questions:
            value = arguments[q.id]
            if q.type == "choice":
                decisions.append(
                    Decision(
                        id=q.id,
                        type=q.type,
                        answer=value["answer"],
                        probabilities=value.get("probabilities"),
                    )
                )
            elif q.type == "bool":
                decisions.append(
                    Decision(
                        id=q.id,
                        type=q.type,
                        answer=value["answer"],
                        score=value.get("probability_yes"),
                    )
                )
            else:
                decisions.append(
                    Decision(id=q.id, type=q.type, answer=value["answer"])
                )
        return decisions
