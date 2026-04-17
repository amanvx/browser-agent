# 🤖 Browser Agent

An autonomous AI agent that controls a real browser — searches products, reads pages, clicks buttons, and completes tasks on its own.

Built with **Python + Playwright + Claude API**.

---

## 📁 Project Structure

```
browser-agent/
├── main.py                  ← Entry point (run this)
├── requirements.txt         ← Python dependencies
├── .env.example             ← Copy this to .env
│
├── agent/
│   └── agent.py             ← AI brain / main loop
│
├── browser/
│   └── controller.py        ← Playwright browser controller
│
├── tools/
│   └── tools.py             ← Tool definitions + executor
│
├── memory/
│   └── memory.py            ← Action logger (saves to logs/)
│
└── logs/                    ← Auto-created, session logs saved here
```

---

## ⚙️ Setup (Step by Step)

### 1. Prerequisites

Make sure you have:
- **Python 3.11+** → https://python.org
- **pip** (comes with Python)

Check:
```bash
python --version   # should be 3.11+
pip --version
```

---

### 2. Clone / Download the project

```bash
# If using git:
git clone <your-repo-url>
cd browser-agent

# Or just download and unzip, then:
cd browser-agent
```

---

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

---

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Install Playwright browsers

```bash
playwright install chromium
```

This downloads a real Chromium browser (~150MB). Only needed once.

---

### 6. Set up your API key

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key at: https://console.anthropic.com

---

### 7. Run the agent!

```bash
python main.py
```

You'll see a prompt — type your task and watch the browser go! 🚀

---

## 🎯 Example Tasks

### Interactive mode (just run and type):
```bash
python main.py
```

### Pass task directly:
```bash
python main.py --task "Search for wireless earbuds on Amazon India and show me the top 3 results with prices"

python main.py --task "Go to Flipkart, search for Nike shoes, and tell me the cheapest one"

python main.py --task "Search YouTube for 'Python tutorial for beginners' and list the top 5 videos"

python main.py --task "Go to Google and find the current weather in Mumbai"
```

### Run built-in examples:
```bash
python main.py --example 1   # Amazon product search
python main.py --example 2   # Flipkart shoes
python main.py --example 3   # Google + Amazon book search
python main.py --example 4   # YouTube search
python main.py --example 5   # Google weather
python main.py --example 6   # Flipkart laptop search
```

### Headless mode (no browser window, faster):
```bash
python main.py --headless --task "your task here"
```

### Limit steps (controls cost):
```bash
python main.py --max-steps 15 --task "your task here"
```

---

## 💰 API Cost Control

Each agent run uses the Claude API. Here's how to control costs:

| Setting | Effect |
|---|---|
| `--max-steps 10` | Cheaper, fewer actions |
| `--max-steps 25` | Default, handles complex tasks |
| Simple tasks | Cost ~$0.01–0.05 per run |
| Complex tasks | Cost ~$0.05–0.20 per run |

Tips:
- Start with simple tasks to test
- Use `--max-steps 10` for quick tests
- Check your usage at https://console.anthropic.com/usage

---

## 📋 Session Logs

Every run is automatically saved to `logs/session_YYYYMMDD_HHMMSS.json`.

Example log entry:
```json
{
  "task": "Search for earbuds on Amazon",
  "total_steps": 8,
  "actions": [
    {
      "step": 1,
      "tool": "goto_url",
      "inputs": {"url": "https://www.amazon.in"},
      "result": "Navigated to amazon.in. Page title: 'Amazon.in'"
    },
    ...
  ]
}
```

---

## 🛠️ Troubleshooting

**`playwright install` fails**
```bash
pip install playwright --upgrade
playwright install chromium
```

**Browser doesn't open**
- Make sure you're not in headless mode
- Try: `python main.py --task "go to google.com"`

**API key error**
- Check your `.env` file has `ANTHROPIC_API_KEY=sk-ant-...`
- Make sure there are no spaces around `=`

**Agent gets stuck**
- Lower max steps: `--max-steps 10`
- Try a simpler task first

**Import errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## 🔧 Customization

### Add a new website target

Edit `main.py` and add to `EXAMPLE_TASKS`:
```python
"Go to Meesho and search for 'saree under 500', list top 5 results"
```

### Add a new tool

In `tools/tools.py`, add to `TOOLS` list:
```python
{
    "name": "my_tool",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
}
```

Then add the execution logic in `ToolExecutor.execute()`.

### Change the AI model

In `agent/agent.py`, change the model:
```python
model="claude-haiku-4-5-20251001"   # cheaper, faster
model="claude-opus-4-5"             # smarter, more expensive (default)
```

---

## 🚀 What to Build Next

- **Price tracker** — monitor product prices over time
- **Auto-buyer** — add to cart + checkout automatically  
- **Research agent** — gather info from multiple sites into a report
- **Form filler** — fill and submit forms automatically
- **Job applier** — apply to jobs on LinkedIn/Naukri

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `anthropic` | Claude AI API |
| `playwright` | Browser control |
| `beautifulsoup4` | HTML parsing |
| `python-dotenv` | Load .env file |
| `rich` | Pretty terminal output |
