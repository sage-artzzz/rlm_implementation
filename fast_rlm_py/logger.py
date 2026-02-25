"""Logging system for RLM execution."""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fast_rlm_py.llm_client import Usage
from fast_rlm_py.ui import print_step, show_final_result


# Global state
_log_file: Optional[Path] = None
_log_prefix: Optional[str] = None
_log_dir: Path = Path("./logs")
_log_handle: Optional[Any] = None


def set_log_prefix(prefix: str) -> None:
    """Set custom prefix for log filename."""
    global _log_prefix
    _log_prefix = prefix


def set_log_dir(directory: str) -> None:
    """Set log directory path."""
    global _log_dir
    _log_dir = Path(directory)


def get_log_file() -> Optional[str]:
    """Get current log file path."""
    return str(_log_file) if _log_file else None


def _init_log_file() -> None:
    """Initialize log file if not already done."""
    global _log_file, _log_handle

    if _log_file is None:
        _log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
        prefix = f"{_log_prefix}_" if _log_prefix else "run_"
        _log_file = _log_dir / f"{prefix}{timestamp}.jsonl"

        _log_handle = open(_log_file, "w", buffering=1)  # Line buffered

        print(f"📝 Logging to: {_log_file}\n")


def _generate_run_id() -> str:
    """Generate unique run ID."""
    return f"{int(time.time() * 1000)}-{os.urandom(4).hex()}"


class Logger:
    """Logger for a single agent run."""

    def __init__(self, depth: int, max_steps: int, parent_run_id: Optional[str] = None):
        self.run_id = _generate_run_id()
        self.parent_run_id = parent_run_id
        self.depth = depth
        self.max_steps = max_steps

        _init_log_file()

    def _write_log(self, event_data: Dict[str, Any]) -> None:
        """Write a log entry to JSONL file."""
        log_entry = {
            "time": datetime.now().isoformat(),
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "depth": self.depth,
            **event_data
        }
        if _log_handle:
            _log_handle.write(json.dumps(log_entry) + "\n")
            _log_handle.flush()

    def log_agent_start(self) -> None:
        """Log agent start event."""
        self._write_log({"event_type": "agent_start"})

    def log_agent_end(self) -> None:
        """Log agent end event."""
        self._write_log({"event_type": "agent_end"})

    def log_step(
        self,
        step: int,
        code: str,
        output: Optional[str] = None,
        has_error: bool = False,
        reasoning: Optional[str] = None,
        usage: Optional[Usage] = None,
        timestamps: Optional[Dict[str, str]] = None,
        total_usage: Optional[Usage] = None
    ) -> None:
        """Log a single execution step."""
        event_data = {
            "step": step,
            "code": code,
        }

        if output is not None:
            event_data["event_type"] = "execution_result"
            event_data["output"] = output
            event_data["hasError"] = has_error
        else:
            event_data["event_type"] = "code_generated"

        if reasoning:
            event_data["reasoning"] = reasoning

        if usage:
            event_data["usage"] = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cached_tokens": usage.cached_tokens,
                "reasoning_tokens": usage.reasoning_tokens,
                "cost": usage.cost
            }

        if timestamps:
            event_data["timestamps"] = timestamps

        self._write_log(event_data)

        # Display on terminal
        print_step(
            depth=self.depth,
            step=step,
            max_steps=self.max_steps,
            code=code,
            output=output,
            has_error=has_error,
            usage=usage,
            total_usage=total_usage
        )

    def log_final_result(self, result: Any) -> None:
        """Log final result."""
        self._write_log({
            "event_type": "final_result",
            "result": result
        })

        # Display on terminal
        show_final_result(result, self.depth)

    @staticmethod
    def flush() -> None:
        """Flush log file."""
        if _log_handle:
            _log_handle.flush()

    @staticmethod
    def close() -> None:
        """Close log file."""
        global _log_handle
        if _log_handle:
            _log_handle.close()
            _log_handle = None
