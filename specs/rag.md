# Phase 4 · Local Vector RAG Specification

> **Phase:** 4  
> **Priority:** P1 — Vector RAG & SOP Ingestion  
> **Module Path:** `src/rag/`  
> **Depends On:** Phase 1 (Core Architecture)  
> **Unlocks:** Phase 6 (UI Presentation)

---

## REQ-RAG-001 — Cached Embedding Model Loader

**Requirement:** The embedding model (`BAAI/bge-m3`) MUST be loaded into memory using `@st.cache_resource` singleton pattern.

**Rationale:** Prevents duplicate model instantiations during Streamlit reruns, eliminating memory leaks and OOM crashes.

**Acceptance Criteria:**
- `src/rag/embedder.py` defines `load_embedding_model()` decorated with `@st.cache_resource`.
- Uses `SentenceTransformer("BAAI/bge-m3")`.
- Instantiates model once per server process.

**Dependencies:** `sentence-transformers`, `streamlit`

**Status:** `[PLANNED]`

---

## REQ-RAG-002 — SOP Document Ingestion Pipeline

**Requirement:** The system MUST provide an offline script `src/rag/indexer.py` to parse, chunk, embed, and index SOP documents from `data/sops/`.

**Rationale:** Converts static PDF/Markdown compliance documents into searchable local vector representations.

**Acceptance Criteria:**
- Reads documents from `data/sops/`.
- Chunks text into 500-token chunks with 50-token overlap.
- Generates embeddings using `BAAI/bge-m3`.
- Persists index to `data/vector_store/` (FAISS index or ChromaDB).

**Dependencies:** `REQ-RAG-001`, `faiss-cpu`

**Status:** `[PLANNED]`

---

## REQ-RAG-003 — Vector Similarity Search Retriever

**Requirement:** `src/rag/retriever.py` MUST expose a similarity search interface to query the persisted vector store.

**Rationale:** Enables semantic retrieval of relevant SOP sections based on dispatcher natural language questions.

**Acceptance Criteria:**
- Loads persisted vector index from `data/vector_store/`.
- Returns top-k matching text snippets with document filename, page/section number, and similarity score.
- Raises `VectorStoreNotInitializedError` if index directory is missing.

**Dependencies:** `REQ-RAG-002`, `REQ-ARC-003`

**Status:** `[PLANNED]`
