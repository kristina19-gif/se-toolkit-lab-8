# Lab 8 - Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A - Bare agent

Evidence still needs to be pasted manually from the early bare-agent run:
- response to "What is the agentic loop?"
- response to "What labs are available in our LMS?"

## Task 1B - Agent with LMS tools

Evidence still needs to be pasted manually from the LMS-tool run:
- response to "What labs are available?"
- response to "Describe the architecture of the LMS system"

## Task 1C - Skill prompt

Evidence still needs to be pasted manually from the skill-prompt run:
- response to "Show me the scores"

## Task 2A - Deployed agent

```text
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | WebChat channel enabled
nanobot-1  | WebChat starting on 0.0.0.0:8765
nanobot-1  | MCP server 'lms': connected, 13 tools registered
nanobot-1  | Agent loop started
```

## Task 2B - Web client

Verified automatically:
- `http://10.93.24.148:42002/flutter` returns the Flutter app HTML through Caddy.
- `/ws/chat` is reachable and nanobot processed messages from the WebSocket channel.

Manual screenshot still needed:
- open `http://10.93.24.148:42002/flutter`
- capture the connected Flutter chat UI

## Task 3A - Structured logging

Happy path excerpt from VictoriaLogs:

```json
{"_msg":"request_completed","_time":"2026-03-27T15:00:45.530419712Z","event":"request_completed","method":"GET","path":"/items/","severity":"INFO","status":"200","trace_id":"8c4eda0ec8321f4d820d4512a118ec20"}
{"_msg":"request_completed","_time":"2026-03-27T15:00:45.510801664Z","event":"request_completed","method":"GET","path":"/items/","severity":"INFO","status":"200","trace_id":"cab5ad3e1d9843e14d05682f70ae05a4"}
```

Error path excerpt from VictoriaLogs:

```json
{"_msg":"unhandled_exception","_time":"2026-03-27T14:56:01.196427008Z","event":"unhandled_exception","path":"/pipeline/sync","severity":"ERROR","trace_id":"18992d15d78e1f41236721575089a799","exception.type":"gaierror","exception.message":"-2"}
{"_msg":"unhandled_exception","_time":"2026-03-27T14:55:52.718885120Z","event":"unhandled_exception","path":"/items/","severity":"ERROR","trace_id":"f963a118582a7073d8e17f939a1d7c4c","exception.type":"gaierror","exception.message":"-2"}
```

Manual screenshot still needed:
- VictoriaLogs UI query at `http://10.93.24.148:42002/utils/victorialogs/select/vmui`

## Task 3B - Traces

Healthy trace sample retrieved from VictoriaTraces:

```json
{"traceID":"8c4eda0ec8321f4d820d4512a118ec20","serviceName":"Learning Management Service","operationName":"SELECT db-lab-8"}
```

Manual screenshots still needed:
- healthy trace span hierarchy in `http://10.93.24.148:42002/utils/victoriatraces`
- error trace showing the database failure path

## Task 3C - Observability MCP tools

Failure-condition response to "Any errors in the last hour?":

> Yes, there are 3 errors in the last hour, all from the Learning Management Service:
>
> - `unhandled_exception` | Pipeline sync failed - `socket.gaierror: [Errno -2] Name or service not known`
> - `db_query` | Database query failed - `[Errno -2] Name or service not known`
> - `db_query` | Database connection closed - `asyncpg.exceptions.InterfaceError: connection is closed`

Healthy-state note:

- Direct MCP smoke test against `logs_error_count` returned an empty list before the failure was induced.
- A browser/chat screenshot for the healthy prompt is still worth adding manually.

## Task 4A - Multi-step investigation

Response in the same chat after a failed LMS request:

> Based on my investigation, here's what went wrong with the LMS system:
>
> Root Cause: Database Connectivity Failure
>
> The LMS backend cannot connect to its database due to a DNS resolution error.
>
> Evidence from Logs:
> The error message `"[Errno -2] Name or service not known"` appears repeatedly in database query attempts.
>
> Impact:
> - All `/items/` endpoint requests fail with HTTP 500
> - Lab listings cannot be retrieved
> - Sync pipeline cannot complete

Note:
- The agent consistently investigated with the new log tools in the same failure chat.
- `traces_list` and `traces_get` were implemented and verified directly via MCP smoke tests.
- The exact `"What went wrong?"` phrasing still needs one more prompt-tuning pass if you want the final answer to mention trace evidence every single time without extra context.

## Task 4B - Proactive health check

Transcript excerpt from the proactive report posted back into the same chat:

> Health Check Report (2-minute window)
>
> Status: Backend Unhealthy
>
> - LMS Backend: HTTP 500
> - Errors (last 10 min): 7
> - Root Cause: database connectivity issue
> - Error: `socket.gaierror: [Errno -2] Name or service not known`
> - Trace ID: `4f3b96e5162d17fe5db475836845cd4c`

The same chat also listed the scheduled cron job:

> `f990a763 | Health Check | Every 2 minutes`

## Task 4C - Bug fix and recovery

1. Root cause

- The planted bug was in `backend/app/routers/items.py`.
- `get_items()` caught every exception and converted backend/database failures into `404 Items not found`, hiding the real failure path.

2. Fix

```diff
-    try:
-        return await read_items(session)
-    except Exception as exc:
-        raise HTTPException(
-            status_code=status.HTTP_404_NOT_FOUND,
-            detail="Items not found",
-        ) from exc
+    return await read_items(session)
```

3. Post-fix failure check

HTTP response after redeploy with PostgreSQL stopped:

```text
HTTP/1.1 500 Internal Server Error
{"detail":"[Errno -2] Name or service not known","type":"gaierror","path":"/items/"}
```

This confirms the real backend/database error is now surfaced instead of the old fake `404`.

4. Healthy follow-up

Recovery check after PostgreSQL restart:

```text
curl /items/ -> 56 records
```

Agent health summary after recovery:

> System Health Check
>
> LMS Backend Status: Healthy
> - Item count: 56
