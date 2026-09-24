# Phase 1 · Core Architecture Specification

> **Phase:** 1  
> **Priority:** P0 — Foundation  
> **Module Path:** `src/core/`  
> **Depends On:** None  
> **Unlocks:** Phase 2 (Database Layer), Phase 3 (Execution Tools)

---

## REQ-ARC-001 — Pydantic Settings Configuration Loader

**Requirement:** The application MUST load non-secret and secret environment settings through a validated Pydantic Settings model from `.env` and `configs/settings.yaml`.

**Rationale:** Centralizes environment configuration parsing and prevents hardcoded connection strings or API keys in application source code.

**Acceptance Criteria:**
- `src/core/config.py` defines `Settings` inheriting from `pydantic_settings.BaseSettings`.
- Loads `MSSQL_HOST`, `MSSQL_PORT`, `MSSQL_DATABASE`, `MSSQL_USERNAME`, `MSSQL_PASSWORD`, `OLLAMA_BASE_URL`, and `EMBEDDING_MODEL`.
- Fails fast with descriptive error message if mandatory variables are missing.

**Dependencies:** `pydantic-settings`, `.env`

**Status:** `[PLANNED]`

---

## REQ-ARC-002 — AgentState TypedDict Schema Contract

**Requirement:** The LangGraph ReAct orchestrator MUST pass state through a strongly-typed `AgentState` TypedDict using `add_messages` reducer for conversation history.

**Rationale:** Establishes predictable state contracts between LangGraph node functions, tool routers, and memory checkpointers.

**Acceptance Criteria:**
- `src/core/state.py` defines `AgentState(TypedDict)`.
- Contains `messages` (Annotated with `add_messages`), `session_id`, `dispatcher_query`, `fleet_data`, `sop_context`, `weather_data`, `tool_calls_made`, `has_error`, and `error_summary`.
- Direct mutation of state is prohibited; nodes must return partial update dicts.

**Dependencies:** `langgraph.graph.message.add_messages`

**Status:** `[PLANNED]`

---

## REQ-ARC-003 — Custom Exception Hierarchy

**Requirement:** The codebase MUST define a domain-specific exception hierarchy in `src/core/exceptions.py`.

**Rationale:** Enables precise error handling and graceful degradation across database timeouts, tool failures, and SQL safety violations.

**Acceptance Criteria:**
- Base exception `ColdChainAgentException` defined.
- Subclasses include `UnsafeSQLError`, `DatabaseUnavailableError`, `VectorStoreNotInitializedError`, `WeatherToolError`, and `AuditWriteError`.

**Dependencies:** None

**Status:** `[PLANNED]`
