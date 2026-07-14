# Research AI Agent 🧠

A complete, self-hosted FastAPI backend that acts as a personal AI research assistant. It automatically fetches daily AI research papers from Hugging Face, uses a LangGraph pipeline and open-source LLMs to analyze and summarize them, and tracks reading streaks for a 2-person network (you and your partner) using Expo Push Notifications.

Built using a **Django-style MVC architecture** inside FastAPI for maximum scalability and separation of concerns.

## ✨ Features

- **Daily Paper Analysis**: Automatically pulls a top daily AI paper from the Hugging Face Daily Papers API.
- **LangGraph Pipeline**: Processes the paper PDF via a robust 10-node AI pipeline (extracts sections, classifies them, and extracts the Title, Summary, Methods, Experiments, and Limitations).
- **Free Open Source LLMs**: Uses `Qwen/Qwen2.5-72B-Instruct` via the free Hugging Face Inference API. No paid OpenAI keys required!
- **Notion Sync (Optional)**: Automatically writes beautifully formatted research summaries directly to a Notion database.
- **Social Streak Tracking**: Tracks daily reading streaks for two users, with endpoints designed to show a side-by-side comparison on a mobile app dashboard.
- **Push Notifications**: Integrated with `apscheduler` and Expo Push to send daily reminders to mobile devices when a new paper is ready to read.

## 🏗️ Architecture (Django-Style MVC)

The project is structured like a Django project, where every feature is a self-contained "app" with its own models, schemas, and controllers.

```text
src/
├── core/            # Database config, scheduler setup, environment config
├── users/           # User management (seed users, Expo push tokens)
├── papers/          # Stateless app for fetching HF papers and triggering LangGraph
├── analysis/        # The LangGraph AI pipeline (16 files, 10 nodes)
├── reading/         # Tracks reading logs and daily streaks
└── notifications/   # APScheduler background worker and Expo Push logic
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer)

### 2. Setup

Clone the repository and install dependencies using `uv`:

```powershell
uv venv
.venv\Scripts\activate
uv sync
```

### 3. Environment Variables
Copy `.env.dev` to `.env` and fill in your keys:

```env
# Hugging Face (Free)
HF_TOKEN=hf_...
HF_MODEL=Qwen/Qwen2.5-72B-Instruct

# Notion (Optional)
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=...
```

### 4. Run the Server

Start the FastAPI server (this will automatically create the SQLite database and seed the two default users):

```powershell
uv run main.py
```

The server runs on `http://localhost:8000`. 
Interactive API documentation (Swagger) is available at `http://localhost:8000/docs`.

## 📡 Key API Endpoints

- `GET /api/papers/random` — Fetches a random highly-rated paper from Hugging Face's daily papers.
- `POST /api/papers/analyze` — Downloads a paper PDF, runs the AI LangGraph pipeline to analyze it, and syncs the summary to Notion.
- `GET /api/reading/streak/{user_id}` — Gets the current reading streak for a specific user.
- `POST /api/reading/{user_id}` — Logs a paper as read for today and updates the streak.
- `PUT /api/users/{user_id}/push-token` — Registers a mobile device's Expo push token for notifications.

## 🤖 LangGraph Pipeline Flow
```text
PDF → Markdown → Split Sections → Classify Sections → Fan-out (Title, Methods, Experiments, Limitations) → Summary → Assemble → Notion
```
