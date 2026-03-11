"""Top-level runner for the research automation agent.

Minimal, modular, and scheduled. Run `python agent.py --once` to execute one cycle.
"""
import argparse
import logging
import time
import schedule
import sys
import os
from pathlib import Path

# Ensure the workspace and `src` directory are on sys.path so imports below work
ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from src.agent import config
from src.agent import searcher, analyzer, latex_writer, emailer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("research_agent")


def run_once(topic: str):
    logger.info("Starting run for topic: %s", topic)
    results = searcher.search(topic)
    if not results:
        logger.info("No search results found for: %s", topic)

    findings = analyzer.analyze(results)

    latex = latex_writer.generate_latex(topic, findings)
    latex_writer.append_to_file(latex)

    # Small email summary: list high-priority titles
    high = [f for f in findings if f.get("priority") == "High"]
    summary_lines = [f"Research run for: {topic}", f"Total results: {len(results)}", "High priority:\n"]
    for h in high[:10]:
        summary_lines.append(f"- {h.get('title')} ({h.get('url')})")

    body = "\n".join(summary_lines)
    # send email but ignore failure
    sent = emailer.send_email(f"Research summary — {topic}", body)
    if not sent:
        logger.info("Email not sent; check configuration")

    logger.info("Run complete; LaTeX appended to %s", config.LATEX_FILE)


def schedule_loop(topic: str):
    logger.info("Scheduling job every 6 hours for topic: %s", topic)
    schedule.every(6).hours.do(run_once, topic=topic)
    # do an immediate run on start
    run_once(topic)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, default=config.DEFAULT_TOPIC)
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    args = parser.parse_args()

    topic = args.topic
    if args.once:
        run_once(topic)
    else:
        schedule_loop(topic)


if __name__ == "__main__":
    main()
