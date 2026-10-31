# RAG Pipeline

An async, distributed RAG (retrieval-augmented generation) pipeline: ingest documents from URLs, chunk and embed them in parallel, store them in a vector DB, and answer questions grounded in what was ingested. Demo corpus: the Indian Constitution.

## Tech stack
Python, Django, Celery, Redis, Dask, LangChain, ChromaDB, Sentence-Transformers, OpenAI, Docker.

## How it works

**Ingestion (async, fanned out).** `POST` a batch of file URLs → each one becomes an `IngestionLog` row (`PENDING`) → a Celery `group` dispatches one `process_url` task per URL in parallel, not sequentially. Each task loads the document, and splits it into overlapping chunks (LangChain's `RecursiveCharacterTextSplitter`) via **Dask**, so chunking itself is parallelized across a document's pages rather than done chunk-by-chunk on one core. Chunks are embedded (`SentenceTransformer` locally, swappable for OpenAI embeddings) and written into a **ChromaDB** collection. Each log's status moves `PENDING → STARTED → DONE`/`FAILED` independently, so a batch's progress is queryable (`GET` ingestion-status by `batch_id`) while it's still running.

**Retrieval + generation.** A question is embedded and matched against the Chroma collection (`collection.query`, top-5 by similarity). The retrieved chunks become the grounding context for a call to OpenAI (`gpt-3.5-turbo`) — the answer is only generated from what was actually retrieved, not from the model's own unguided knowledge. Every question/answer pair is persisted (`Chat` model) for later review.

**Supporting pieces:** a custom `async_retry_and_timeout` decorator (bounded retries + timeout around async DB calls, raising a typed `ServiceException` instead of letting a hang propagate) and a custom async-aware response-caching decorator for Django views.

## Running locally

```bash
git clone https://github.com/m0s0m0/rag-pipeline.git
cd rag-pipeline
make build_local
make up_local
```

Needs `OPENAI_API_KEY` set in your environment — nothing is hardcoded in this repo.

## Code quality
flake8-checked.
