"""Global usage tracker across all subagents."""

from fast_rlm_py.llm_client import Usage


class UsageTracker:
    """Tracks token usage across all subagent calls."""

    def __init__(self):
        self.global_usage = Usage()

    def track(self, usage: Usage) -> None:
        """Add usage from a step to global totals."""
        self.global_usage.prompt_tokens += usage.prompt_tokens
        self.global_usage.completion_tokens += usage.completion_tokens
        self.global_usage.total_tokens += usage.total_tokens
        self.global_usage.cached_tokens += usage.cached_tokens
        self.global_usage.reasoning_tokens += usage.reasoning_tokens
        if usage.cost is not None:
            if self.global_usage.cost is None:
                self.global_usage.cost = 0.0
            self.global_usage.cost += usage.cost

    def get_total(self) -> Usage:
        """Get current global usage totals."""
        return Usage(
            prompt_tokens=self.global_usage.prompt_tokens,
            completion_tokens=self.global_usage.completion_tokens,
            total_tokens=self.global_usage.total_tokens,
            cached_tokens=self.global_usage.cached_tokens,
            reasoning_tokens=self.global_usage.reasoning_tokens,
            cost=self.global_usage.cost
        )

    def reset(self) -> None:
        """Reset global usage counters."""
        self.global_usage = Usage()
