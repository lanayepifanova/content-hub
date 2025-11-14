# Creator RAG Engine (WIP)

This repository is being transformed into a Retrieval-Augmented Generation (RAG) assistant for academic and technical creators who need high-signal hooks, outlines, and scripts without living inside ideation docs all day. The long-term goal is a personalized content memory that understands your story, tone, and aspirational audience (STEM majors, student founders, hacker-house builders, ambitious college students) and can surface relevant ideas on demand.

> ⚠️ Current code still runs the legacy calendar/brief app. The documentation below describes the target system and the implementation plan guiding the migration.

---

## Vision

- **Personalized memory**: ingest every artifact you produce (threads, scripts, analytics, voice notes) and index them in a relational + vector store so the model can cite your own material when drafting.
- **Audience-aware generation**: every response is grounded in your style plus the specific personas you attract, ensuring hooks align with the high-achieving academic/tech crowd.
- **Pattern insights**: the system continuously analyzes top-performing posts to learn which structures, cadences, and CTAs resonate so it can recommend blueprints instead of generic advice.
- **Idea → Script pipeline**: you ask for a topic, the engine retrieves precedent, proposes hook variations, expands them into outlines/scripts, and tracks provenance.

---

## Architecture Pillars

1. **Memory Architecture**
   - Ingest tweets, long-form scripts, newsletters, Notion pages, audio transcripts, and performance analytics.
   - Store raw text in object storage, metadata in Postgres, and semantic representations in a vector DB (pgvector or Pinecone).
   - Maintain persona profiles (you + micro-audiences) for grounding prompts.

2. **Retrieval Layer**
   - Multi-hop retrieval: metadata filter (content type, performance tier, persona) → dense similarity search.
   - Hybrid ranking (BM25 + embeddings) ensures factual snippets and stylistic cues are both surfaced.
   - Scheduled pattern-mining jobs cluster high-performing hooks to generate “recipes.”

3. **Generation Stack**
   - Prompt schema: system message with persona + instructions, contextual snippets, and explicit task formatting (hooks, outline, CTA, script).
   - Primary LLM: GPT‑4.1 (or equivalent). Later phases may fine-tune adapters using your archive.
   - Output validators enforce JSON so UI blocks render consistently.

4. **Analytics & Pattern Locator**
   - Feature extraction per post: hook archetype, pacing, CTA type, sentiment, etc.
   - Correlate features with retention metrics (watch time, CTR) to highlight winning structures.
   - Insight queries like “Which hook formats over-index for STEM majors?” feed both dashboards and generation prompts.

5. **User Workflow**
   - Dashboard replaces the calendar: idea stream, memory search, and pattern pulses.
   - Brief builder auto-fills outlines/scripts with cited snippets and suggestions for B-roll + CTAs.
   - Feedback panel lets you up/down vote generated ideas to reinforce preferences.

6. **Data Flow**
   1. Ingest sources via API/webhooks/manual uploads.
   2. Normalize → embed → persist in vector + relational stores.
   3. On request, filter + retrieve + compose prompt + call LLM.
   4. Store generated assets with provenance and feed performance back into analytics.

7. **Implementation Tips & Stack**
   - FastAPI backend, Postgres/pgvector, object storage (S3), Celery/RQ for ingestion + analytics workers.
   - Embeddings: `text-embedding-3-large` (or similar) for semantic search.
   - RAG caching layer to memoize frequent intents (“give me 5 study hooks”).
   - Security: encrypt archive at rest; prefer self-hosted deployment for IP-heavy data.

---

## Implementation Plan

| Phase | Focus | Key Deliverables |
| --- | --- | --- |
| 0. Stabilize | Preserve current app while scaffolding new services. | Document migration plan (this file), add feature flagging, ensure deploy pipeline ready for schema changes. |
| 1. Memory Ingestion | Capture and normalize creator assets. | Ingestion APIs, asset metadata schema, embedding + storage jobs, persona profile definitions. |
| 2. Retrieval Stack | Build multi-hop search + pattern miner. | Hybrid retriever service, analytics jobs that cluster top posts, pattern recipe store. |
| 3. Generation Engine | Wire RAG pipeline + output contracts. | Prompt templates, GPT‑4.1 integration, JSON schema for hooks/outlines/scripts, provenance logging. |
| 4. Insights Layer | Ship analytics views and pattern surfacer. | Feature extraction workers, reporting endpoints (“what worked last week”), dashboard cards. |
| 5. Creator UI | Replace calendar with RAG dashboard. | Idea feed, memory search bar, script workspace, feedback mechanisms. |
| 6. Feedback & Loop Closure | Teach the system over time. | User rating signals, publish-event ingestion, automatic performance backfill updating pattern stats. |
| 7. Polish & Scale | Monitoring, security, extensibility. | Encryption, audit logs, per-persona prompts, multi-creator tenancy. |

Each phase should land in small PRs (e.g., Phase 1 can be broken into ingestion schema → worker pipeline → admin upload UI). Legacy calendar routes can be deprecated once Phase 5 ships.

---

## Development Notes

- **Running the legacy app**: `./run.sh` still starts the FastAPI + SQLite calendar for now.
- **Testing**: `pip install -e ".[dev]" && pytest`.
- **Next actions**: begin Phase 1 by defining ingestion tables + background workers; track progress in issues/PRs referencing this plan.
