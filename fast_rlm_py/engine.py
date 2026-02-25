"""Core RLM engine - pure Python implementation."""

import asyncio
import io
import json
import os
import sys
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from fast_rlm_py.llm_client import LLMClient, Usage
from fast_rlm_py.logger import Logger, set_log_dir, set_log_prefix, get_log_file
from fast_rlm_py.ui import show_python_ready, show_llm_query_call, show_global_usage, start_spinner
from fast_rlm_py.usage_tracker import UsageTracker


@dataclass
class RLMConfig:
    """Configuration for RLM execution."""
    primary_agent: str = "z-ai/glm-5"
    sub_agent: str = "minimax/minimax-m2.5"
    max_depth: int = 3
    max_calls_per_subagent: int = 20
    truncate_len: int = 2000
    max_money_spent: float = 1.0
    max_completion_tokens: int = 50000
    max_prompt_tokens: int = 200000

    @classmethod
    def default(cls) -> "RLMConfig":
        """Load default configuration from yaml file."""
        try:
            config_path = Path(__file__).parent.parent / "rlm_config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    data = yaml.safe_load(f) or {}
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            pass
        return cls()


def truncate_text(text: str, truncate_len: int) -> str:
    """Truncate text for display."""
    if len(text) > truncate_len:
        return f"[TRUNCATED: Last {truncate_len} chars shown].. " + text[-truncate_len:]
    elif len(text) == 0:
        return "[EMPTY OUTPUT]"
    else:
        return "[FULL OUTPUT SHOWN]... " + text


def now() -> str:
    """Get current timestamp."""
    return datetime.now().isoformat()


async def subagent(
    context: str,
    config: RLMConfig,
    usage_tracker: UsageTracker,
    llm_client: LLMClient,
    subagent_depth: int = 0,
    parent_run_id: Optional[str] = None
) -> Any:
    """Execute a single RLM subagent."""
    logger = Logger(subagent_depth, config.max_calls_per_subagent, parent_run_id)
    logger.log_agent_start()

    model_name = config.primary_agent if subagent_depth == 0 else config.sub_agent
    is_leaf_agent = subagent_depth >= config.max_depth

    # Python REPL state
    repl_globals: Dict[str, Any] = {}
    repl_locals: Dict[str, Any] = {}

    # Define llm_query function for this agent
    async def llm_query(query_context: str) -> Any:
        """Recursively query a sub-LLM."""
        if subagent_depth >= config.max_depth:
            raise RuntimeError(
                "MAXIMUM DEPTH REACHED. You must solve this task on your own without calling llm_query."
            )

        show_llm_query_call(subagent_depth)
        result = await subagent(
            query_context,
            config,
            usage_tracker,
            llm_client,
            subagent_depth + 1,
            logger.run_id
        )
        return result

    # Setup initial REPL environment
    setup_code = f"""
context = {json.dumps(context)}
__final_result__ = None
__final_result_set__ = False

def FINAL(x):
    global __final_result__, __final_result_set__
    __final_result__ = x
    __final_result_set__ = True

def FINAL_VAR(x):
    global __final_result__, __final_result_set__
    __final_result__ = x
    __final_result_set__ = True
"""

    # Initialize REPL
    exec(setup_code, repl_globals, repl_locals)

    # Inject llm_query into the REPL environment
    repl_globals['llm_query'] = llm_query
    repl_locals['llm_query'] = llm_query

    # Initial context exploration code
    initial_code = """
print("Context type: ", type(context))
print(f"Context length: {len(context) if hasattr(context, '__len__') else 'N/A'}")

if len(context) > 500:
    print(f"First 500 characters of str(context): ", str(context)[:500])
    print("---")
    print(f"Last 500 characters of str(context): ", str(context)[-500:])
else:
    print(f"Context: ", context)
"""

    # Execute initial code
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    step0_exec_start = now()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        try:
            exec(compile(initial_code, "<repl>", "exec"), repl_globals, repl_locals)
        except Exception as e:
            stdout_buffer.write(f"\nError: {e}\n")
    step0_exec_end = now()

    output = stdout_buffer.getvalue() + stderr_buffer.getvalue()
    messages = [{
        "role": "user",
        "content": f"""Outputs will always be truncated to last {config.truncate_len} characters.
code:\n```repl\n{initial_code}\n```\n
Output:\n{output.strip()}
"""
    }]

    # Log step 0
    no_usage = Usage()
    logger.log_step(
        step=0,
        code=initial_code,
        output=output.strip(),
        has_error=False,
        usage=no_usage,
        timestamps={
            "execution_start": step0_exec_start,
            "execution_end": step0_exec_end
        }
    )

    show_python_ready(subagent_depth)

    # Main execution loop
    for i in range(config.max_calls_per_subagent):
        llm_call_start = now()
        llm_spinner = start_spinner("Generating code...")

        code_result = llm_client.generate_code(messages, model_name, is_leaf_agent)
        llm_call_end = now()

        messages.append(code_result.message)

        # Track usage globally
        usage_tracker.track(code_result.usage)
        total_usage = usage_tracker.get_total()

        # Check budgets
        if total_usage.cost is not None and total_usage.cost > config.max_money_spent:
            raise RuntimeError(
                f"Budget exceeded: ${total_usage.cost:.4f} spent, limit is ${config.max_money_spent}"
            )
        if total_usage.completion_tokens > config.max_completion_tokens:
            raise RuntimeError(
                f"Completion token budget exceeded: {total_usage.completion_tokens:,} tokens used, "
                f"limit is {config.max_completion_tokens:,}"
            )
        if total_usage.prompt_tokens > config.max_prompt_tokens:
            raise RuntimeError(
                f"Prompt token budget exceeded: {total_usage.prompt_tokens:,} tokens used, "
                f"limit is {config.max_prompt_tokens:,}"
            )

        llm_spinner.success("Code generated")

        if not code_result.success:
            logger.log_step(
                step=i + 1,
                code=code_result.code,
                reasoning=code_result.message.get("reasoning"),
                usage=code_result.usage,
                timestamps={
                    "llm_call_start": llm_call_start,
                    "llm_call_end": llm_call_end
                }
            )
            messages.append({
                "role": "user",
                "content": "Error: We could not extract code because you may not have used repl block!"
            })
            continue

        # Execute the generated code
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        exec_start = now()
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            try:
                # Check if code contains await (needs async execution)
                if 'await ' in code_result.code:
                    # Wrap in async function for proper await support
                    async_code = f"""
async def __async_exec__():
{chr(10).join('    ' + line for line in code_result.code.splitlines())}

__async_result__ = __async_exec__()
"""
                    compiled_code = compile(async_code, "<repl>", "exec")
                    exec(compiled_code, repl_globals, repl_locals)
                    # Run the async function
                    async_result = repl_locals.get('__async_result__') or repl_globals.get('__async_result__')
                    if asyncio.iscoroutine(async_result):
                        await async_result
                else:
                    # Regular sync code
                    compiled_code = compile(code_result.code, "<repl>", "exec")
                    exec(compiled_code, repl_globals, repl_locals)
            except Exception as e:
                import traceback
                stdout_buffer.write(f"\nError: {traceback.format_exc()}")

        exec_end = now()

        output = stdout_buffer.getvalue() + stderr_buffer.getvalue()
        truncated_text = truncate_text(output, config.truncate_len)

        step_timestamps = {
            "llm_call_start": llm_call_start,
            "llm_call_end": llm_call_end,
            "execution_start": exec_start,
            "execution_end": exec_end
        }

        # Check if final result was set
        final_result_set = repl_locals.get("__final_result_set__") or repl_globals.get("__final_result_set__")
        if final_result_set:
            logger.log_step(
                step=i + 1,
                code=code_result.code,
                reasoning=code_result.message.get("reasoning"),
                usage=code_result.usage,
                timestamps=step_timestamps,
                total_usage=total_usage
            )

            result = repl_locals.get("__final_result__") or repl_globals.get("__final_result__")
            logger.log_final_result(result)
            logger.log_agent_end()
            return result

        has_error = "Error" in output or "Traceback" in output
        logger.log_step(
            step=i + 1,
            code=code_result.code,
            output=truncated_text,
            has_error=has_error,
            reasoning=code_result.message.get("reasoning"),
            usage=code_result.usage,
            timestamps=step_timestamps,
            total_usage=total_usage
        )

        messages.append({
            "role": "user",
            "content": f"Output: \n{truncated_text}"
        })

    logger.log_agent_end()
    raise RuntimeError("Did not finish the function stack before subagent died")


