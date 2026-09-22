# CLAUDE.md — Local Cold-Chain Logistics AI Assistant
> **Spec-Driven Development (SDD) System Instruction Set**
> Version: 1.0.0 | Target OS: Linux (Ubuntu) | Python: 3.12+

---

## ⚠️ MANDATORY PRE-FLIGHT CHECKLIST

Before writing **any** code, the AI coding agent MUST perform the following steps:

1. **Read this file in full.** Do not skip sections.
2. **Inspect existing source files** in `src/` to confirm architectural alignment before generating new code.
3. **Identify the relevant spec file** in `specs/` for the component being modified.
4. **Confirm zero drift** from the architectural layers defined in §1 before proceeding.
5. **Never assume** — if a file does not exist, say so. Do not hallucinate imports or schemas.

---

## §1 — Project Overview & Architecture

### Mission Statement

This platform is a **100% local, zero-cost, agentic orchestration system** for cold-chain logistics dispatchers. It operates entirely on-premise — no cloud LLM APIs, no external data exfiltration, no SaaS subscriptions. Every inference, embedding, retrieval, and audit event runs locally.

### Primary Use Case

Cold-chain logistics dispatchers query the AI assistant to:
- Monitor active fleet telemetry (temperature, location, vehicle status)
- Retrieve SOP guidance for compliance incidents
- Get real-time weather risk assessments along delivery routes
- Review immutable audit trails of all AI-generated decisions

---

### Architectural Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1 — PRESENTATION                                         │
│  Streamlit (Dual-View UI)                                        │
│  ├── Dispatch Console   → Live fleet telemetry + AI chat         │
│  └── Audit Log Viewer   → Secured, read-only agent trace log     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2 — ORCHESTRATION                                         │
│  LangGraph (ReAct State Machine)                                 │
│  ├── State: AgentState (TypedDict)                               │
│  ├── Router: tool_router node (decides tool invocations)         │
│  ├── Memory: SqliteSaver / MemorySaver (checkpointing)           │
│  └── Supervisor: halts on unsafe SQL patterns                    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3 — EXECUTION (TOOLS)                                     │
│  ├── SQLAlchemy → Telemetry queries (SELECT-only, FDE_VIEWS)     │
│  ├── Local Vector RAG → FAISS/ChromaDB + BAAI/bge-m3 embeddings │
│  └── Open-Meteo API → Weather risk assessment (graceful deg.)    │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4 — DATA & SECURITY                                       │
│  ├── MSSQL 2022 (Docker) → Primary telemetry database           │
│  ├── FDE_VIEWS schema → Read-only SQL views (agent access only)  │
│  └── AgentAuditLog → Append-only audit table (immutable)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## §2 — Tech Stack & Environment

### Core Runtime

| Component | Technology | Version Constraint |
|---|---|---|
| Language | Python | `>=3.12` |
| Agent Orchestration | LangGraph | `>=0.2` |
| LLM Integration | LangChain | `>=0.3` |
| Presentation | Streamlit | `>=1.35` |
| Package Manager | `uv` | **Exclusively** — never use `pip` directly |

### Database & ORM

| Component | Technology | Notes |
|---|---|---|
| Primary Database | MSSQL 2022 (Docker) | `mcr.microsoft.com/mssql/server:2022-latest` |
| ODBC Driver | `pyodbc` | ODBC Driver 18 for SQL Server |
| ORM | SQLAlchemy | `>=2.0`, async-compatible |
| Connection Schema | `FDE_VIEWS` | Agent ONLY ever queries this schema |

### AI & Embedding Stack

| Component | Technology | Notes |
|---|---|---|
| Local LLM Runtime | Ollama | Primary; Groq API as optional fallback |
| Embedding Model | `BAAI/bge-m3` (HuggingFace) | Loaded via `sentence-transformers` |
| Vector Store | FAISS **or** ChromaDB | Local only — no Pinecone, no Weaviate Cloud |
| SOP Document Loader | LangChain `DirectoryLoader` | Loads from `data/sops/` |

### OS & Infrastructure

