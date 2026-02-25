# How to Use fast-rlm - Complete Guide

## 🚀 Quick Start (2 Minutes)

### Step 1: Install

```bash
# Navigate to the repo
cd /home/sage/Documents/fast-rlm

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### Step 2: Set Your API Key

Your API key is already in `.env`:
```bash
# Check it's there
cat .env

# Load it into your environment
export $(cat .env | grep -v '^#' | xargs)
```

### Step 3: Run Your First Query

```python
# Create a file: my_first_query.py
import fast_rlm

result = fast_rlm.run("Count the letter 'r' in: apple, orange, strawberry")
print("Answer:", result["results"])
print("Cost:", result["usage"]["cost"])
```

Run it:
```bash
export $(cat .env | grep -v '^#' | xargs)
uv run python my_first_query.py
```

**That's it!** You just used an RLM agent. 🎉

---

## 📖 Understanding What Just Happened

When you ran the query, fast-rlm:

1. **Started a primary agent** with a Python REPL
2. **Agent wrote code** to count 'r' in each word:
   ```python
   words = ["apple", "orange", "strawberry"]
   result = {w: w.lower().count('r') for w in words}
   FINAL(result)
   ```
3. **Executed the code** natively in Python
4. **Returned the result** to you

Check the logs:
```bash
# List recent logs
ls -lt logs/ | head -5

# View the last log with the TUI (if you have bun installed)
./viewlog logs/$(ls -t logs/ | head -1)
```

---

## 🎯 Basic Examples

### Example 1: Simple Counting

```python
import fast_rlm

result = fast_rlm.run(
    "Generate 10 fruit names and count 'r' in each",
    prefix="fruit_count"  # Creates logs/fruit_count_*.jsonl
)
print(result["results"])
```

### Example 2: Long Context (RAG)

```python
import fast_rlm

# Load a large document
document = open("large_file.txt").read()  # Can be millions of tokens!

query = f"""
Find all mentions of "machine learning" in this document and summarize them.

# Document:
{document}
"""

result = fast_rlm.run(query, prefix="search_ml")
print(result["results"])
```

### Example 3: Using Sub-agents

```python
import fast_rlm

# This will automatically spawn sub-agents
query = """
Generate 3 lists:
- 20 fruits
- 20 animals
- 20 countries

For each item, count the letter 'e'.
Use parallel sub-agents for speed!
"""

result = fast_rlm.run(query, prefix="parallel_demo")
print(result["results"])
```

---

## ⚙️ Configuration

### Basic Configuration

```python
import fast_rlm

# Create config
config = fast_rlm.RLMConfig()
config.primary_agent = "anthropic/claude-sonnet-4"  # Use Claude
config.sub_agent = "minimax/minimax-m2.5"           # Use Minimax for sub-agents
config.max_depth = 4                                # Allow deeper recursion
config.max_money_spent = 0.50                       # Spend max $0.50

# Run with config
result = fast_rlm.run(
    "Your query here",
    config=config,
    prefix="my_task"
)
```

### All Configuration Options

```python
config = fast_rlm.RLMConfig()

# Models
config.primary_agent = "z-ai/glm-5"              # Root agent model
config.sub_agent = "minimax/minimax-m2.5"        # Sub-agent model

# Limits
config.max_depth = 3                             # Max recursion depth
config.max_calls_per_subagent = 20               # Max LLM calls per agent
config.max_money_spent = 1.0                     # Budget cap (USD)
config.max_completion_tokens = 50000             # Max completion tokens
config.max_prompt_tokens = 200000                # Max prompt tokens

# Display
config.truncate_len = 2000                       # Output chars shown per step
```

### Using Different Models

```python
# OpenAI
config.primary_agent = "openai/gpt-4"

# Anthropic
config.primary_agent = "anthropic/claude-sonnet-4"

# DeepSeek
config.primary_agent = "deepseek/deepseek-chat"

# Local models (via OpenRouter)
config.primary_agent = "meta-llama/llama-3.1-70b"
```

---

## 🔧 Advanced Usage

### Custom Configuration File

Edit `rlm_config.yaml`:
```yaml
primary_agent: "anthropic/claude-sonnet-4"
sub_agent: "minimax/minimax-m2.5"
max_depth: 4
max_calls_per_subagent: 30
max_money_spent: 2.0
```

Then use defaults:
```python
import fast_rlm

config = fast_rlm.RLMConfig.default()  # Loads from rlm_config.yaml
result = fast_rlm.run("Your query", config=config)
```

### Using Direct Python API

For more control, use the Python implementation directly:

```python
import fast_rlm_py

config = fast_rlm_py.RLMConfig()
config.primary_agent = "anthropic/claude-sonnet-4"

result = fast_rlm_py.run("Your query", config=config)
print(result["results"])
```

### Adding Custom Tools

Edit `fast_rlm_py/engine.py` around line 99:

```python
# Add custom functions to REPL
def search_database(query: str):
    # Your custom database search
    return results

repl_globals['search_database'] = search_database

# Now agents can use: results = search_database("term")
```

Example with Elasticsearch:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

def es_search(index: str, query: dict):
    results = es.search(index=index, body=query)
    return [hit['_source'] for hit in results['hits']['hits']]

repl_globals['es_search'] = es_search
repl_locals['es_search'] = es_search
```

---

## 📊 Examples in the Repo

### Run Existing Examples

