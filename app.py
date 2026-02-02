"""
Gradio App - Text Adventure AI Agent Assignment

A simple interface for the text adventure AI agent assignment.
"""

import gradio as gr

TITLE = "Playing Zork has never been so boring"

DESCRIPTION = """
Build AI agents to play classic text adventure games (Zork, Colossal Cave, Enchanter, etc.) using the Model Context Protocol (MCP) and HuggingFace models.

This project provides:
- **MCP Server** - Exposes text adventure games as MCP tools using FastMCP
- **ReAct Agent** - An agent that uses MCP tools to play games with reasoning
- **Submission Template** - Starter code for students to implement their own solutions
- **Evaluation System** - Deterministic evaluation with seeded runs
- **57 Games** - Zork trilogy, Infocom classics, and many more Z-machine games
"""

CLONE_INSTRUCTIONS = """
## Getting Started

### 1. Fork the Template Space

Fork the template Space on Hugging Face:
```
https://huggingface.co/spaces/LLM-course/text-adventure-template
```

### 2. Clone Your Fork Locally

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/text-adventure-agent
cd text-adventure-agent
```

### 3. Implement Your Agent

Edit these files:
- `agent.py` - Your ReAct agent implementation (implement the `StudentAgent` class)
- `mcp_server.py` - Your MCP server implementation (add tools like `play_action`, `memory`, etc.)

### 4. Test Locally

```bash
# Test MCP server interactively
fastmcp dev mcp_server.py

# Run your agent
python run_agent.py --agent . --game lostpig -v -n 20
```

### 5. Push and Submit

```bash
git add -A
git commit -m "Implement my agent"
git push
```

Then submit your Space URL on the course platform.
"""

demo = gr.Blocks(title=TITLE)

with demo:
    gr.Markdown(f"# {TITLE}")
    gr.Markdown(DESCRIPTION)
    gr.Markdown("---")
    gr.Markdown(CLONE_INSTRUCTIONS)

if __name__ == "__main__":
    demo.launch()
