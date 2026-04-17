"""
memory.py — Logs every agent action and result to a JSON file.
Lets you review exactly what the agent did step by step.
"""

import json
import os
from datetime import datetime


class Memory:
    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"session_{timestamp}.json")
        self.entries = []
        self.task = ""

    def set_task(self, task: str):
        self.task = task
        self._save()

    def log_action(self, step: int, tool: str, inputs: dict, result: str):
        entry = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "inputs": inputs,
            "result": result[:500]  # cap result size
        }
        self.entries.append(entry)
        self._save()
        return entry

    def log_final(self, summary: str):
        self.entries.append({
            "step": "FINAL",
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        })
        self._save()

    def _save(self):
        data = {
            "task": self.task,
            "session_start": self.entries[0]["timestamp"] if self.entries else None,
            "total_steps": len(self.entries),
            "actions": self.entries
        }
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_log_path(self) -> str:
        return self.log_file