```bash
# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Simple counting
uv run python test_counting_r.py

# Pure Python test
uv run python test_python_rlm.py

# Parallel execution
uv run python examples/parallel_r_count.py

# Podcast example (requires data)
# uv run python examples/podcast.py
```

### Run Benchmarks

```bash
# Install benchmark dependencies
uv sync --extra benchmarks

# Run LongBench benchmark
uv run python benchmarks/longbench_benchmark.py

# Run Oolong benchmark
uv run python benchmarks/oolong_synth_benchmark.py
```

---

## 📝 Viewing Logs

### Simple Log Viewer

```bash
# View last log (plain text)
fast-rlm-log logs/$(ls -t logs/ | head -1)
```

### TUI Log Viewer (Interactive)

```bash
# Install bun first (if not installed)
curl -fsSL https://bun.sh/install | bash

# Install viewer dependencies
cd tui_log_viewer && bun install && cd ..

# View with TUI
./viewlog logs/$(ls -t logs/ | head -1)

# Or
fast-rlm-log logs/your_log.jsonl --tui
```

---

## 💡 Use Cases

### 1. RAG Without Vector Databases

```python
# Traditional RAG: chunk, embed, store, retrieve, generate
# RLM RAG: just give it the whole document!

import fast_rlm

docs = open("all_documentation.txt").read()  # 1M+ tokens

result = fast_rlm.run(
    f"How do I configure authentication? Here are the docs:\n\n{docs}"
)
```

### 2. Complex Data Analysis

```python
import fast_rlm

data = open("sales_data.csv").read()

query = f"""
Analyze this sales data and find:
1. Top 5 products by revenue
2. Month-over-month growth trends
3. Geographic distribution of sales

Data:
{data}
"""

result = fast_rlm.run(query, prefix="sales_analysis")
```

### 3. Multi-Document Summarization

```python
import fast_rlm
from pathlib import Path

# Load all documents
docs = []
for file in Path("documents/").glob("*.txt"):
    docs.append(f"# {file.name}\n{file.read_text()}\n")

query = f"""
Summarize the key themes across all documents.

Documents:
{"".join(docs)}
"""

result = fast_rlm.run(query, prefix="multi_doc_summary")
```

---

## 🛠️ Development Workflow

### 1. Make Changes

```bash
# Edit Python code
code fast_rlm_py/engine.py

# Changes are immediately reflected (editable install)
```

### 2. Test Changes

```bash
# Quick test
export $(cat .env | grep -v '^#' | xargs)
uv run python -c "import fast_rlm; print(fast_rlm.run('test'))"

# Run existing tests
uv run python test_python_rlm.py
```

### 3. View Logs

```bash
# Check what the agent did
./viewlog logs/$(ls -t logs/ | head -1)
```

---

## 🔍 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'openai'"

**Solution:**
```bash
# Install dependencies
uv sync
# Or
pip install openai rich pyyaml
```

### Problem: "RLM_MODEL_API_KEY environment variable is missing"

**Solution:**
```bash
# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Or add to ~/.bashrc
echo 'export RLM_MODEL_API_KEY=sk-or-...' >> ~/.bashrc
```

### Problem: Agent runs but returns no result

**Solution:**
```bash
# Check the logs
cat logs/$(ls -t logs/ | head -1) | grep -i error

# Check if budget was exceeded
cat logs/$(ls -t logs/ | head -1) | grep -i budget

# Increase limits
config.max_calls_per_subagent = 30
config.max_money_spent = 2.0
```

### Problem: "Budget exceeded"

**Solution:**
```python
# Increase budget
config = fast_rlm.RLMConfig()
config.max_money_spent = 5.0  # Increase to $5
config.max_completion_tokens = 100000
```

---

## 📚 Next Steps

### Learn More

1. **Read the docs:**
   - `docs/getting-started/quickstart.md`
   - `docs/guide/configuration.md`
   - `docs/guide/tips.md`

2. **Check examples:**
   - `examples/parallel_r_count.py`
   - `examples/podcast.py`

3. **Read migration guides:**
   - `PYTHON_IMPLEMENTATION.md`
   - `FILE_MIGRATION_MAP.md`

### Get Help

- **Documentation:** [avbiswas.github.io/fast-rlm](https://avbiswas.github.io/fast-rlm/)
- **GitHub:** [github.com/avbiswas/fast-rlm](https://github.com/avbiswas/fast-rlm)
- **Issues:** [github.com/avbiswas/fast-rlm/issues](https://github.com/avbiswas/fast-rlm/issues)

---

## 🎯 Quick Reference

### Installation
```bash
uv sync  # or: pip install -e .
export $(cat .env | grep -v '^#' | xargs)
```

### Basic Usage
```python
import fast_rlm
result = fast_rlm.run("your query")
print(result["results"])
```

### With Config
```python
config = fast_rlm.RLMConfig()
config.primary_agent = "anthropic/claude-sonnet-4"
result = fast_rlm.run("query", config=config)
```

### View Logs
```bash
./viewlog logs/$(ls -t logs/ | head -1)
```

### Run Examples
```bash
export $(cat .env | grep -v '^#' | xargs)
uv run python test_python_rlm.py
```

---

**You're ready to use fast-rlm!** 🚀

Start with simple queries and gradually explore more complex use cases. The agent will surprise you with how well it handles long contexts and complex reasoning tasks.
