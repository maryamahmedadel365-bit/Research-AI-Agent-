"""
Entry point. Thin on purpose — all real wiring lives in graph.py.
Usage: python main.py path/to/paper.pdf
"""

import sys

from dotenv import load_dotenv

load_dotenv()  # reads .env in the current directory and sets os.environ
# for you — this replaces the need for `export $(cat .env | xargs)`,
# which is a bash-only command and doesn't work on Windows/PowerShell.

from graph import build_graph
from state import initial_state


def run(pdf_path: str):
    app = build_graph()
    result = app.invoke(initial_state(pdf_path))

    if result.get("errors"):
        print("Completed with errors:")
        for err in result["errors"]:
            print(" -", err)
    else:
        print("Success. Notion page id:", result.get("notion_page_id"))

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py path/to/paper.pdf")
        sys.exit(1)
    run(sys.argv[1])