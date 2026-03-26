# Lab 8 — The Agent is the Interface

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Your team has been running the LMS backend for weeks. Everyone queries data through the React dashboard or Swagger UI. Your team lead wants a new kind of interface: an AI agent that anyone can talk to in natural language. Instead of clicking through dashboards, users just ask questions — "which lab has the lowest pass rate?", "any errors in the last hour?" — and the agent figures out which API calls to make.
>
> Set it up from scratch. Wire it into the system. Then extend it with observability tools so it can answer questions about system health too.

## What you will learn

By the end of this lab, you should be able to say:

> 1. I can explain what makes an AI agent different from a regular client like a web app or a bot.
> 2. I set up nanobot from scratch — created the project, installed the framework, connected it to the Qwen API, wired it into Docker Compose, and talked to it.
> 3. I saw what a bare agent does without tools (hallucinates) vs. with MCP tools (answers correctly) — and I understand why.
> 4. I built MCP tools that let the agent query logs and traces, turning observability data into a conversational interface.
> 5. I used the agent to find and fix a real bug without manually grepping logs.
> 6. I configured a cron job so the agent proactively reports system health.

## Architecture

You start with the base LMS system (left side). During the lab, you add the agent and chat client (right side).

```
What you start with                    What you add
====================                   =============

┌──────────────┐                       ┌──────────────┐
│ React        │                       │ Flutter      │
│ Dashboard    │                       │ Chat UI      │
│ /            │                       │ /flutter     │
└──────┬───────┘                       └──────┬───────┘
       │ HTTP                                 │ WebSocket
       │                                      │
       ▼                                      ▼
┌──────────────────────────────────────────────────────┐
│  Caddy (reverse proxy)                               │
│  routes /items, /analytics, /ws/chat, /flutter, ...  │
└──────┬────────────────────────────────┬──────────────┘
       │                                │
       │ /items, /analytics, ...        │ /ws/chat
       ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│ Backend      │                 │ Nanobot      │
│ (FastAPI)    │◀────────────────│ (AI agent)   │
│              │   MCP tools     │              │
└──────┬───────┘                 └──────────────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │
└──────────────┘
```

### What you start with

| Service | What it does |
|---------|-------------|
| **backend** | FastAPI REST API — labs, scores, learners, analytics, ETL pipeline |
| **postgres** | Database storing all LMS data |
| **caddy** | Reverse proxy — routes traffic, serves the React dashboard |
| **client-web-react** | React dashboard at `/` — charts and tables |
| **qwen-code-api** | LLM proxy — gives you access to the Qwen language model |
| **pgadmin** | Database admin UI at `/utils/pgadmin` |

### What you add

| Service | What it does | When |
|---------|-------------|------|
| **nanobot** | AI agent — receives chat via WebSocket, reasons with LLM, calls backend via MCP tools | Task 1 |
| **client-web-flutter** | Chat UI at `/flutter` — talk to the agent in a browser | Task 1 |
| Observability MCP tools | Agent can query logs and traces | Task 2 |
| Cron health check | Agent reports system health on a schedule | Task 4 |

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Set Up the Agent](./lab/tasks/required/task-1.md) — create nanobot from scratch, connect to LLM, add MCP tools, add chat client
2. [Give the Agent New Eyes](./lab/tasks/required/task-2.md) — structured logging, observability MCP tools
3. [Diagnose and Fix a Bug](./lab/tasks/required/task-3.md) — use the agent to investigate a real production issue
4. [Make the Agent Proactive](./lab/tasks/required/task-4.md) — multi-step skills, cron health checks

### Optional

1. [Add a Telegram Bot Client](./lab/tasks/optional/task-1.md) — same agent, different interface
