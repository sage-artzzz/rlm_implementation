"""Terminal UI for displaying agent execution."""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live

from fast_rlm_py.llm_client import Usage


console = Console()


def add_line_numbers(code: str) -> str:
    """Add line numbers to code."""
    lines = code.split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{str(i+1).rjust(width)} {line}" for i, line in enumerate(lines))


def print_step(
    depth: int,
    step: int,
    max_steps: int,
    code: str,
    output: Optional[str] = None,
    has_error: bool = False,
    usage: Optional[Usage] = None,
    total_usage: Optional[Usage] = None
) -> None:
    """Print a single execution step."""
    indent = "    │ " * depth

    # Header
    title = f" Depth {depth} · Step {step}/{max_steps} "
    header = "─" * 40 + title + "─" * 40
    console.print(f"{indent}[bold blue]{header}[/bold blue]")

    # Code panel
    if code:
        syntax = Syntax(add_line_numbers(code), "python", theme="monokai", line_numbers=False)
        panel = Panel(syntax, title="[blue]Python Code[/blue]", border_style="blue")
        if depth > 0:
            # For nested calls, add indent
            from io import StringIO
            temp_console = Console(file=StringIO(), force_terminal=True)
            temp_console.print(panel)
            panel_output = temp_console.file.getvalue()
            for line in panel_output.splitlines():
                console.print(f"{indent}{line}")
        else:
            console.print(panel)
    else:
        console.print(f"{indent}[yellow]No code generated. Stopping.[/yellow]")

    # Output panel
    if output is not None:
        color = "red" if has_error else "green"
        label = "Error" if has_error else "Result"
        text = Text(output, style=color if has_error else None)
        panel = Panel(text, title=f"[{color}]{label}[/{color}]", border_style=color)
        if depth > 0:
            from io import StringIO
            temp_console = Console(file=StringIO(), force_terminal=True)
            temp_console.print(panel)
            panel_output = temp_console.file.getvalue()
            for line in panel_output.splitlines():
                console.print(f"{indent}{line}")
        else:
            console.print(panel)

    # Usage panel
    if usage:
        usage_lines = []

        # Step usage
        step_parts = [
            f"[cyan]{usage.prompt_tokens:,}[/cyan] prompt",
            f"[cyan]{usage.completion_tokens:,}[/cyan] completion"
        ]
        if usage.cached_tokens > 0:
            step_parts.append(f"[yellow]{usage.cached_tokens:,}[/yellow] cached")
        if usage.reasoning_tokens > 0:
            step_parts.append(f"[magenta]{usage.reasoning_tokens:,}[/magenta] reasoning")

        cost_str = f"${usage.cost:.6f}" if usage.cost is not None else "Unknown"
        usage_lines.append(f"[bold]Step:[/bold]  {', '.join(step_parts)} | Cost: [green]{cost_str}[/green]")

        # Total usage
        if total_usage:
            total_parts = [
                f"[cyan]{total_usage.prompt_tokens:,}[/cyan] prompt",
                f"[cyan]{total_usage.completion_tokens:,}[/cyan] completion"
            ]
            if total_usage.cached_tokens > 0:
                total_parts.append(f"[yellow]{total_usage.cached_tokens:,}[/yellow] cached")
            if total_usage.reasoning_tokens > 0:
                total_parts.append(f"[magenta]{total_usage.reasoning_tokens:,}[/magenta] reasoning")

            total_cost_str = f"${total_usage.cost:.6f}" if total_usage.cost is not None else "Unknown"
            usage_lines.append(f"[bold]Total:[/bold] {', '.join(total_parts)} | Cost: [green]{total_cost_str}[/green]")

        panel = Panel("\n".join(usage_lines), title="[cyan]Usage[/cyan]", border_style="cyan")
        if depth > 0:
            from io import StringIO
            temp_console = Console(file=StringIO(), force_terminal=True)
            temp_console.print(panel)
            panel_output = temp_console.file.getvalue()
            for line in panel_output.splitlines():
                console.print(f"{indent}{line}")
        else:
            console.print(panel)


def show_python_ready(depth: int) -> None:
    """Show Python REPL is ready."""
    indent = "    │ " * depth
    console.print(f"{indent}[green bold]✔ Python Ready[/green bold]")


def show_llm_query_call(depth: int) -> None:
    """Show llm_query was called."""
    indent = "    │ " * depth
    console.print(f"{indent}[cyan bold]↳ llm_query called[/cyan bold]")


def show_final_result(result: any, depth: int) -> None:
    """Show final result."""
    indent = "    │ " * depth
    text = result if isinstance(result, str) else str(result)
    panel = Panel(
        Text(text, style="green"),
        title="[green bold]✔ Final Result[/green bold]",
        border_style="green",
        padding=(1, 1)
    )
    if depth > 0:
        from io import StringIO
        temp_console = Console(file=StringIO(), force_terminal=True)
        temp_console.print(panel)
        panel_output = temp_console.file.getvalue()
        for line in panel_output.splitlines():
            console.print(f"{indent}{line}")
    else:
        console.print(panel)


def show_global_usage(total_usage: Usage) -> None:
    """Show global usage statistics."""
    usage_parts = [
        f"[cyan]{total_usage.prompt_tokens:,}[/cyan] prompt",
        f"[cyan]{total_usage.completion_tokens:,}[/cyan] completion"
    ]

    if total_usage.cached_tokens > 0:
        usage_parts.append(f"[yellow]{total_usage.cached_tokens:,}[/yellow] cached")

    if total_usage.reasoning_tokens > 0:
        usage_parts.append(f"[magenta]{total_usage.reasoning_tokens:,}[/magenta] reasoning")

    cost_str = f"${total_usage.cost:.6f}" if total_usage.cost is not None else "Unknown"
    usage_text = ", ".join(usage_parts) + f" | Cost: [green]{cost_str}[/green]"

    panel = Panel(
        usage_text,
        title="[magenta bold]📊 Global Usage (All Runs)[/magenta bold]",
        border_style="magenta",
        padding=(0, 1)
    )
    console.print()
    console.print(panel)


class Spinner:
    """Simple spinner for long operations."""

    def __init__(self, text: str):
        self.text = text
        self.spinner = None
        self.live = None

    def start(self):
        """Start the spinner."""
        from rich.spinner import Spinner as RichSpinner
        self.spinner = RichSpinner("dots", text=self.text)
        self.live = Live(self.spinner, console=console, transient=True)
        self.live.start()
        return self

    def success(self, text: str):
        """Stop spinner with success message."""
        if self.live:
            self.live.stop()
        console.print(f"[green]✔[/green] {text}")

    def error(self, text: str):
        """Stop spinner with error message."""
        if self.live:
            self.live.stop()
        console.print(f"[red]✖[/red] {text}")


def start_spinner(text: str) -> Spinner:
    """Start a spinner for long operations."""
    return Spinner(text).start()
