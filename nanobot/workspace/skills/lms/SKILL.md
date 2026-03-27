# LMS skill

Use the `lms_*` MCP tools whenever the user asks about real LMS data such as labs, learners, pass rates, completion rates, groups, timelines, or sync status.

Guidelines:
- Prefer live `lms_*` tool calls over guessing.
- If the user asks for scores, pass rates, timelines, groups, top learners, or completion for a lab but does not specify the lab, ask which lab they mean or list available labs first.
- For `lms_health`, summarize whether the backend is healthy and include the item count if available.
- For numeric results, format percentages and counts clearly.
- Keep answers concise and grounded in tool output.
- If the user asks what you can do, explain that you can answer general questions and query live LMS data through tools, but you only know current LMS facts after calling those tools.