- **Primary Target:** Linux (Ubuntu 22.04+)
- **Containerization:** Docker (MSSQL only)
- **No WSL assumptions** — all paths must use POSIX format

---

## §3 — Directory Structure (Canonical)

```text
Agentic-Cold-Chain/
│
├── CLAUDE.md                    # ← YOU ARE HERE (system instruction set)
├── README.md
├── pyproject.toml               # uv-managed project manifest
├── uv.lock                      # Lockfile — NEVER edit manually
├── .env.example                 # Template; never commit .env
├── .gitignore
│
├── specs/                       # SDD specification files — READ BEFORE CODING
│   ├── architecture.md          # Layer boundaries and data flow diagrams
│   ├── tools.md                 # Tool input/output schemas (LLM-facing docstrings)
│   ├── database.md              # SQL view schemas and FDE_VIEWS contract
│   ├── rag.md                   # Embedding pipeline and retrieval strategy
│   ├── audit.md                 # Audit log schema and immutability rules
│   └── ui.md                    # Streamlit layout and session state contracts
│
├── configs/
│   ├── settings.yaml            # Non-secret configuration (ports, model names)
│   └── logging.yaml             # Structured logging configuration
│
├── data/
│   ├── sops/                    # Cold-chain SOP documents (PDF, DOCX, MD)
│   ├── vector_store/            # Persisted FAISS index or ChromaDB directory
│   └── manifests/               # Document ingestion checksums
│
├── docker/
│   └── mssql-init/
│       ├── init.sql             # Schema bootstrap: FDE_VIEWS, AgentAuditLog
│       └── seed.sql             # Development seed data (non-production)
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py            # Pydantic Settings — loads from .env
│   │   ├── constants.py         # DB schema names, view names, model IDs
│   │   ├── exceptions.py        # Custom exception hierarchy
│   │   └── state.py             # AgentState TypedDict definition
│   │
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine factory (MSSQL + pyodbc)
│   │   ├── views.py             # ORM mapped classes for FDE_VIEWS
│   │   └── audit.py             # AgentAuditLog write function (append-only)
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── fleet_query.py       # Tool: query FDE_VIEWS.VW_ACTIVE_FLEET
│   │   ├── sop_retrieval.py     # Tool: semantic search over SOP vector store
│   │   └── weather.py           # Tool: Open-Meteo route weather assessment
│   │
│   ├── rag/
│   │   ├── embedder.py          # @st.cache_resource embedding model loader
│   │   ├── indexer.py           # SOP ingestion → chunking → vector store
│   │   └── retriever.py         # Similarity search + reranking
│   │
│   ├── agent/
│   │   ├── graph.py             # LangGraph StateGraph definition
│   │   ├── nodes.py             # All ReAct node functions
│   │   ├── router.py            # Conditional edge logic (tool routing)
│   │   └── prompts.py           # System prompt templates
│   │
│   └── ui/
│       ├── app.py               # Streamlit entry point
│       ├── dispatch_console.py  # Primary dispatcher view
│       └── audit_viewer.py      # Secured audit log view
│
└── tests/
    ├── unit/
    │   ├── test_tools.py
    │   ├── test_agent_nodes.py
    │   └── test_rag.py
    └── integration/
        ├── test_database.py
        └── test_end_to_end.py
```

---

## §4 — Setup & Execution Commands

### 4.1 — Database Initialization (MSSQL via Docker)

```bash
# Pull and run MSSQL 2022 with persistent volume
docker run -e "ACCEPT_EULA=Y" \
           -e "MSSQL_SA_PASSWORD=YourStrong!Passw0rd" \
           -e "MSSQL_PID=Developer" \
           -p 1433:1433 \
           --name cold-chain-mssql \
           -v cold-chain-mssql-data:/var/opt/mssql \
           -d mcr.microsoft.com/mssql/server:2022-latest

# Wait for SQL Server to be ready, then run schema bootstrap
docker exec -it cold-chain-mssql \
  /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U SA -P "YourStrong!Passw0rd" \
  -i /docker/mssql-init/init.sql -No
```

### 4.2 — Python Environment Setup (uv)

