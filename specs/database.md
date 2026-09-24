# Phase 2 · Telemetry Database & Security Specification

> **Phase:** 2  
> **Priority:** P0 — Data Layer & Safety  
> **Module Path:** `src/database/`, `docker/mssql-init/`  
> **Depends On:** Phase 1 (Core Architecture)  
> **Unlocks:** Phase 3 (Execution Tools), Phase 5 (Audit Logging)

---

## REQ-DB-001 — MSSQL Container & Bootstrap Infrastructure

**Requirement:** The telemetry database MUST run inside an isolated MSSQL Server 2022 Docker container with schema bootstrap scripts (`init.sql`, `seed.sql`).

**Rationale:** Guarantees local, zero-cost database deployment matching production SQL Server capabilities.

**Acceptance Criteria:**
- `docker/mssql-init/init.sql` creates database `ColdChainDB` and schema `FDE_VIEWS`.
- `docker/mssql-init/seed.sql` populates realistic sample fleet telemetry data.

**Dependencies:** Docker, `mcr.microsoft.com/mssql/server:2022-latest`

**Status:** `[PLANNED]`

---

## REQ-DB-002 — Read-Only Active Fleet View (`VW_ACTIVE_FLEET`)

**Requirement:** The AI agent MUST access vehicle telemetry exclusively through the read-only view `FDE_VIEWS.VW_ACTIVE_FLEET`.

**Rationale:** Prevents direct access to raw underlying tables and abstracts internal table schemas.

**Acceptance Criteria:**
- `FDE_VIEWS.VW_ACTIVE_FLEET` exposes vehicle ID, driver name, current temperature (°C), target temperature range, GPS location, speed, and fuel level.
- Raw tables (`dbo.TBL_SC_FLEET_HIST_RAW`) are hidden from application read/write permissions.

**Dependencies:** `REQ-DB-001`

**Status:** `[PLANNED]`

---

## REQ-DB-003 — Zero-Mutation SQL Execution Guard

**Requirement:** All LLM-generated SQL statements MUST be validated by `validate_sql_safety()` before execution against MSSQL.

**Rationale:** Enforces absolute zero-mutation security, preventing accidental or adversarial data corruption.

**Acceptance Criteria:**
- `validate_sql_safety(sql: str)` verifies statement starts with `SELECT`.
- Regex rejects `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `GRANT`.
- Rejects queries that do not explicitly target `FDE_VIEWS` schema objects.
- Raises `UnsafeSQLError` if any violation occurs.

**Dependencies:** `REQ-ARC-003`

**Status:** `[PLANNED]`

---

## REQ-DB-004 — SQLAlchemy Engine & View ORM Mapping

**Requirement:** Database interaction MUST use SQLAlchemy 2.0 ORM mapped models bound to `pyodbc` driver.

**Rationale:** Provides type-safe query construction and connection pool management.

**Acceptance Criteria:**
- `src/database/connection.py` provides engine factory reading credentials from `src/core/config.py`.
- `src/database/views.py` maps ORM class `ActiveFleetView` to `FDE_VIEWS.VW_ACTIVE_FLEET`.

**Dependencies:** `REQ-ARC-001`, `pyodbc`

**Status:** `[PLANNED]`
