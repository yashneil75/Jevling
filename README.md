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

### Changing the Model

You can switch models in two ways:

**Environment variables** (no code changes needed):

```bash
export JEVLING_MODEL_REPO="your-org/your-model-gguf"
export JEVLING_MODEL_FILE="your-model-Q4_K_M.gguf"
```

**Constructor parameters** (per-instance override):

```python
client = JevlingClient(
    repo_id="your-org/your-model-gguf",
    filename="your-model-Q4_K_M.gguf",
)
```

## License

MIT — Copyright (c) 2026 Yashneil Gajjala — see [LICENSE](LICENSE).
