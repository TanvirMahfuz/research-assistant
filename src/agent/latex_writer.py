"""Generate LaTeX summaries and append them to a research_log.tex file."""
from datetime import datetime
from typing import List, Dict
import logging
from . import config

logger = logging.getLogger(__name__)


LATEX_HEADER = r"""
% Automatically generated research log
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\begin{document}
\section*{Research Log}
"""

LATEX_FOOTER = r"""
\end{document}
"""


def ensure_file():
    """Create the LaTeX file with a header if it doesn't exist."""
    path = config.LATEX_FILE
    if not path.exists():
        path.write_text(LATEX_HEADER + "\n" + LATEX_FOOTER)


def generate_latex(topic: str, findings: List[Dict]) -> str:
    """Return a LaTeX string summarizing findings grouped by priority.

    findings: list of {title, url, summary, priority}
    """
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    high = [f for f in findings if f.get("priority") == "High"]
    low = [f for f in findings if f.get("priority") != "High"]

    lines = []
    lines.append(f"\\subsection*{{{ts} --- {topic}}}")

    def render_list(items):
        if not items:
            return "\\textit{No items found}.\\\n"
        parts = ["\\begin{itemize}"]
        for it in items:
            title = it.get("title", "(no title)")
            url = it.get("url", "")
            summary = it.get("summary", "")
            safe_title = title.replace("%", "\\%").replace("_", "\\_")
            safe_summary = summary.replace("%", "\\%").replace("_", "\\_")
            parts.append(f"\\item \\textbf{{{safe_title}}} --- {safe_summary} \\newline \\url{{{url}}}")
        parts.append("\\end{itemize}")
        return "\n".join(parts) + "\n"

    lines.append("\\paragraph{High Priority}")
    lines.append(render_list(high))

    lines.append("\\paragraph{Low Priority}")
    lines.append(render_list(low))

    return "\n".join(lines)


def append_to_file(latex_snippet: str):
    path = config.LATEX_FILE
    ensure_file()
    # Insert the snippet before the \end{document}
    content = path.read_text()
    if "\\end{document}" in content:
        content = content.replace("\\end{document}", latex_snippet + "\\n\\end{document}")
    else:
        content = content + "\n" + latex_snippet
    path.write_text(content)
    logger.info("Appended LaTeX to %s", path)
