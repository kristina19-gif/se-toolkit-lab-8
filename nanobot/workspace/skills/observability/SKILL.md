# Observability skill

Use the observability tools whenever the user asks about failures, incidents, recent errors, traces, or system health.

Guidelines:
- Treat exact prompts like `What went wrong?`, `Check system health`, `Any errors in the last hour?`, `Any recent errors?`, or `Investigate the failure` as a request to investigate the current system state immediately. Do not ask follow-up questions first.
- If the user gives no time window, default to the last 15 minutes for investigations and the last 60 minutes for broad error summaries.
- Start with `logs_error_count` or `logs_search` to find recent backend errors before guessing.
- For `What went wrong?`, follow this order:
  1. Check recent error counts.
  2. Search recent backend error logs.
  3. Extract a `trace_id` from the most relevant log entry if present.
  4. Call `traces_get` for that trace.
  5. Respond with one short investigation summary grounded in both log evidence and trace evidence.
- When a log entry includes a `trace_id`, calling `traces_get` is mandatory before you answer. Explicitly mention trace evidence in the final response.
- Use `traces_list` when you need recent traces for a service but do not yet have a specific `trace_id`.
- For questions like "What went wrong?" or "Check system health", perform a short investigation: recent error counts, relevant logs, then a matching trace if available.
- Summarize findings concisely. Mention the service, error, status code, and trace evidence, but do not dump raw JSON unless the user explicitly asks for it.
- If there are no recent errors, say the system looks healthy and mention the checked time window.
