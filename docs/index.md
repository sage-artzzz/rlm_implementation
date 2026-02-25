# fast-rlm

A minimal, **pure Python** implementation of Recursive Language Models (RLMs) for handling arbitrarily long context.

[![PyPI](https://img.shields.io/pypi/v/fast-rlm)](https://pypi.org/project/fast-rlm/)
[![GitHub](https://img.shields.io/github/stars/avbiswas/fast-rlm)](https://github.com/avbiswas/fast-rlm)

[GitHub](https://github.com/avbiswas/fast-rlm) | [PyPI](https://pypi.org/project/fast-rlm/) | [Paper](https://arxiv.org/abs/2512.24601)

!!! success "Pure Python (v0.2.0+)"
    fast-rlm now uses a pure Python implementation. **No Deno or external runtimes required!**

## What are RLMs?

RLMs are an inference technique where an LLM interacts with arbitrarily long prompts through an external REPL. The LLM can:

- Write code to explore, decompose, and transform the prompt
- Recursively invoke sub-agents to complete smaller subtasks
- Work with contexts far beyond any model's window (millions of tokens)

Crucially, sub-agent responses are not automatically loaded into the parent agent's context — they are returned as symbols or variables inside the parent's REPL.

## Quick Start

```bash
pip install fast-rlm
export RLM_MODEL_API_KEY=sk-or-...
```

```python
import fast_rlm

result = fast_rlm.run("Generate 50 fruits and count number of r")
print(result["results"])
```

## Key Features

- ✅ **Pure Python** - No external runtimes (Deno, Node, etc.)
- ✅ **Arbitrarily long context** - Process millions of tokens
- ✅ **Recursive subagents** - Decompose complex tasks
- ✅ **Budget controls** - Token and cost limits
- ✅ **JSONL logging** - Detailed execution traces
- ✅ **TUI log viewer** - Interactive debugging

## Example: Long Context

```python
import fast_rlm

transcripts = open("lex_fridman_all_transcripts.txt").read()  # millions of tokens

result = fast_rlm.run(
    "Summarize what the first 5 ML guests said about AGI.\n\n" + transcripts
)
print(result["results"])
```

The agent will automatically:
- Search and filter transcripts programmatically
- Chunk data intelligently
- Spawn sub-agents for parallel processing
- Aggregate results

No manual RAG pipeline needed!

## Architecture

```
User Query (arbitrarily long)
      ↓
Primary Agent (Python REPL)
      ├─→ Writes code to explore context
      ├─→ Spawns sub-agents recursively
      │   ├─→ Sub-agent 1 (processes chunk 1)
      │   ├─→ Sub-agent 2 (processes chunk 2)
      │   └─→ Sub-agent N (processes chunk N)
      └─→ Aggregates results → Final Answer
```

## Installation

See [Installation Guide](getting-started/installation.md)

## Configuration

```python
from fast_rlm import run, RLMConfig

config = RLMConfig.default()
config.primary_agent = "anthropic/claude-sonnet-4"
config.max_depth = 5
config.max_money_spent = 2.0

result = run("Your query", config=config)
```

See [Configuration](guide/configuration.md) for all options.

## Documentation

- [Getting Started](getting-started/installation.md)
- [Configuration](guide/configuration.md)
- [Best Practices](guide/tips.md)
- [Development](development/from-source.md)

## Implementation

fast-rlm is implemented in **pure Python**:

```
fast_rlm_py/
├── engine.py          # Core RLM loop
├── llm_client.py      # OpenAI API client
├── prompts.py         # System prompts
├── logger.py          # JSONL logging
├── ui.py              # Terminal UI (Rich)
└── usage_tracker.py   # Token tracking
```

- **Native Python execution** (faster than WASM)
- **Easy to extend** (add custom tools)
- **Simple deployment** (just `pip install`)
- **Standard debugging** (native Python traces)

## Paper

Based on the research paper: [arxiv.org/abs/2512.24601](https://arxiv.org/abs/2512.24601)

## Support

If you find this helpful, consider supporting on [Patreon](https://www.patreon.com/NeuralBreakdownwithAVB).

## License

MIT
