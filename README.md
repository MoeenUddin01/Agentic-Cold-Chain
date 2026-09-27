# 🚛 Local Cold-Chain Logistics AI Assistant

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Package Manager: uv](https://img.shields.io/badge/package_manager-uv-8A2BE2.svg)](https://github.com/astral-sh/uv)
[![Orchestration: LangGraph](https://img.shields.io/badge/orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![UI: Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Database: MSSQL 2022](https://img.shields.io/badge/database-MSSQL_2022-CC292B.svg)](https://www.microsoft.com/en-us/sql-server/sql-server-2022)
[![Privacy: 100% Local](https://img.shields.io/badge/privacy-100%25_Local_Zero_Cloud-success.svg)](#security--governance)

An enterprise-grade, **100% local, zero-cost, agentic orchestration platform** for cold-chain logistics dispatchers. Designed to operate completely on-premise without cloud LLM APIs, SaaS subscriptions, or data exfiltration.

---

## 🌟 Key Features

- **📺 Dual-View Console**:
  - **Dispatcher View**: Live fleet telemetry tracking, cold-chain temperature monitoring, and interactive AI agent chat.
  - **Audit Viewer**: Secured, read-only interface to trace all historical LLM reasoning chains and tool executions.
- **⚡ LangGraph ReAct State Machine**: State-driven decision routing with memory checkpointing, tool validation, and error recovery.
- **🔒 Zero-Mutation Database Security**: Strict enforcement requiring all AI-generated SQL to be `SELECT`-only against read-only `FDE_VIEWS` schemas.
- **📜 Immutable Audit Trail**: Append-only logging to `FDE_VIEWS.AgentAuditLog` capturing session IDs, prompt parameters, tool outputs, and LLM reasoning steps.
- **📚 Local Vector RAG**: SOP retrieval using local `BAAI/bge-m3` embeddings combined with FAISS / ChromaDB for offline compliance lookup.
- **🌤️ Route Weather Assessment**: Real-time checkpoint weather evaluation powered by Open-Meteo with built-in graceful degradation handling.

---

## 🏗️ Architecture Overview

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

## 📐 Spec-Driven Development (SDD)

This project strictly adheres to **Spec-Driven Development**. All intended system behavior is documented in the `specs/` directory, which acts as the **source of truth**.

The development follows a phased execution order:
1. **Foundation** (`specs/architecture.md`)
2. **Data Layer** (`specs/database.md`)
3. **Execution Tools** (`specs/tools.md`)
4. **Vector RAG** (`specs/rag.md`)
5. **Security & Audit** (`specs/audit.md`)
6. **Presentation** (`specs/ui.md`)

Code is only written or modified after the corresponding specification is marked `[STABLE]` and verified.

---

## 🛠️ Tech Stack & Environment

| Component | Technology | Description |
|---|---|---|
| **Runtime** | Python 3.12+ | Core language execution |
| **Package Manager** | `uv` | Fast dependency resolution and environment isolation |
| **Agent Orchestration** | LangGraph & LangChain | ReAct state graphs and tool abstractions |
| **User Interface** | Streamlit | Responsive web console and audit log viewer |
| **Telemetry DB** | MSSQL Server 2022 (Docker) | Primary telemetry store with `FDE_VIEWS` schema |
| **Local LLM** | Ollama (`llama3.1:8b`) | On-premise reasoning engine |
| **Embeddings & Vector Store** | `BAAI/bge-m3` + FAISS/ChromaDB | Local embedding model and vector storage |

---

## 📁 Project Structure

```text
Agentic-Cold-Chain/
├── CLAUDE.md                    # Core System Instruction Set (SDD Rules & Constraints)
├── README.md                    # Project Documentation
├── pyproject.toml               # uv project manifest & dependencies
├── .env.example                 # Environment variables template
│
├── specs/                       # SDD Component Specification Documents
│   ├── architecture.md          # Layer boundaries & state flow diagrams
│   ├── database.md              # View definitions & security contracts
│   ├── tools.md                 # LLM tool input/output schemas
│   ├── rag.md                   # Ingestion pipeline & vector index strategy
│   ├── audit.md                 # Audit log schema & immutability rules
│   └── ui.md                    # Streamlit layout & state specifications
│
├── configs/                     # Application configurations
│   ├── settings.yaml            # Runtime non-secret settings
│   └── logging.yaml             # Structured logging rules
│
├── data/                        # Local data directory (Git-ignored content)
│   ├── sops/                    # PDF/Markdown compliance documents
│   ├── vector_store/            # Persisted FAISS/ChromaDB vector indices
│   └── manifests/               # Ingestion tracking checksums
│
├── docker/                      # Container bootstrap files
│   └── mssql-init/
│       ├── init.sql             # DB Schema & FDE_VIEWS bootstrap
│       └── seed.sql             # Fleet telemetry sample data
│
├── src/                         # Application Source Code
│   ├── core/                    # Configs, state models, constants, exceptions
│   ├── database/                # SQLAlchemy connection engine & audit writer
│   ├── tools/                   # LangGraph tool functions (Fleet, SOP, Weather)
│   ├── rag/                     # Cached embedder, indexer, and retriever
│   ├── agent/                   # ReAct graph, nodes, tool router, and prompts
│   └── ui/                      # Streamlit application entry point & views
│
└── tests/                       # Test Suite
    ├── unit/                    # Unit tests for tools, RAG, and agent nodes
    └── integration/             # End-to-end and database integration tests
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Docker / Docker Desktop** (running)
- **[Ollama](https://ollama.com/)**

---

### 2. Environment Setup

Clone the repository and install dependencies using `uv`:

```bash
# Clone the repository
git clone https://github.com/MoeenUddin01/Agentic-Cold-Chain.git
cd Agentic-Cold-Chain

# Create virtual environment and sync dependencies
uv venv --python 3.12
source .venv/bin/activate
uv sync

# Configure environment variables
cp .env.example .env
```

---

### 3. Database Initialization (MSSQL via Docker)

Start the local MSSQL Server container:

```bash
docker run -v mssql_data:/var/opt/mssql \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=YourStrong!Passw0rd" \
  -p 1433:1433 \
  --name cold-chain-mssql \
  -d mcr.microsoft.com/mssql/server:2022-latest
```

**Install the Microsoft ODBC 18 Driver (Ubuntu/Linux):**
```bash
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc > /dev/null
curl -fsSL https://packages.microsoft.com/config/ubuntu/24.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list > /dev/null
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev
```

Initialize the database schema and ingest raw telemetry data:

```bash
uv run python scripts/ingest_telemetry.py
```

---

### 4. Local LLM Setup (Ollama)

Pull the local reasoning model:

```bash
ollama pull llama3.1:8b
```

---

### 5. Ingestion & Application Run

Build the SOP vector index:

```bash
uv run python src/rag/indexer.py
```

Launch the Streamlit Dispatcher Web Console:

```bash
uv run streamlit run src/ui/app.py --server.port 8501
```

Access the UI in your browser at `http://localhost:8501`.

---

## 🛡️ Security & Governance

1. **Zero-Mutation Rule**: All LLM-generated SQL statements are validated through `validate_sql_safety()` prior to execution. Any query containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, or targeting tables outside `FDE_VIEWS` is instantly halted.
2. **Immutable Audit Trail**: Reasoning steps and tool outputs are recorded to `FDE_VIEWS.AgentAuditLog`. The database user role only possesses `INSERT` privilege on the audit table—`UPDATE` and `DELETE` operations are disabled.
3. **Memory Safety**: Embedding models and LangGraph state graphs are cached using Streamlit's `@st.cache_resource` singleton pattern to prevent memory duplication and OOM errors during UI reruns.
4. **Graceful Degradation**: External API calls (such as Open-Meteo weather forecasts) fail safely with fallback options, ensuring core telemetry monitoring remains functional even during network timeouts.

---

## 🧪 Testing

Run the test suite with `pytest`:

```bash
# Run unit tests
uv run pytest tests/unit -v

# Run full integration test suite
uv run pytest tests/ -v
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