```bash
# Create virtual environment (Python 3.12 required)
uv venv --python 3.12

# Activate environment
source .venv/bin/activate

# Sync all dependencies from pyproject.toml + uv.lock
uv sync

# Install ODBC Driver 18 for SQL Server (Ubuntu)
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list \
  | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

### 4.3 — Running the Application

```bash
# Run the SOP ingestion / vector index builder
uv run python src/rag/indexer.py

# Run the LangGraph orchestrator (headless, for testing)
uv run python src/agent/graph.py

# Launch the Streamlit UI (primary entry point)
uv run streamlit run src/ui/app.py --server.port 8501

# Run tests
uv run pytest tests/ -v
```

### 4.4 — Ollama Model Setup

```bash
# Pull the local reasoning model (adjust model tag as needed)
ollama pull llama3.1:8b

# Verify the model is available
ollama list
```

---

## §5 — Development Rules & Security Constraints (CRITICAL — NEVER VIOLATE)

### 5.1 — ZERO-MUTATION RULE (Database Safety)

> **This is an absolute, non-negotiable constraint. Violation terminates the agent session.**

- **The AI agent MUST NEVER generate or execute** `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, or `GRANT` statements against any database.
- **All LLM-generated SQL MUST:**
  1. Begin with the literal token `SELECT`
  2. Reference exclusively `FDE_VIEWS.VW_ACTIVE_FLEET` (or other explicitly whitelisted `FDE_VIEWS.*` views)
  3. Pass through the `validate_sql_safety()` guard function before execution

```python
# src/database/connection.py — MANDATORY GUARD (do not remove or bypass)
import re

FORBIDDEN_SQL_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|EXEC|GRANT|REVOKE|MERGE)\b",
    flags=re.IGNORECASE,
)

def validate_sql_safety(sql: str) -> str:
    """
    Validates that an LLM-generated SQL string is safe to execute.

    Rules:
      - Must start with SELECT (after stripping whitespace/comments)
      - Must not contain any mutation keywords
      - Must reference only FDE_VIEWS schema objects

    Args:
        sql: The raw SQL string generated by the LLM.

    Returns:
        The validated SQL string (unchanged) if safe.

    Raises:
        UnsafeSQLError: If any forbidden pattern is detected.
    """
    clean = sql.strip().upper()
    if not clean.startswith("SELECT"):
        raise UnsafeSQLError(f"SQL must begin with SELECT. Got: {sql[:80]!r}")
    if FORBIDDEN_SQL_PATTERNS.search(sql):
        raise UnsafeSQLError(f"Forbidden mutation keyword detected in SQL: {sql[:80]!r}")
    if "FDE_VIEWS" not in sql.upper():
        raise UnsafeSQLError("SQL must reference FDE_VIEWS schema exclusively.")
    return sql
```

### 5.2 — IMMUTABLE AUDIT LOG

- **Every** LangGraph node execution and tool invocation MUST be logged to `FDE_VIEWS.AgentAuditLog`.
- Audit records are **append-only**. The application user role has `INSERT` permission ONLY on `AgentAuditLog` — no `UPDATE` or `DELETE`.
- Each audit record MUST capture: `session_id`, `timestamp_utc`, `node_name`, `tool_name`, `input_summary`, `output_summary`, `reasoning_trace`, `llm_model_used`.
- If the audit log write fails, the agent must **raise an exception and halt** — do not silently swallow audit failures.

```python
# Canonical audit log entry structure (src/database/audit.py)
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class AuditEntry:
    session_id: str
    timestamp_utc: datetime
    node_name: str
    tool_name: str | None
    input_summary: str          # max 1000 chars
    output_summary: str         # max 1000 chars
    reasoning_trace: str        # full chain-of-thought
    llm_model_used: str
```

### 5.3 — STATE MANAGEMENT (Streamlit Memory Safety)

- **Embedding models MUST be loaded using `@st.cache_resource`** — never inside a standard function call or `st.session_state`.
- Loading the `BAAI/bge-m3` model outside of `@st.cache_resource` will cause memory duplication on every Streamlit rerun, leading to OOM crashes.
- The LangGraph graph object (`compiled_graph`) MUST also be initialized with `@st.cache_resource`.

