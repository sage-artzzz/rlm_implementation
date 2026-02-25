# Development from Source

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [Bun](https://bun.sh/) (optional - only for log viewer)

!!! info "No Deno Required"
    As of version 0.2.0, fast-rlm uses a pure Python implementation.
    **Deno is no longer required!**

## Setup

```bash
git clone https://github.com/avbiswas/fast-rlm.git
cd fast-rlm
```

### Install Python dependencies

=== "uv (recommended)"

    ```bash
    uv sync
    ```

=== "pip"

    ```bash
    pip install -e .
    ```

### (Optional) Install log viewer dependencies

```bash
cd tui_log_viewer && bun install && cd ..
```

### Set your API key

Create a `.env` file in the project root:

```
RLM_MODEL_API_KEY=sk-or-...
RLM_MODEL_BASE_URL=https://openrouter.ai/api/v1
```

Or use `.envrc` with [direnv](https://direnv.net/):

```bash
export RLM_MODEL_API_KEY=sk-or-...
export RLM_MODEL_BASE_URL=https://openrouter.ai/api/v1  # optional, this is the default
```

| Variable | Description | Default |
|----------|-------------|---------|
| `RLM_MODEL_API_KEY` | API key for your LLM provider | _(required)_ |
| `RLM_MODEL_BASE_URL` | OpenAI-compatible base URL | `https://openrouter.ai/api/v1` |

## Configuration

Edit `rlm_config.yaml` at the project root:

```yaml
max_calls_per_subagent: 20
max_depth: 3
truncate_len: 2000
primary_agent: "z-ai/glm-5"
sub_agent: "minimax/minimax-m2.5"
max_money_spent: 1.0
max_completion_tokens: 50000
max_prompt_tokens: 200000
```

## Running

```bash
# Run the counting-r example
python test_counting_r.py

# Or with uv
uv run python test_counting_r.py

# Run the pure Python test
python test_python_rlm.py

# View logs
./viewlog logs/<logfile>.jsonl
```

## Editable Python install

To develop the package locally:

```bash
# With uv (recommended)
uv sync

# With pip
pip install -e .
```

Changes to `fast_rlm/` and `fast_rlm_py/` are reflected immediately — no rebuild needed.

## Project structure

```
fast-rlm/
├── fast_rlm/              # Python package (original API)
│   ├── __init__.py        # Public API: run(), RLMConfig
│   ├── _runner.py         # Uses fast_rlm_py backend
│   └── _cli.py            # fast-rlm-log CLI entry point
├── fast_rlm_py/           # Pure Python implementation
│   ├── engine.py          # Core recursive agent loop
│   ├── llm_client.py      # LLM API client (OpenAI)
│   ├── prompts.py         # System prompts
│   ├── logger.py          # JSONL logger
│   ├── ui.py              # Terminal UI (Rich)
│   └── usage_tracker.py   # Token/cost tracking
├── tui_log_viewer/        # OpenTUI log viewer (Bun)
├── benchmarks/            # Evaluation scripts
├── examples/              # Usage examples
├── rlm_config.yaml        # Default agent configuration
└── pyproject.toml         # Python build config (hatchling)
```

## Running Benchmarks

```bash
# Install benchmark dependencies
uv sync --extra benchmarks

# Run LongBench
uv run python benchmarks/longbench_benchmark.py

# Run Oolong
uv run python benchmarks/oolong_synth_benchmark.py
```

## Testing

```bash
# Simple test
python test_counting_r.py

# Pure Python API test
python test_python_rlm.py

# With environment loaded
export $(cat .env | grep -v '^#' | xargs)
uv run python test_python_rlm.py
```

## Adding Custom Tools

It's easy to extend the Python implementation with custom tools:

```python
# Edit fast_rlm_py/engine.py, around line 99

# Add your custom tool
from elasticsearch import Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

def es_search(index: str, query: dict):
    return es.search(index=index, body=query)

# Inject into REPL environment
repl_globals['es_search'] = es_search
repl_locals['es_search'] = es_search

# Now agents can use: results = es_search("docs", {...})
```

## Migration from TypeScript

The TypeScript/Deno implementation has been migrated to pure Python:

| Old (TypeScript) | New (Python) |
|-----------------|--------------|
| `src/subagents.ts` | `fast_rlm_py/engine.py` |
| `src/call_llm.ts` | `fast_rlm_py/llm_client.py` |
| `src/prompt.ts` | `fast_rlm_py/prompts.py` |
| `src/logging.ts` | `fast_rlm_py/logger.py` |
| `src/ui.ts` | `fast_rlm_py/ui.py` |
| `src/usage.ts` | `fast_rlm_py/usage_tracker.py` |

See `FILE_MIGRATION_MAP.md` for detailed migration guide.
