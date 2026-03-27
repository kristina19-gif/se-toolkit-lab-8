"""Async HTTP client and models for LMS and observability services."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class HealthResult(BaseModel):
    status: str
    item_count: int | str = "unknown"
    error: str = ""


class Item(BaseModel):
    id: int | None = None
    type: str = "step"
    parent_id: int | None = None
    title: str = ""
    description: str = ""


class Learner(BaseModel):
    id: int | None = None
    external_id: str = ""
    student_group: str = ""


class PassRate(BaseModel):
    task: str
    avg_score: float
    attempts: int


class TimelineEntry(BaseModel):
    date: str
    submissions: int


class GroupPerformance(BaseModel):
    group: str
    avg_score: float
    students: int


class TopLearner(BaseModel):
    learner_id: int
    avg_score: float
    attempts: int


class CompletionRate(BaseModel):
    lab: str
    completion_rate: float
    passed: int
    total: int


class SyncResult(BaseModel):
    new_records: int
    total_records: int


class LogEntry(BaseModel):
    timestamp: str = ""
    message: str = ""
    service: str = ""
    severity: str = ""
    event: str = ""
    path: str = ""
    status: str = ""
    trace_id: str = ""
    span_id: str = ""
    error: str = ""


class LogSearchResult(BaseModel):
    query: str
    logs: list[LogEntry]


class ErrorCount(BaseModel):
    service: str
    errors: int


class ErrorCountResult(BaseModel):
    query: str
    counts: list[ErrorCount]


class TraceSpanReference(BaseModel):
    trace_id: str = Field(alias="traceID")
    span_id: str = Field(alias="spanID")
    ref_type: str = Field(alias="refType")
    model_config = ConfigDict(populate_by_name=True)


class TraceTag(BaseModel):
    key: str
    type: str | None = None
    value: Any = None


class TraceLogField(BaseModel):
    key: str
    value: Any = None


class TraceLogRecord(BaseModel):
    timestamp: int
    fields: list[TraceLogField] = Field(
        default_factory=lambda: cast(list[TraceLogField], [])
    )


class TraceProcess(BaseModel):
    service_name: str = Field(alias="serviceName")
    tags: list[TraceTag] = Field(default_factory=lambda: cast(list[TraceTag], []))
    model_config = ConfigDict(populate_by_name=True)


class TraceSpan(BaseModel):
    trace_id: str = Field(alias="traceID")
    span_id: str = Field(alias="spanID")
    operation_name: str = Field(alias="operationName")
    start_time: int = Field(alias="startTime")
    duration: int
    process_id: str = Field(alias="processID")
    references: list[TraceSpanReference] = Field(
        default_factory=lambda: cast(list[TraceSpanReference], [])
    )
    tags: list[TraceTag] = Field(default_factory=lambda: cast(list[TraceTag], []))
    logs: list[TraceLogRecord] = Field(
        default_factory=lambda: cast(list[TraceLogRecord], [])
    )
    model_config = ConfigDict(populate_by_name=True)


class TraceSummary(BaseModel):
    trace_id: str
    services: list[str]
    operations: list[str]
    span_count: int
    start_time: str
    duration_ms: float


class TraceListResult(BaseModel):
    service: str
    traces: list[TraceSummary]


class TraceData(BaseModel):
    trace_id: str
    services: list[str]
    operations: list[str]
    span_count: int
    start_time: str
    duration_ms: float
    spans: list[TraceSpan]


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------


class LMSClient:
    """Client for the LMS backend API and observability endpoints."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        logs_url: str | None = None,
        traces_url: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.logs_url = (logs_url or "").rstrip("/")
        self.traces_url = (traces_url or "").rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers, timeout=10.0)

    def _logs_client(self) -> httpx.AsyncClient:
        if not self.logs_url:
            raise RuntimeError(
                "VictoriaLogs URL not configured. Set NANOBOT_LOGS_BASE_URL."
            )
        return httpx.AsyncClient(timeout=15.0)

    def _traces_client(self) -> httpx.AsyncClient:
        if not self.traces_url:
            raise RuntimeError(
                "VictoriaTraces URL not configured. Set NANOBOT_TRACES_BASE_URL."
            )
        return httpx.AsyncClient(timeout=15.0)

    async def health_check(self) -> HealthResult:
        async with self._client() as c:
            try:
                r = await c.get(f"{self.base_url}/items/")
                r.raise_for_status()
                items = [Item.model_validate(i) for i in r.json()]
                return HealthResult(status="healthy", item_count=len(items))
            except httpx.ConnectError:
                return HealthResult(
                    status="unhealthy", error=f"connection refused ({self.base_url})"
                )
            except httpx.HTTPStatusError as exc:
                return HealthResult(
                    status="unhealthy", error=f"HTTP {exc.response.status_code}"
                )
            except Exception as exc:
                return HealthResult(status="unhealthy", error=str(exc))

    async def get_items(self) -> list[Item]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/items/")
            r.raise_for_status()
            return [Item.model_validate(i) for i in r.json()]

    async def get_learners(self) -> list[Learner]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/learners/")
            r.raise_for_status()
            return [Learner.model_validate(i) for i in r.json()]

    async def get_pass_rates(self, lab: str) -> list[PassRate]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
            )
            r.raise_for_status()
            return [PassRate.model_validate(i) for i in r.json()]

    async def get_timeline(self, lab: str) -> list[TimelineEntry]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/timeline",
                params={"lab": lab},
            )
            r.raise_for_status()
            return [TimelineEntry.model_validate(i) for i in r.json()]

    async def get_groups(self, lab: str) -> list[GroupPerformance]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/groups",
                params={"lab": lab},
            )
            r.raise_for_status()
            return [GroupPerformance.model_validate(i) for i in r.json()]

    async def get_top_learners(self, lab: str, limit: int = 5) -> list[TopLearner]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/top-learners",
                params={"lab": lab, "limit": limit},
            )
            r.raise_for_status()
            return [TopLearner.model_validate(i) for i in r.json()]

    async def get_completion_rate(self, lab: str) -> CompletionRate:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/completion-rate",
                params={"lab": lab},
            )
            r.raise_for_status()
            return CompletionRate.model_validate(r.json())

    async def sync_pipeline(self) -> SyncResult:
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/pipeline/sync")
            r.raise_for_status()
            return SyncResult.model_validate(r.json())

    async def logs_search(
        self,
        *,
        keyword: str = "",
        service: str = "",
        level: str = "",
        minutes: int = 60,
        limit: int = 20,
    ) -> LogSearchResult:
        filters = [f"_time:{minutes}m"]
        if service:
            filters.append(f'"service.name":"{service}"')
        if level:
            filters.append(f"severity:{level.upper()}")
        if keyword:
            filters.append(f'"{keyword}"')
        query = " AND ".join(filters)

        async with self._logs_client() as c:
            r = await c.get(
                f"{self.logs_url}/select/logsql/query",
                params={"query": query, "limit": limit},
            )
            r.raise_for_status()
            logs = [_normalize_log_entry(line) for line in r.text.splitlines() if line]
        return LogSearchResult(query=query, logs=logs)

    async def logs_error_count(
        self,
        *,
        minutes: int = 60,
        service: str = "",
    ) -> ErrorCountResult:
        filters = [f"_time:{minutes}m", "severity:ERROR"]
        if service:
            filters.append(f'"service.name":"{service}"')
        base_query = " AND ".join(filters)
        query = (
            f"{base_query} | stats by (service.name) count() as errors "
            "| sort by (errors desc)"
        )

        async with self._logs_client() as c:
            r = await c.get(
                f"{self.logs_url}/select/logsql/query",
                params={"query": query, "limit": 50},
            )
            r.raise_for_status()
            counts = [
                ErrorCount(
                    service=str(row.get("service.name") or "unknown"),
                    errors=int(row.get("errors") or 0),
                )
                for row in _parse_json_lines(r.text)
            ]
        return ErrorCountResult(query=query, counts=counts)

    async def traces_list(
        self,
        *,
        service: str,
        minutes: int = 60,
        limit: int = 10,
    ) -> TraceListResult:
        end = datetime.now(tz=UTC)
        start = end - timedelta(minutes=minutes)
        params = {
            "service": service,
            "start": _unix_micros(start),
            "end": _unix_micros(end),
            "limit": limit,
        }
        async with self._traces_client() as c:
            r = await c.get(
                f"{self.traces_url}/select/jaeger/api/traces",
                params=params,
            )
            r.raise_for_status()
            payload = r.json()
        traces = [_trace_summary(item) for item in payload.get("data", [])]
        return TraceListResult(service=service, traces=traces)

    async def traces_get(self, trace_id: str) -> TraceData:
        async with self._traces_client() as c:
            r = await c.get(f"{self.traces_url}/select/jaeger/api/traces/{trace_id}")
            r.raise_for_status()
            payload = r.json()
        traces = payload.get("data", [])
        if not traces:
            raise RuntimeError(f"Trace not found: {trace_id}")
        return _trace_detail(traces[0])


