# Phase 6 · Presentation Layer Specification

> **Phase:** 6  
> **Priority:** P0 — Presentation  
> **Module Path:** `src/ui/`  
> **Depends On:** Phase 3 (Execution Tools), Phase 4 (Vector RAG), Phase 5 (Audit Logging)  
> **Unlocks:** None (Final Integration Phase)

---

## REQ-UI-001 — Streamlit Navigation & Dual-Console Shell

**Requirement:** `src/ui/app.py` MUST provide sidebar navigation switching between Dispatch Console and Audit Log Viewer views.

**Rationale:** Separates operational dispatching workflows from compliance audit review.

**Acceptance Criteria:**
- Implemented as Streamlit application (`streamlit run src/ui/app.py`).
- Sidebar contains view selector ("🚛 Dispatch Console", "📜 Audit Log Viewer").
- Caches compiled LangGraph graph using `@st.cache_resource`.

**Dependencies:** `streamlit`, `REQ-ARC-002`

**Status:** `[PLANNED]`

---

## REQ-UI-002 — Interactive Dispatcher Telemetry Console

**Requirement:** `src/ui/dispatch_console.py` MUST display real-time fleet telemetry cards alongside an interactive AI chat interface.

**Rationale:** Provides dispatchers with visual fleet metrics and conversational decision support.

**Acceptance Criteria:**
- Displays live vehicle temperature readings, compliance status badges (Normal / Warning / Alert), and location.
- Interactive chat interface invokes LangGraph agent loop.
- Renders AI responses with tool execution expanders and citations.

**Dependencies:** `REQ-UI-001`, `REQ-TLS-001`, `REQ-TLS-002`, `REQ-TLS-003`

**Status:** `[PLANNED]`

---

## REQ-UI-003 — Secured Read-Only Audit Log Trace Viewer

**Requirement:** `src/ui/audit_viewer.py` MUST provide a read-only table view of historical `FDE_VIEWS.AgentAuditLog` records.

**Rationale:** Enables safety officers and auditors to review LLM reasoning traces and verify compliance.

**Acceptance Criteria:**
- Queries `FDE_VIEWS.AgentAuditLog` ordered by `timestamp_utc DESC`.
- Supports filtering by `session_id`, `node_name`, or date range.
- Displays full reasoning trace in an expandable detail view.
- Provides CSV download option for audit reports.

**Dependencies:** `REQ-UI-001`, `REQ-AUD-001`

**Status:** `[PLANNED]`
