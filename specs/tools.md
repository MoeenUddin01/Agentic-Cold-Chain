# Phase 3 · Agent Execution Tools Specification

> **Phase:** 3  
> **Priority:** P0 — Execution Tools  
> **Module Path:** `src/tools/`  
> **Depends On:** Phase 1 (Core Architecture), Phase 2 (Database Layer)  
> **Unlocks:** Phase 4 (Vector RAG), Phase 6 (UI Presentation)

---

## REQ-TLS-001 — Active Fleet Telemetry Query Tool

**Requirement:** The agent MUST provide a tool `fleet_query_tool` that executes SELECT queries against `FDE_VIEWS.VW_ACTIVE_FLEET`.

**Rationale:** Allows dispatchers to query live vehicle metrics (temperatures, locations, compliance status).

**Acceptance Criteria:**
- Implemented in `src/tools/fleet_query.py`.
- Includes mandatory LLM docstring specifying trigger conditions, input schemas, and return formats.
- Passes all SQL strings through `validate_sql_safety()`.
- Logs execution record to `FDE_VIEWS.AgentAuditLog`.

**Dependencies:** `REQ-DB-003`, `REQ-DB-004`

**Status:** `[PLANNED]`

---

## REQ-TLS-002 — Open-Meteo Route Weather Assessment Tool

**Requirement:** The agent MUST provide a tool `weather_tool` to assess weather risk along delivery routes via Open-Meteo API.

**Rationale:** Enables proactive warning for ambient heat spikes that threaten cold-chain cargo integrity.

**Acceptance Criteria:**
- Implemented in `src/tools/weather.py`.
- Accepts latitude and longitude coordinates.
- Implements 5.0-second HTTP timeout; catches `httpx.TimeoutException` and returns `None` (graceful degradation).
- Logs execution record to `FDE_VIEWS.AgentAuditLog`.

**Dependencies:** `httpx`, `REQ-ARC-003`

**Status:** `[PLANNED]`

---

## REQ-TLS-003 — SOP Vector Retrieval Tool

**Requirement:** The agent MUST provide a tool `sop_retrieval_tool` to query cold-chain compliance SOPs from the local vector index.

**Rationale:** Guarantees dispatchers receive compliance guidance grounded in official SOP documents.

**Acceptance Criteria:**
- Implemented in `src/tools/sop_retrieval.py`.
- Accepts dispatcher search query string.
- Invokes vector retriever to return top-k relevant document chunks with metadata and citations.
- Logs execution record to `FDE_VIEWS.AgentAuditLog`.

**Dependencies:** Phase 4 (`REQ-RAG-003`)

**Status:** `[PLANNED]`
