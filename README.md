# Zero-GPU Research Automation Agent

Small, minimalist research automation agent that:

- Searches the web (DuckDuckGo) for a topic.
- Analyzes findings (best-effort Groq API call, otherwise local heuristics).
- Appends a clean LaTeX summary to `research_log.tex`.
- Sends a short email summary using SMTP.
- Runs automatically every 6 hours (uses `schedule`).

Setup
1. Copy `.env.template` to `.env` and fill in `GROQ_API_KEY`, `EMAIL_USER`, and `EMAIL_PASS`.
2. (Optional) Configure `RESEARCH_TOPIC` in env or pass `--topic` on the command line.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

Run once:

```bash
python agent.py --once
```

Run in background (VS Code): Use the Command Palette -> Run Task -> "Run Research Agent (background)".

Notes
- The code attempts a best-effort HTTP call to a Groq endpoint if `GROQ_API_KEY` is set. If the SDK or endpoint differs, update `src/agent/analyzer.py::_call_groq_http` to match your Groq API.
- If Groq isn't available, the agent falls back to keyword heuristics so it remains functional without paid API calls.
