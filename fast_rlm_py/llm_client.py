"""LLM API client for generating code."""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI

from fast_rlm_py.prompts import SYSTEM_PROMPT, LEAF_AGENT_SYSTEM_PROMPT


@dataclass
class Usage:
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost: Optional[float] = None


@dataclass
class CodeReturn:
    """Return value from LLM code generation."""
    code: str
    success: bool
    message: Dict[str, Any]
    usage: Usage


class LLMClient:
    """Client for calling LLM APIs to generate code."""

    def __init__(self):
        api_key = os.getenv("RLM_MODEL_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("RLM_MODEL_BASE_URL") or "https://openrouter.ai/api/v1"

        if not api_key:
            raise RuntimeError(
                "RLM_MODEL_API_KEY environment variable is missing or empty. "
                "Set it to your API key, e.g.: export RLM_MODEL_API_KEY='sk-...'"
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_code(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        is_leaf_agent: bool = False
    ) -> CodeReturn:
        """Generate code from LLM given message history."""
        system_prompt = LEAF_AGENT_SYSTEM_PROMPT if is_leaf_agent else SYSTEM_PROMPT

        completion = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ]
        )

        content = completion.choices[0].message.content or ""

        # Extract code from ```repl ... ``` blocks
        repl_matches = re.findall(r'```repl([\s\S]*?)```', content)
        code = "\n".join(m.strip() for m in repl_matches)

        # Extract usage
        usage_data = completion.usage
        usage = Usage(
            prompt_tokens=usage_data.prompt_tokens,
            completion_tokens=usage_data.completion_tokens,
            total_tokens=usage_data.total_tokens,
            cached_tokens=getattr(getattr(usage_data, 'prompt_tokens_details', None), 'cached_tokens', 0) or 0,
            reasoning_tokens=getattr(getattr(usage_data, 'completion_tokens_details', None), 'reasoning_tokens', 0) or 0,
            cost=getattr(usage_data, 'cost', None)
        )

        message = {
            "role": "assistant",
            "content": content,
            "reasoning": getattr(completion.choices[0].message, 'reasoning', None)
        }

        if not code:
            return CodeReturn(
                code="",
                success=False,
                message=message,
                usage=usage
            )

        return CodeReturn(
            code=code,
            success=True,
            message=message,
            usage=usage
        )
