# Phase 5 · Security & Immutable Audit Specification

> **Phase:** 5  
> **Priority:** P0 — Security & Immutability  
> **Module Path:** `src/database/audit.py`  
> **Depends On:** Phase 2 (Telemetry Database Layer)  
> **Unlocks:** Phase 6 (UI Presentation)

---

## REQ-AUD-001 — Immutable Append-Only Audit Table Schema

**Requirement:** The database MUST maintain an immutable audit table `FDE_VIEWS.AgentAuditLog` with `INSERT`-only permissions for the application user.

**Rationale:** Guarantees tamper-proof record of all AI reasoning steps, tool calls, and data access events for compliance verification.

**Acceptance Criteria:**
- `FDE_VIEWS.AgentAuditLog` contains columns: `audit_id`, `session_id`, `timestamp_utc`, `node_name`, `tool_name`, `input_summary`, `output_summary`, `reasoning_trace`, `llm_model_used`.
- Application database user role has `INSERT` grant only — `UPDATE` and `DELETE` privileges are explicitly denied.

**Dependencies:** `REQ-DB-001`

**Status:** `[PLANNED]`

---

## REQ-AUD-002 — Audit Log Writer & Failure Halting

**Requirement:** The application MUST write an audit record on every LangGraph node execution and tool call via `src/database/audit.py`.

**Rationale:** Ensures total traceability of agentic execution paths.

**Acceptance Criteria:**
- `log_agent_action(entry: AuditEntry)` inserts record into `FDE_VIEWS.AgentAuditLog`.
- If audit write fails (e.g. database disconnect), raises `AuditWriteError` and halts agent turn — silent swallowing of audit failures is prohibited.

**Dependencies:** `REQ-AUD-001`, `REQ-ARC-003`

**Status:** `[PLANNED]`
