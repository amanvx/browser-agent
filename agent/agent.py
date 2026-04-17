"""
agent.py — The AI brain loop.
Sends task to OpenRouter, receives tool calls, executes them, feeds results back.
Loops until task_complete or max steps reached.
"""

import json
import os

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from browser.controller import BrowserController
from tools.tools import TOOLS, ToolExecutor
from memory.memory import Memory

console = Console()

SYSTEM_PROMPT = """You are an autonomous browser agent. You control a real web browser to complete tasks for the user.

You have tools to:
- Navigate to URLs
- Click buttons and links (by CSS selector or visible text)
- Type into input fields
- Scroll pages
- Read page content, links, and input fields
- Take screenshots
- Wait for pages to load

IMPORTANT RULES:
1. Always start by navigating to the right website.
2. After navigating or clicking, use get_page_text or get_links to understand what's on the page before acting.
3. For search boxes, first use get_inputs to find the correct selector, then use type_text.
4. Common search box selectors: input[type='search'], input[name='q'], #twotabsearchtextbox (Amazon), input[name='search_query'] (YouTube).
5. If a click fails by selector, try click_text with the button's visible text instead.
6. After adding to cart or completing a major step, use get_page_text to confirm it worked.
7. Be patient — use wait() after page loads if needed.
8. When the task is fully done, call task_complete with a clear summary.
9. If something fails 2 times in a row, try a different approach.
10. Never give up — try alternative selectors, scroll to find elements, or navigate differently.

Think step by step. Always read the page before acting on it."""


class BrowserAgent:
    def __init__(self, headless: bool = False, max_steps: int = 30):
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            default_headers={
                "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
                "X-Title": os.getenv("OPENROUTER_APP_NAME", "browser-agent"),
            },
        )
        self.headless = headless
        self.max_steps = max_steps
        self.browser = BrowserController(headless=headless)
        self.memory = Memory()

    def run(self, task: str):
        """Run the agent on a task."""
        console.print(Panel(f"[bold cyan]TASK:[/bold cyan] {task}", title="🤖 Browser Agent", border_style="cyan"))
        self.memory.set_task(task)

        # Start browser
        self.browser.start()
        executor = ToolExecutor(self.browser)

        # Conversation history (OpenAI-style)
        messages = [{"role": "user", "content": task}]
        openai_tools = convert_tools_to_openai(TOOLS)

        step = 0

        try:
            while step < self.max_steps and not executor.done:
                step += 1
                console.print(f"\n[dim]━━━ Step {step} ━━━[/dim]")

                # Call OpenRouter
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
                    tools=openai_tools,
                    tool_choice="auto",
                )
                msg = response.choices[0].message

                # Print any assistant text
                if msg.content:
                    console.print(f"[yellow]Agent:[/yellow] {msg.content}")

                # Process tool calls
                tool_results = []

                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            tool_input = json.loads(tool_call.function.arguments or "{}")
                        except json.JSONDecodeError:
                            tool_input = {}

                        console.print(
                            f"[green]→ Tool:[/green] [bold]{tool_name}[/bold] "
                            f"[dim]{json_preview(tool_input)}[/dim]"
                        )

                        # Execute tool
                        result = executor.execute(tool_name, tool_input)

                        # Log to memory
                        self.memory.log_action(step, tool_name, tool_input, result)

                        # Show result preview
                        preview = result[:200] + "..." if len(result) > 200 else result
                        console.print(f"[dim]  ↳ {preview}[/dim]")

                        tool_results.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        })

                    # Include assistant tool-call message before tool results
                    messages.append({
                        "role": "assistant",
                        "content": msg.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in msg.tool_calls
                        ],
                    })
                else:
                    # No tools requested; assistant gave final text
                    messages.append({"role": "assistant", "content": msg.content or ""})
                    break

                # Feed results back to Claude
                if tool_results:
                    messages.extend(tool_results)

                # Check if done
                if executor.done:
                    break

            # Final output
            if executor.done:
                self.memory.log_final(executor.final_summary)
                console.print(Panel(
                    f"[bold green]✅ TASK COMPLETE[/bold green]\n\n{executor.final_summary}",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[bold yellow]⚠️ Reached max steps ({self.max_steps}) without completing task.[/bold yellow]",
                    border_style="yellow"
                ))

        except KeyboardInterrupt:
            console.print("\n[red]Interrupted by user.[/red]")

        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            raise

        finally:
            console.print(f"\n[dim]Session log saved: {self.memory.get_log_path()}[/dim]")
            self.browser.stop()

        return executor.final_summary


def json_preview(d: dict) -> str:
    """Short preview of tool inputs."""
    parts = []
    for k, v in d.items():
        v_str = str(v)[:40]
        parts.append(f"{k}={v_str!r}")
    return "(" + ", ".join(parts) + ")"


def convert_tools_to_openai(tools: list[dict]) -> list[dict]:
    """Convert Anthropic-style tool definitions to OpenAI-style function tools."""
    converted = []
    for tool in tools:
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
                },
            }
        )
    return converted