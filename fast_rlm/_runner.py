"""
fast-rlm runner - now using pure Python implementation.

This module provides the original fast_rlm API but uses the pure Python
implementation (fast_rlm_py) instead of Deno/TypeScript.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict

import yaml

# Import the pure Python implementation
import fast_rlm_py


@dataclass
class RLMConfig:
    """Configuration for fast-rlm."""

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
        """Load defaults from bundled rlm_config.yaml."""
        try:
            config_path = Path(__file__).parent.parent / "rlm_config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    data = yaml.safe_load(f) or {}
                return cls(
                    **{k: v for k, v in data.items() if k in cls.__dataclass_fields__}
                )
        except Exception:
            pass
        return cls()

    def to_py_config(self) -> fast_rlm_py.RLMConfig:
        """Convert to Python implementation config."""
        return fast_rlm_py.RLMConfig(
            primary_agent=self.primary_agent,
            sub_agent=self.sub_agent,
            max_depth=self.max_depth,
            max_calls_per_subagent=self.max_calls_per_subagent,
            truncate_len=self.truncate_len,
            max_money_spent=self.max_money_spent,
            max_completion_tokens=self.max_completion_tokens,
            max_prompt_tokens=self.max_prompt_tokens
        )


def run(
    query: str,
    prefix: Optional[str] = None,
    config: Optional[RLMConfig | dict] = None,
    verbose: bool = True,
) -> Dict:
    """
    Run a fast-rlm query using pure Python implementation.

    Args:
        query: The question / context to process.
        prefix: Optional log filename prefix.
        config: RLMConfig object or dict of overrides (e.g. primary_agent, max_depth).
        verbose: If True, stream output to terminal.

    Returns:
        Dict with 'results', 'usage', and optionally 'log_file'.
    """
    # Convert config
    if config is None:
        py_config = fast_rlm_py.RLMConfig.default()
    elif isinstance(config, dict):
        # Load defaults first
        default_config = RLMConfig.default()
        # Merge with overrides
        for key, value in config.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)
        py_config = default_config.to_py_config()
    else:
        py_config = config.to_py_config()

    # Call pure Python implementation
    return fast_rlm_py.run(query, config=py_config, prefix=prefix, verbose=verbose)