def run(
    query: str,
    config: Optional[RLMConfig] = None,
    prefix: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run a fast-rlm query (pure Python implementation).

    Args:
        query: The question / context to process.
        prefix: Optional log filename prefix.
        config: RLMConfig object with settings.
        verbose: If True, display output to terminal.

    Returns:
        Dict with 'results', 'usage', and 'log_file'.
    """
    if config is None:
        config = RLMConfig.default()

    if prefix:
        set_log_prefix(prefix)

    # Initialize global tracker and LLM client
    usage_tracker = UsageTracker()
    usage_tracker.reset()

    llm_client = LLMClient()

    result = None
    error = None

    try:
        # Run the main subagent
        result = asyncio.run(subagent(query, config, usage_tracker, llm_client))

        # Show global usage
        show_global_usage(usage_tracker.get_total())

        print(f"JSON_RESULT:{json.dumps({'results': result})}")

    except Exception as e:
        error = str(e)
        import traceback
        traceback.print_exc()
        raise

    finally:
        Logger.flush()

        log_file = get_log_file()
        if log_file:
            print(f"\n📝 Log saved to: {log_file}")
            print(f"   View with: fast-rlm-log {log_file} --tui")

        Logger.close()

    total_usage = usage_tracker.get_total()
    return {
        "results": result,
        "log_file": log_file,
        "usage": {
            "prompt_tokens": total_usage.prompt_tokens,
            "completion_tokens": total_usage.completion_tokens,
            "total_tokens": total_usage.total_tokens,
            "cached_tokens": total_usage.cached_tokens,
            "reasoning_tokens": total_usage.reasoning_tokens,
            "cost": total_usage.cost
        },
        **({"error": error} if error else {})
    }
