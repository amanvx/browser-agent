"""
main.py — Entry point for Browser Agent
Usage:
    python main.py
    python main.py --task "Search for iPhone 15 on Flipkart and show me the price"
    python main.py --headless  (run without opening a visible browser window)
"""

import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Check API key
if not os.getenv("OPENROUTER_API_KEY"):
    print("❌ ERROR: OPENROUTER_API_KEY not set.")
    print("   1. Copy .env.example to .env")
    print("   2. Add your OpenRouter API key")
    sys.exit(1)

from agent.agent import BrowserAgent


# ── Example tasks you can try ───────────────────────────────────────────────────

EXAMPLE_TASKS = [
    "Search for 'wireless earbuds' on Amazon India (amazon.in) and tell me the top 3 results with their prices.",
    "Go to Flipkart, search for 'Nike shoes', filter by price and show me the cheapest option.",
    "Search for 'Python programming book' on Google and find the top result on Amazon.",
    "Go to YouTube and search for 'AI agents tutorial 2024', tell me the top 3 video titles.",
    "Go to google.com, search for 'weather in Mumbai today' and tell me the current temperature.",
    "Search for 'laptop under 50000' on Flipkart and list the top 5 results with prices.",
]


def main():
    parser = argparse.ArgumentParser(description="Browser Agent — AI that controls your browser")
    parser.add_argument("--task", type=str, help="Task for the agent to complete")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (no window)")
    parser.add_argument("--max-steps", type=int, default=25, help="Max steps before stopping (default: 25)")
    parser.add_argument("--example", type=int, help="Run example task by number (1-6)")
    args = parser.parse_args()

    # Pick task
    if args.task:
        task = args.task
    elif args.example:
        idx = args.example - 1
        if 0 <= idx < len(EXAMPLE_TASKS):
            task = EXAMPLE_TASKS[idx]
            print(f"Running example task {args.example}: {task}")
        else:
            print(f"Example number must be 1-{len(EXAMPLE_TASKS)}")
            sys.exit(1)
    else:
        # Interactive mode
        print("\n🤖 Browser Agent — Interactive Mode")
        print("=" * 50)
        print("\nExample tasks:")
        for i, t in enumerate(EXAMPLE_TASKS, 1):
            print(f"  {i}. {t}")
        print()
        user_input = input("Enter your task (or press Enter for example 1): ").strip()

        if not user_input:
            task = EXAMPLE_TASKS[0]
            print(f"Using: {task}")
        elif user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(EXAMPLE_TASKS):
                task = EXAMPLE_TASKS[idx]
                print(f"Using example {user_input}: {task}")
            else:
                print(f"Example number must be 1-{len(EXAMPLE_TASKS)}")
                sys.exit(1)
        else:
            task = user_input

    # Run agent
    agent = BrowserAgent(
        headless=args.headless,
        max_steps=args.max_steps
    )
    agent.run(task)


if __name__ == "__main__":
    main()