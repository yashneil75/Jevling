# jevling

Local, Jev-compatible typed decisions backed by `llama-cpp-python`.

## Install

```bash
pip install -e .
```

## Usage

```python
from jevling import JevlingClient, Question, SystemOneRequest

client = JevlingClient()

req = SystemOneRequest(
    state={"ticket": "My order never arrived"},
    questions=[
        Question(
            id="department",
            type="choice",
            question="Which department should handle this?",
            options=["billing", "technical", "sales"],
        ),
        Question(id="urgent", type="bool", question="Is this urgent?"),
        Question(
            id="frustration",
            type="score",
            question="Frustration level",
            min=0,
            max=2,
        ),
    ],
)

response = client.decide(req)
print(response.model_dump_json(indent=2))
```

## Configuration

Model settings are in `jevling/config.py`:

- `MODEL_REPO` — Hugging Face repo ID
- `MODEL_FILE` — GGUF filename glob
- `n_gpu_layers=-1` — set to `0` for CPU-only inference

## License

MIT — Copyright (c) 2026 Yashneil Gajjala — see [LICENSE](LICENSE).
