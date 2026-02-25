# fast-rlm-py: Pure Python Implementation

This is a **pure Python** implementation of Recursive Language Models (RLMs), converted from the original TypeScript/Deno version.

## Key Differences from Original

| Feature | Original (TypeScript/Deno) | Pure Python |
|---------|---------------------------|-------------|
| **Runtime** | Deno + Pyodide (WASM) | Native Python |
| **Dependencies** | Deno, npm packages | OpenAI, Rich, PyYAML |
| **REPL** | Pyodide (Python in WebAssembly) | Native Python `exec()` |
| **Performance** | Slower (WASM overhead) | Faster (native execution) |
| **Installation** | Requires Deno installation | Pure Python, no external runtime |

## Advantages

✅ **No Deno required** - Pure Python, works anywhere Python runs
✅ **Faster execution** - Native Python instead of WASM
✅ **Easier to extend** - Add custom tools/functions directly in Python
✅ **Better debugging** - Standard Python stack traces
✅ **Simpler deployment** - Just `pip install`, no Deno setup

## Usage

```python
import fast_rlm_py

# Simple query
result = fast_rlm_py.run("Generate 10 fruits and count 'r' in each")
print(result["results"])

# With configuration
config = fast_rlm_py.RLMConfig()
config.primary_agent = "anthropic/claude-sonnet-4"
config.max_depth = 4
config.max_money_spent = 2.0

result = fast_rlm_py.run(
    "Summarize these documents...",
    config=config,
    prefix="my_task"
)
```

## Architecture

```
fast_rlm_py/
├── __init__.py          # Public API
├── engine.py            # Main RLM engine (replaces subagents.ts)
├── llm_client.py        # LLM API calls (replaces call_llm.ts)
├── prompts.py           # System prompts (replaces prompt.ts)
├── logger.py            # JSONL logging (replaces logging.ts)
├── ui.py                # Terminal UI with Rich (replaces ui.ts)
└── usage_tracker.py     # Token tracking (replaces usage.ts)
```

## Adding Custom Tools

It's much easier to add custom tools in pure Python:

```python
# In engine.py, modify the repl_globals dict:

# Add Elasticsearch
from elasticsearch import Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

def es_search(index: str, query: dict) -> list:
    results = es.search(index=index, body=query)
    return [hit['_source'] for hit in results['hits']['hits']]

repl_globals['es_search'] = es_search

# Now agents can use: results = es_search("docs", {"match": {"title": "AI"}})
```

## Migration from Original

If you're using the original TypeScript version, switching is easy:

```python
# Before (TypeScript version)
import fast_rlm
result = fast_rlm.run("query")

# After (Pure Python version)
import fast_rlm_py
result = fast_rlm_py.run("query")  # Same API!
```

## Requirements

- Python 3.10+
- `openai>=1.0.0`
- `rich>=13.0.0`
- `pyyaml>=6.0`

## Installation

```bash
pip install -e .  # Install from source
```

## Environment Variables

Same as the original:

```bash
export RLM_MODEL_API_KEY=sk-or-your-key-here
export RLM_MODEL_BASE_URL=https://openrouter.ai/api/v1  # optional
```

## Testing

```bash
python test_python_rlm.py
```

## Comparison

**When to use Pure Python version:**
- You want simpler setup (no Deno)
- You need to add custom Python tools
- You want faster execution
- You're deploying in Python-only environments

**When to use Original TypeScript version:**
- You already have Deno installed
- You need maximum sandboxing (Pyodide WASM isolation)
- You're using the official published package

## Status

✅ Complete feature parity with original
✅ All core functionality implemented
✅ Same API and configuration
✅ Compatible log format
