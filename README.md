# 🔍 Text-to-SQL Agent

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)

**Convert natural language questions into SQL queries and visualize results instantly using AI.**

[Live Demo](https://text-to-sql-frontend.onrender.com) · [API Docs](https://text-to-sql-backend.onrender.com/docs) · [Report Bug](https://github.com/pranotosh2/text-to-sql-agent/issues)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Running with Docker](#-running-with-docker)
- [Running Locally](#-running-locally-without-docker)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#-deployment-on-render)
- [Screenshots](#-screenshots)
- [Author](#-author)

---

## 🧠 Overview

**Text-to-SQL Agent** is a production-ready AI application that allows users to query a PostgreSQL database using plain English. The system uses a **LangChain ReAct agent** powered by **Groq's LLaMA3-70b** model to introspect the live database schema, generate validated SQL, execute queries, and return results through an interactive Streamlit dashboard.

> **Example:** Type *"Show top 10 customers by total order value"* → The agent reads the schema, writes the SQL, executes it, and displays a table + chart — no SQL knowledge required.

---

## 🏗 Architecture

```
User (Browser)
     │
     ▼
┌─────────────────┐
│  Streamlit UI   │  ← Ask questions, view results, edit SQL, download CSV
│  (Port 8501)    │
└────────┬────────┘
         │ POST /query
         ▼
┌─────────────────┐
│   FastAPI       │  ← REST API with /query, /execute, /schema, /health
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         LangChain ReAct Agent           │
│                                         │
│  Tool 1: get_schema                     │
│  └─ Reads live schema from PostgreSQL   │
│                                         │
│  Tool 2: generate_sql                   │
│  └─ Groq LLaMA3-70b writes SELECT SQL  │
│                                         │
│  Tool 3: execute_sql                    │
│  └─ Validates + runs query safely       │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ← Northwind sample database (orders, customers, products)
│  (Port 5432)    │
└─────────────────┘

All services run inside Docker Compose.
GitHub Actions handles CI/CD → Docker Hub → Render.
```

---

## ✨ Features

- 🗣 **Natural Language to SQL** — Ask any question in plain English
- 🔍 **Schema-Aware Prompting** — Agent reads live database schema at query time; works on any PostgreSQL database without code changes
- 🛡 **SQL Validation Layer** — Blocks `DROP`, `DELETE`, `TRUNCATE`, `INSERT`, `UPDATE` — only `SELECT` allowed
- ✏️ **Editable SQL** — View, edit, and re-run the generated SQL directly in the UI
- 📊 **Auto Visualization** — Bar, Line, and Scatter charts generated automatically from results
- ⬇️ **Export** — Download results as CSV or the generated SQL as a `.sql` file
- 🐳 **Fully Dockerized** — One command to run all three services
- ⚙️ **CI/CD Pipeline** — GitHub Actions: test → build → push to Docker Hub → deploy to Render
- 🚀 **Production Ready** — FastAPI with health checks, CORS middleware, and error handling

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Matplotlib |
| Backend | FastAPI, Uvicorn |
| AI Agent | LangChain, Groq (LLaMA3-70b) |
| Database | PostgreSQL 15, SQLAlchemy |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |

---

## 📁 Project Structure

```
text-to-sql-agent/
├── backend/
│   ├── main.py              # FastAPI app — /query, /execute, /schema, /health
│   ├── agent.py             # LangChain ReAct agent with 3 tools
│   ├── database.py          # PostgreSQL connection, schema reader, SQL executor
│   ├── northwind.sql        # Sample database seed (auto-loaded by Docker)
│   ├── requirements.txt
│   └── tests/
│       └── test_api.py      # Pytest test suite
├── frontend/
│   ├── app.py               # Streamlit dashboard
│   └── requirements.txt
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── .env.example             # Environment variable template
├── .gitignore
└── .github/
    └── workflows/
        └── ci.yml           # GitHub Actions CI/CD pipeline
```

---

## 🚀 Getting Started

### Prerequisites

- [Anaconda / Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/)
- **Groq API Key** (free) — [console.groq.com](https://console.groq.com)

### Clone the repository

```bash
git clone https://github.com/pranotosh2/text-to-sql-agent.git
cd text-to-sql-agent
```

### Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=postgresql://postgres:postgres@db:5432/northwind
```

---

## 🐳 Running with Docker

The easiest way — runs all three services (PostgreSQL, FastAPI, Streamlit) together.

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Streamlit UI | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

**Stop the project:**
```bash
docker-compose down
```

**Reset everything (including database):**
```bash
docker-compose down -v
```

---

## 💻 Running Locally (Without Docker)

**Step 1 — Create and activate conda environment:**
```bash
conda create -n text2sql python=3.11 -y
conda activate text2sql
```

**Step 2 — Start PostgreSQL (Docker for DB only):**
```bash
docker run -d --name northwind_db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=northwind \
  -p 5432:5432 postgres:15

docker exec -i northwind_db psql -U postgres -d northwind < backend/northwind.sql
```

**Step 3 — Start the backend (Terminal 1):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Step 4 — Start the frontend (Terminal 2):**
```bash
cd frontend
pip install -r requirements.txt
# Change API_URL in app.py to http://localhost:8000 first
python -m streamlit run app.py
```

---

## 🔐 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `GROQ_API_KEY` | Groq API key for LLaMA3-70b | `gsk_xxx...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/northwind` |

> ⚠️ Never commit your `.env` file. It is already in `.gitignore`.

---

## 📡 API Reference

### `GET /health`
Returns service health status.
```json
{ "status": "ok", "service": "text-to-sql-agent" }
```

### `GET /schema`
Returns the live database schema as plain text.

### `POST /query`
Accepts a natural language question, runs the agent, returns SQL + results.

**Request:**
```json
{ "question": "Show top 10 customers by total order value" }
```

**Response:**
```json
{
  "success": true,
  "sql": "SELECT c.company_name, SUM(...) ...",
  "columns": ["company_name", "total_value"],
  "rows": [...],
  "row_count": 10,
  "summary": "Agent reasoning..."
}
```

### `POST /execute`
Executes a raw SELECT query directly (only SELECT allowed).

**Request:**
```json
{ "sql": "SELECT * FROM customers LIMIT 5" }
```

---

## ⚙️ CI/CD Pipeline

Every push to `main` triggers:

```
git push main
      │
      ▼
 GitHub Actions
      │
      ├── 1. pytest (spins up PostgreSQL service container)
      │
      ├── 2. Docker build + push to Docker Hub
      │
      └── 3. Trigger Render deploy hooks → live app updates
```

### GitHub Secrets required

| Secret | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password or access token |
| `RENDER_DEPLOY_HOOK_BACKEND` | Render deploy hook URL for backend |
| `RENDER_DEPLOY_HOOK_FRONTEND` | Render deploy hook URL for frontend |

---

## 🌐 Deployment on Render

1. Push to GitHub
2. Create a **PostgreSQL** database on Render → copy the Internal Database URL
3. Load data: `psql "<external_db_url>" -f backend/northwind.sql`
4. Create **Web Service** for backend → Runtime: Docker → set `GROQ_API_KEY` and `DATABASE_URL`
5. Create **Web Service** for frontend → Runtime: Docker → set `API_URL` to backend URL
6. Update `API_URL` in `frontend/app.py` to your Render backend URL → push

> **Note:** Render free tier sleeps after 15 min of inactivity. First request after sleep takes ~30 seconds to wake up.

---

## 🖼 Screenshots

> Add screenshots of your running app here after deployment.

```
frontend/screenshots/
├── dashboard.png
├── results_table.png
├── visualization.png
└── sql_editor.png
```

---

## 🔑 Key Design Decisions

**1. Schema-aware prompting**
The agent reads the live schema at query time from `information_schema.columns` — it works on any PostgreSQL database without hardcoding table names.

**2. SQL validation layer**
Before execution, every query is checked for dangerous keywords (`DROP`, `DELETE`, `TRUNCATE`, `INSERT`, `UPDATE`). Only `SELECT` is permitted — a critical production safety decision.

**3. Transparent SQL output**
The generated SQL is shown alongside results and is editable. This builds user trust and is a real UX decision that data tools companies care about.

---

## 👨‍💻 Author

**Pranotosh Mandal**
M.Tech Data Analytics — IIT (ISM) Dhanbad

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/pranotosh-mandal-869460269/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/pranotosh2)

---

<div align="center">
  <sub>Built with ❤️ using LangChain · FastAPI · Streamlit · PostgreSQL · Docker</sub>
</div>