```python
# src/rag/embedder.py — CORRECT PATTERN (mandatory)
import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_embedding_model() -> SentenceTransformer:
    """
    Loads the BAAI/bge-m3 embedding model into a cached singleton.

    This function is decorated with @st.cache_resource to ensure the model
    is instantiated exactly once per Streamlit server process, preventing
    memory duplication across UI reruns.

    Returns:
        SentenceTransformer: The loaded embedding model, ready for inference.
    """
    return SentenceTransformer("BAAI/bge-m3", device="cpu")

# WRONG — never do this inside a node or button callback:
# model = SentenceTransformer("BAAI/bge-m3")
```

### 5.4 — GRACEFUL DEGRADATION

All external tool calls MUST implement graceful degradation. The agent must never crash due to a single tool failure.

| Tool | Failure Scenario | Required Behavior |
|---|---|---|
| `weather.py` (Open-Meteo) | HTTP timeout / 5xx | Log warning, set `weather_data = None`, continue with partial context |
| `fleet_query.py` (MSSQL) | Connection refused / timeout | Raise `DatabaseUnavailableError`, surface friendly message to dispatcher |
| `sop_retrieval.py` (FAISS) | Index not found | Raise `VectorStoreNotInitializedError`, prompt user to run `indexer.py` |

```python
# src/tools/weather.py — CORRECT graceful degradation pattern
import httpx
from src.core.exceptions import WeatherToolError

async def get_route_weather(lat: float, lon: float) -> dict | None:
    """
    Fetches real-time weather data for a delivery route coordinate.

    Args:
        lat: Latitude of the route checkpoint.
        lon: Longitude of the route checkpoint.

    Returns:
        dict: Weather payload from Open-Meteo, or None if the service
              is unavailable. The agent MUST handle the None case.

    Raises:
        WeatherToolError: Only on unexpected non-timeout errors.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": lat, "longitude": lon, "current_weather": True},
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        # Graceful degradation: log and return None, do NOT raise
        return None
    except httpx.HTTPStatusError as exc:
        raise WeatherToolError(f"Open-Meteo returned {exc.response.status_code}") from exc
```

---

## §6 — Spec-Driven Development (SDD) Enforcement

### 6.1 — Pre-Coding Alignment Protocol

Before writing any new module or modifying an existing one, the agent MUST:

1. **Locate the relevant spec file** in `specs/` and read it completely.
2. **Confirm the component's layer** from the architecture diagram in §1.
3. **Check for existing implementations** — never duplicate logic that already exists.
4. **Announce the spec alignment** in a comment at the top of each new file:

```python
# Spec: specs/tools.md § Fleet Query Tool
# Layer: Execution (Layer 3)
# Arch-status: Aligned with FDE_VIEWS Zero-Mutation constraint (§5.1)
```

### 6.2 — Tool Docstring Standard (MANDATORY)

Every LangGraph tool function MUST include a structured docstring. The LLM uses these docstrings to decide when and how to invoke each tool. Incomplete docstrings will cause incorrect tool routing.

**Required docstring sections for all tools:**

```python
def tool_function(param: InputType) -> OutputType:
    """
    [One-line description of what this tool does for the dispatcher.]

    Use this tool when:
      - [Trigger condition 1]
      - [Trigger condition 2]

    Do NOT use this tool when:
      - [Anti-pattern 1]
      - [Anti-pattern 2]

    Args:
        param (InputType): Description of the parameter.
            Schema: { "field": "type — description" }

    Returns:
        OutputType: Description of the return value.
            Schema: { "field": "type — description" }

    Side Effects:
        - Writes one record to AgentAuditLog on every invocation.

    Raises:
        SpecificError: When [condition].
    """
```

### 6.3 — New Feature Addition Checklist

When adding any new capability:

- [ ] Spec file updated in `specs/` before code is written
- [ ] Tool docstring complete (§6.2 format)
- [ ] `validate_sql_safety()` called if any SQL is generated
- [ ] Audit log entry written before function returns
- [ ] Graceful degradation implemented for all external I/O
- [ ] `@st.cache_resource` used for any model or graph object
- [ ] Unit test added in `tests/unit/`
- [ ] `src/core/exceptions.py` updated with any new exception types