def _parse_json_lines(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _normalize_log_entry(raw: str) -> LogEntry:
    data = json.loads(raw)
    return LogEntry(
        timestamp=str(data.get("_time", "")),
        message=str(data.get("_msg", "")),
        service=str(data.get("service.name", data.get("otelServiceName", ""))),
        severity=str(data.get("severity", "")),
        event=str(data.get("event", "")),
        path=str(data.get("path", "")),
        status=str(data.get("status", "")),
        trace_id=str(data.get("trace_id", data.get("otelTraceID", ""))),
        span_id=str(data.get("span_id", data.get("otelSpanID", ""))),
        error=str(data.get("error", "")),
    )


def _unix_micros(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000)


def _trace_summary(data: dict[str, Any]) -> TraceSummary:
    spans = [TraceSpan.model_validate(span) for span in data.get("spans", [])]
    return TraceSummary(
        trace_id=str(data.get("traceID", "")),
        services=_trace_services(data),
        operations=sorted({span.operation_name for span in spans}),
        span_count=len(spans),
        start_time=_format_trace_start(spans),
        duration_ms=_trace_duration_ms(spans),
    )


def _trace_detail(data: dict[str, Any]) -> TraceData:
    spans = [TraceSpan.model_validate(span) for span in data.get("spans", [])]
    return TraceData(
        trace_id=str(data.get("traceID", "")),
        services=_trace_services(data),
        operations=sorted({span.operation_name for span in spans}),
        span_count=len(spans),
        start_time=_format_trace_start(spans),
        duration_ms=_trace_duration_ms(spans),
        spans=spans,
    )


def _trace_services(data: dict[str, Any]) -> list[str]:
    processes = data.get("processes", {})
    service_names = {
        TraceProcess.model_validate(process).service_name
        for process in processes.values()
    }
    return sorted(service_names)


def _format_trace_start(spans: list[TraceSpan]) -> str:
    if not spans:
        return ""
    start_micros = min(span.start_time for span in spans)
    return datetime.fromtimestamp(start_micros / 1_000_000, tz=UTC).isoformat()


def _trace_duration_ms(spans: list[TraceSpan]) -> float:
    if not spans:
        return 0.0
    start = min(span.start_time for span in spans)
    end = max(span.start_time + span.duration for span in spans)
    return round((end - start) / 1_000, 3)


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def format_health(result: HealthResult) -> str:
    if result.status == "healthy":
        return f"\u2705 Backend is healthy. {result.item_count} items available."
    return f"\u274c Backend error: {result.error or 'Unknown'}"


def format_labs(items: list[Item]) -> str:
    labs = sorted(
        [item for item in items if item.type == "lab"],
        key=lambda item: str(item.id),
    )
    if not labs:
        return "\U0001f4ed No labs available."
    text = "\U0001f4da Available labs:\n\n"
    text += "\n".join(f"\u2022 {lab.title}" for lab in labs)
    return text


def format_scores(lab: str, rates: list[PassRate]) -> str:
    if not rates:
        return f"\U0001f4ed No scores found for {lab}."
    text = f"\U0001f4ca Pass rates for {lab}:\n\n"
    text += "\n".join(
        f"\u2022 {rate.task}: {rate.avg_score:.1f}% ({rate.attempts} attempts)"
        for rate in rates
    )
    return text
