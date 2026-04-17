"""
tools.py — Tool definitions for Claude agent
Each tool maps to a browser action. Claude calls these autonomously.
"""

from browser.controller import BrowserController


# ── Tool Schemas (sent to Claude API) ──────────────────────────────────────────

TOOLS = [
    {
        "name": "goto_url",
        "description": "Navigate the browser to a specific URL. Use this to open websites.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL to navigate to, e.g. https://www.amazon.in"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "click_element",
        "description": "Click an element on the page using a CSS selector.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the element to click, e.g. '#add-to-cart-button'"}
            },
            "required": ["selector"]
        }
    },
    {
        "name": "click_text",
        "description": "Click an element that contains specific visible text. Use when you know the button/link text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Visible text of the element to click, e.g. 'Add to Cart'"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "type_text",
        "description": "Type text into an input field using a CSS selector.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector of the input field"},
                "text": {"type": "string", "description": "Text to type into the field"}
            },
            "required": ["selector", "text"]
        }
    },
    {
        "name": "press_key",
        "description": "Press a keyboard key. Useful for submitting forms with Enter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Key to press, e.g. 'Enter', 'Tab', 'Escape'"}
            },
            "required": ["key"]
        }
    },
    {
        "name": "scroll_down",
        "description": "Scroll down the page to see more content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "integer", "description": "Pixels to scroll down (default 600)", "default": 600}
            },
            "required": []
        }
    },
    {
        "name": "get_page_text",
        "description": "Get the readable text content of the current page. Use this to read product info, prices, search results, etc.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_links",
        "description": "Get all clickable links on the current page with their text and URLs.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_inputs",
        "description": "Get all input fields on the current page. Helps identify search boxes, forms, etc.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current browser state.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Filename for the screenshot (without path)", "default": "screenshot.png"}
            },
            "required": []
        }
    },
    {
        "name": "wait",
        "description": "Wait for a number of seconds. Useful after actions that take time to load.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {"type": "number", "description": "Seconds to wait", "default": 2}
            },
            "required": []
        }
    },
    {
        "name": "task_complete",
        "description": "Call this when you have fully completed the user's task. Provide a summary of what was accomplished.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Summary of what was accomplished"}
            },
            "required": ["summary"]
        }
    }
]


# ── Tool Executor ───────────────────────────────────────────────────────────────

class ToolExecutor:
    def __init__(self, browser: BrowserController):
        self.browser = browser
        self.done = False
        self.final_summary = ""

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool call and return the result as string."""
        b = self.browser

        if tool_name == "goto_url":
            title = b.goto(tool_input["url"])
            return f"Navigated to {tool_input['url']}. Page title: '{title}'. Current URL: {b.get_current_url()}"

        elif tool_name == "click_element":
            success = b.click(tool_input["selector"])
            return f"Click on '{tool_input['selector']}': {'success' if success else 'FAILED — element not found'}"

        elif tool_name == "click_text":
            success = b.click_text(tool_input["text"])
            return f"Click text '{tool_input['text']}': {'success' if success else 'FAILED — text not found on page'}"

        elif tool_name == "type_text":
            success = b.type_text(tool_input["selector"], tool_input["text"])
            return f"Typed '{tool_input['text']}' into '{tool_input['selector']}': {'success' if success else 'FAILED'}"

        elif tool_name == "press_key":
            b.press_key(tool_input["key"])
            return f"Pressed key: {tool_input['key']}"

        elif tool_name == "scroll_down":
            amount = tool_input.get("amount", 600)
            b.scroll_down(amount)
            return f"Scrolled down {amount}px"

        elif tool_name == "get_page_text":
            text = b.get_page_text()
            return f"PAGE TEXT:\n{text}"

        elif tool_name == "get_links":
            links = b.get_links()
            formatted = "\n".join([f"- {l['text'][:60]} → {l['href'][:80]}" for l in links])
            return f"LINKS ON PAGE:\n{formatted}"

        elif tool_name == "get_inputs":
            inputs = b.get_inputs()
            formatted = "\n".join([str(i) for i in inputs])
            return f"INPUT FIELDS:\n{formatted}"

        elif tool_name == "screenshot":
            filename = tool_input.get("filename", "screenshot.png")
            path = f"logs/{filename}"
            b.screenshot(path)
            return f"Screenshot saved to {path}"

        elif tool_name == "wait":
            seconds = tool_input.get("seconds", 2)
            b.wait(seconds)
            return f"Waited {seconds} seconds"

        elif tool_name == "task_complete":
            self.done = True
            self.final_summary = tool_input.get("summary", "Task completed.")
            return "TASK MARKED COMPLETE"

        else:
            return f"ERROR: Unknown tool '{tool_name}'"