---

## §7 — LangGraph State Contract

### AgentState (Canonical Definition)

```python
# src/core/state.py — DO NOT modify this schema without updating specs/architecture.md
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Conversation history (append-only via add_messages reducer)
    messages: Annotated[list, add_messages]

    # Active session identifier (links to AgentAuditLog.session_id)
    session_id: str

    # Dispatcher query that triggered this graph run
    dispatcher_query: str

    # Results populated by tool nodes (None = tool not yet invoked)
    fleet_data: dict | None
    sop_context: list[str] | None
    weather_data: dict | None

    # Reasoning metadata
    tool_calls_made: list[str]       # Names of tools invoked this run
    has_error: bool                  # True if any tool raised a handled exception
    error_summary: str | None        # Human-readable error description for UI
```

### Node Execution Contract

Every node function in `src/agent/nodes.py` MUST:
1. Accept `state: AgentState` as its only argument
2. Return a `dict` with only the keys it modifies (LangGraph merges partial updates)
3. Write to `AgentAuditLog` before returning
4. Never mutate `state` in-place — return a new dict

---

## §8 — Environment Variables (.env)

```bash
# .env.example — Copy to .env and fill in values. NEVER commit .env.

# --- Database ---
MSSQL_HOST=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=ColdChainDB
MSSQL_USERNAME=dispatcher_readonly
MSSQL_PASSWORD=<REDACTED>
MSSQL_DRIVER=ODBC Driver 18 for SQL Server

# --- LLM ---
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
# Optional Groq fallback (leave blank to disable)
GROQ_API_KEY=

# --- Embeddings ---
EMBEDDING_MODEL=BAAI/bge-m3
VECTOR_STORE_PATH=data/vector_store/
VECTOR_STORE_BACKEND=faiss   # or "chromadb"

# --- Application ---
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
AUDIT_LOG_TABLE=FDE_VIEWS.AgentAuditLog
```

---

## §9 — Prohibited Patterns (Hard Failures)

The following patterns MUST NOT appear anywhere in the codebase. If found, flag immediately and do not execute:

| # | Forbidden Pattern | Reason |
|---|---|---|
| 1 | `openai.Client()` or `anthropic.Anthropic()` | Violates zero-cloud constraint |
| 2 | `pip install` in any script or Makefile | Use `uv` exclusively |
| 3 | Any SQL without `validate_sql_safety()` call | Zero-mutation rule |
| 4 | `SentenceTransformer(...)` outside `@st.cache_resource` | Memory deadlock risk |
| 5 | `os.environ["MSSQL_PASSWORD"]` in source code | Use Pydantic Settings only |
| 6 | `try: ... except: pass` (bare except swallowing) | Masks audit log failures |
| 7 | Hardcoded IP addresses or connection strings | Use `.env` + config only |
| 8 | `AgentAuditLog` UPDATE or DELETE statements | Immutability violation |
| 9 | Vector store writes to cloud endpoints | Local-only vector storage |
| 10 | Returning data directly from raw DB tables | Must use `FDE_VIEWS` only |

---

## §10 — Quick Reference Card

```
PROJECT:   Local Cold-Chain Logistics AI Assistant
RUNTIME:   Python 3.12+ | uv (package manager)
UI:        uv run streamlit run src/ui/app.py
AGENT:     uv run python src/agent/graph.py
INGEST:    uv run python src/rag/indexer.py
TEST:      uv run pytest tests/ -v
DB:        docker start cold-chain-mssql
SCHEMA:    FDE_VIEWS (read-only views ONLY)
AUDIT:     FDE_VIEWS.AgentAuditLog (append-only)
SQL RULE:  SELECT + FDE_VIEWS only — no mutations
MEMORY:    @st.cache_resource for all models
FALLBACK:  Graceful degradation on ALL external tools
```

---

*This CLAUDE.md is the authoritative system instruction set for this repository. All contributors — human and AI — must treat it as the source of truth for architectural decisions, security constraints, and development workflows. Amendments require explicit version bumps and spec file updates.*
