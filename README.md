# Research AI Agent

A LangGraph pipeline that processes research paper PDFs, extracts structured fields, and writes them to a Notion database.

## Pipeline

```text
PDF → Markdown → Split Sections → Classify Sections → Fan-out (Title, Methods, Experiments, Limitations) → Summary → Assemble → Notion
```

## Setup

```powershell
uv venv
.venv\Scripts\activate
uv sync
```

Copy `.env.dev` to `.env` and fill in your keys:

```env
OPENAI_API_KEY=sk-...
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=...
```

## Usage

```powershell
python main.py path/to/paper.pdf
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `converters/` | PDF → Markdown (PyMuPDF) |
| `splitters/` | Markdown → sections by heading |
| `classifiers/` | Map sections to categories (method/experiment/etc.) |
| `extractors/` | Extract individual fields using LLM calls |
| `assembler/` | Combine fields into a structured `PaperSummary` |
| `sinks/` | Write to Notion |
| `nodes/` | LangGraph node wrappers |
| `schemas.py` | Output data model (`PaperSummary`) |
