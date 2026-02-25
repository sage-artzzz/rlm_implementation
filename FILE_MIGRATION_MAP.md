# File Migration Map

## Where Did Everything Go?

If you're looking for code that was in the TypeScript files, here's where to find it now:

### TypeScript → Python Mapping

| Old File (TypeScript) | New File (Python) | Purpose |
|----------------------|-------------------|---------|
| `src/subagents.ts` | `fast_rlm_py/engine.py` | Main RLM engine, subagent logic |
| `src/call_llm.ts` | `fast_rlm_py/llm_client.py` | LLM API calls (OpenAI/OpenRouter) |
| `src/prompt.ts` | `fast_rlm_py/prompts.py` | System prompts for agents |
| `src/logging.ts` | `fast_rlm_py/logger.py` | JSONL logging system |
| `src/ui.ts` | `fast_rlm_py/ui.py` | Terminal UI (Rich instead of boxen) |
| `src/usage.ts` | `fast_rlm_py/usage_tracker.py` | Token usage tracking |
| `deno.json` | ❌ Removed | No longer needed (pure Python) |
| `deno.lock` | ❌ Removed | No longer needed (pure Python) |
| `test_counting_r.ts` | `test_counting_r.py` | Python version already existed |
| `fast_rlm.py` | `fast_rlm/_runner.py` | Merged into runner |

## Quick Reference

### Looking for the main agent loop?
**Was:** `src/subagents.ts` → `export async function subagent(...)`
**Now:** `fast_rlm_py/engine.py` → `async def subagent(...)`

### Looking for LLM API calls?
**Was:** `src/call_llm.ts` → `export async function generate_code(...)`
**Now:** `fast_rlm_py/llm_client.py` → `class LLMClient` → `def generate_code(...)`

### Looking for system prompts?
**Was:** `src/prompt.ts` → `export const SYSTEM_PROMPT = ...`
**Now:** `fast_rlm_py/prompts.py` → `SYSTEM_PROMPT = ...`

### Looking for logging?
**Was:** `src/logging.ts` → `export class Logger ...`
**Now:** `fast_rlm_py/logger.py` → `class Logger ...`

### Looking for terminal UI?
**Was:** `src/ui.ts` → `printStep()`, `boxen`, `chalk`
**Now:** `fast_rlm_py/ui.py` → `print_step()`, `rich.Panel`, `rich.Console`

### Looking for usage tracking?
**Was:** `src/usage.ts` → `trackUsage()`, `getTotalUsage()`
**Now:** `fast_rlm_py/usage_tracker.py` → `class UsageTracker`

## Key Differences

### 1. REPL Execution
**TypeScript/Deno:**
```typescript
const pyodide = await loadPyodide();
await pyodide.runPythonAsync(code);
```

**Pure Python:**
```python
exec(compile(code, "<repl>", "exec"), repl_globals, repl_locals)
```

### 2. UI Rendering
**TypeScript:**
```typescript
import boxen from "npm:boxen@8";
import chalk from "npm:chalk@5";
```

**Python:**
```python
from rich.console import Console
from rich.panel import Panel
```

### 3. Async Functions
**TypeScript:**
```typescript
pyodide.globals.set("llm_query", async (context) => {
    return await subagent(context, depth + 1);
});
```

**Python:**
```python
async def llm_query(context: str):
    return await subagent(context, config, depth + 1)

repl_globals['llm_query'] = llm_query
```

## Opening Files in IDE

If you're looking for specific functionality:

### 🔍 Want to modify agent behavior?
→ Open: `fast_rlm_py/engine.py`

### 🔍 Want to change LLM calls?
→ Open: `fast_rlm_py/llm_client.py`

### 🔍 Want to customize prompts?
→ Open: `fast_rlm_py/prompts.py`

### 🔍 Want to add logging?
→ Open: `fast_rlm_py/logger.py`

### 🔍 Want to customize UI?
→ Open: `fast_rlm_py/ui.py`

### 🔍 Want to add custom tools?
→ Open: `fast_rlm_py/engine.py` (around line 99, modify `repl_globals`)

## File Structure Comparison

### Before
```
fast-rlm/
├── src/               ← TypeScript source
│   ├── subagents.ts
│   ├── call_llm.ts
│   ├── prompt.ts
│   ├── logging.ts
│   ├── ui.ts
│   └── usage.ts
├── deno.json          ← Deno config
└── fast_rlm/
    └── _runner.py     ← Called Deno subprocess
```

### After
```
fast-rlm/
├── fast_rlm_py/       ← Pure Python implementation
│   ├── engine.py
│   ├── llm_client.py
│   ├── prompts.py
│   ├── logger.py
│   ├── ui.py
│   └── usage_tracker.py
└── fast_rlm/
    └── _runner.py     ← Uses fast_rlm_py directly
```

## No More Deno!

These commands **no longer work** (and aren't needed):
```bash
deno task test_counting_r      # ❌ Removed
deno task subagent              # ❌ Removed
deno run src/subagents.ts       # ❌ Removed
```

These commands **now work**:
```bash
python test_counting_r.py       # ✅ Uses Python backend
uv run python test_python_rlm.py  # ✅ Direct Python API
```

## API Compatibility

Both APIs work the same:

```python
# Option 1: Original API (uses Python backend now)
import fast_rlm
result = fast_rlm.run("query")

# Option 2: Direct Python API
import fast_rlm_py
result = fast_rlm_py.run("query")
```

## Need Help?

- **Full conversion details:** `PYTHON_IMPLEMENTATION.md`
- **Cleanup summary:** `CLEANUP_SUMMARY.md`
- **Migration status:** `MIGRATION_COMPLETE.md`
- **Python API docs:** `fast_rlm_py/README.md`
