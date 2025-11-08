# Content Strategist Brainstorm Blueprint

This repository now serves as a living blueprint for building an autonomous “content strategist / scriptwriter” that ships new hooks and short-form scripts every day. Use it as a master plan rather than vendor-specific code.

---

## 1. Mission & Success Criteria

**Goal:** Generate daily, on-brand content ideas (hooks) plus example scripts grounded in a durable profile of you, your offers, and your audience.

**Daily Definition of Done**
- ≥3 fresh hook + script pairs delivered before 9am local time.
- Each idea references at least one fact from your personal knowledge base.
- Included script follows your voice/tone guidelines and ends with a CTA.
- Logged to a searchable archive with metadata (pillar, format, status, performance).

---

## 2. Knowledge Base & Inputs

| Layer | Purpose | Example Data Points | Storage Options |
|-------|---------|---------------------|-----------------|
| Profile | Immutable identity & POV | Bio, credentials, values, taboo topics | `profile.yaml`, Notion DB |
| Content Pillars | Strategic buckets | Mindset, Creator Ops, Tools, Lifestyle | Google Sheet, Airtable |
| Proof Library | Authority receipts | Client wins, stats, testimonials, “I did X” stories | Markdown vault, Firestore |
| Raw Knowledge | Long-form references | Newsletter archive, call transcripts, research links | Obsidian vault, vector DB |
| Performance Log | Feedback loop | Views, saves, shares, comments per post | PostHog, Supabase, CSV |

**Normalization Tips**
- Convert every text asset into semantic chunks (300–500 tokens) and store embeddings in a vector DB (Pinecone, Weaviate, LanceDB).
- Tag each chunk with `pillar`, `tone`, `persona stage`, `source`, `freshness_score`.
- Snapshot personal context quarterly; version profile data so the strategist can compare “current vs previous” narrative angles.

---

## 3. System Architecture (High-Level)

```
            ┌────────────┐
 Input ---> │ Ingestion  │ -- cleans/tags --> Vector Store / KV Store
 Schedules  └────────────┘
                 │
                 ▼
          ┌────────────┐
          │ Idea Forge │ -- generates hooks via templates + LLM
          └────────────┘
                 │
                 ▼
          ┌────────────┐
          │ Script Lab │ -- drafts intro/story/CTA
          └────────────┘
                 │
                 ▼
          ┌────────────┐
          │ QA + Rank  │ -- scores, dedupes, selects top N
          └────────────┘
                 │
                 ▼
          ┌────────────┐
          │ Delivery   │ -- email/Notion/Slack + archive
          └────────────┘
```

### Core Services
1. **Ingestion Daemon** – nightly cron that watches folders, transcripts, analytics exports, then normalizes & embeds content.
2. **Idea Forge** – orchestrator that mixes heuristics (pillar rotation, trend prompts) with LLM calls to pitch hooks.
3. **Script Lab** – builds 30–90s scripts using hook templates, structured storytelling, and CTA logic.
4. **Memory + Feedback Loop** – stores outcomes, tracks what resonated, feeds back into idea weighting.
5. **Scheduler & Delivery** – runs at set times, posts to Slack/Notion/email, and opens tasks in your task manager.

---

## 4. Hook Generation Playbook

**Hook Framework Library**
- Pattern Break: “Everyone says X, but here’s why they’re wrong.”
- Proof → Promise: “I scaled to $Y in Z days — here’s the exact lever.”
- Future Cast: “In 90 days, this will separate creators who win vs fade.”
- Relatable Pain: “If you’re still doing __, you’re burning audience trust.”
- Demystify Process: “The 3-layer prompt stack I use before filming anything.”

**Rotation Logic**
1. Pull top 2 under-served pillars (lowest last-14-day coverage).
2. For each pillar, sample 3 knowledge chunks with high freshness scores.
3. Feed chunks + hook frameworks into an LLM prompt that enforces:
   - Include one personal proof point.
   - Mention transformation/benefit explicitly.
   - Limit to ≤120 characters.
4. De-duplicate against last 30 hooks (cosine similarity threshold 0.88).

**Example Prompt Snippet**
```
You are Lana’s content strategist. Using the context below, craft 5 hook options.
Constraints:
- Tone: candid, practical, slightly spicy.
- Include exactly one proper noun per hook.
- Tie each hook to the stated pillar.

Context:
<pillar_summary>
<proof_chunk>
<audience_pain>
```

---

## 5. Script Builder Blueprint

**Script Anatomy (45–60s short-form)**
1. **Hook (0–3s)** – from Idea Forge output.
2. **Credibility Snap (3–6s)** – “I … / My client …”
3. **Insight Stack (6–35s)** – 2–3 actionable beats referencing knowledge chunks.
4. **Story or Example (35–50s)** – quick anecdote or micro case study.
5. **CTA (50–60s)** – nudge to DM, comment keyword, join list, etc.

**Template JSON**
```json
{
  "hook": "",
  "credibility": "",
  "beats": [
    {"point": "", "supporting_fact": "", "source": ""},
    {"point": "", "supporting_fact": "", "source": ""}
  ],
  "story": {"setup": "", "conflict": "", "resolution": ""},
  "cta": {"copy": "", "destination": "", "urgency": ""}
}
```

**Example Output**
```
Hook: “Your content calendar dies because you brainstorm on empty.”
Cred: “I ship 20+ pieces a week without recycling scripts.”
Beat 1: Map a ‘Recurring Scenes’ list so ideas spawn from lived moments. (Source: personal SOP)
Beat 2: Tag every win/loss with emotions to recycle angles, not words. (Source: test data)
Story: “January launch flopped until we tagged buyer anxieties; next drop → 4.1x sales.”
CTA: “Comment STRATEGIST to steal the tagging template.”
```

---

## 6. Daily Automation Flow

1. **06:00 – Refresh memory**  
   - Sync any overnight notes or analytics exports.  
   - Re-run embeddings for changed docs.
2. **06:10 – Idea Forge**  
   - Select pillars via rotation logic; call LLM with context.  
   - Score hooks on novelty, clarity, alignment (0–5 scale each).
3. **06:20 – Script Lab**  
   - For top 3 hooks, draft scripts using template + relevant chunks.  
   - Run toxicity + duplication checks.
4. **06:30 – QA + Human-in-the-loop**  
   - Post summary to Slack with buttons (Approve / Edit / Discard).  
   - If no response by 08:30, auto-approve best-scoring set.
5. **06:35 – Archive & Tasks**  
   - Log outputs to Notion/Airtable with metadata.  
   - Create tasks in Asana/Todoist with due date + direct link.
6. **Post-Publish**  
   - Listen for performance metrics (views, saves, DM volume).  
   - Update performance log to influence future scoring weights.

---

## 7. Data & Storage Design

### Files / Tables
- `profile.yaml` – persona voice, do/don’t list, offers, CTAs.
- `pillars.csv` – columns: `pillar`, `subpillar`, `weight`, `last_used_at`.
- `knowledge_chunks.parquet` – embeddings + metadata.
- `performance_log.csv` – `date`, `platform`, `hook_id`, `reach`, `saves`, `leads`.
- `daily_outputs/2024-05-01.json` – final hook+script sets per day.

### Metadata Fields (per chunk)
| Field | Description |
|-------|-------------|
| `chunk_id` | UUID for reference in scripts |
| `pillar` | Primary strategic category |
| `tone` | e.g., “spicy”, “mentor”, “scientist” |
| `persona_stage` | Awareness stage (Problem / Solution / Product) |
| `freshness_score` | 0–1 decay based on last use |
| `proof_ref` | Link to full testimonial/data |

---

## 8. Implementation Blueprint

**Tech Stack Options**
- **Orchestrator:** Temporal, Airflow, or simple cron + Python script.
- **Processing:** Python (LangChain/LlamaIndex) or TypeScript (LangGraph, Vercel AI SDK).
- **Vector DB:** Open-source (LanceDB, Chroma) or managed (Pinecone).
- **Prompt Hosting:** OpenAI, Anthropic, local LLM via Ollama (for privacy).
- **Delivery:** Slack bot, Notion API, Email (Postmark), SMS (Twilio).

**Pseudocode**
```python
def run_daily_brainstorm():
    profile = load_yaml("profile.yaml")
    pillars = load_pillars("pillars.csv")
    memory = query_vector_store(pillars)

    hooks = idea_forge(profile, pillars, memory)
    scripts = []
    for hook in hooks[:3]:
        context_chunks = fetch_supporting_chunks(hook)
        script = build_script(profile, hook, context_chunks)
        score = score_script(script, performance_log())
        scripts.append({"hook": hook, "script": script, "score": score})

    deliver(to="Slack", payload=scripts)
    archive_outputs(scripts)
```

**Scoring Heuristics**
- `novelty = 1 - cosine_similarity(hook_embedding, archive_embeddings)`
- `alignment = rubric(profile.voice, script)`
- `performance_boost = rolling_avg_performance(pillar)`
- Final score = `0.4*novelty + 0.4*alignment + 0.2*performance_boost`

---

## 9. Expansion Ideas

- **Interactive Brief Builder:** Ask you 3 questions nightly to inject fresh stories.
- **Auto-B-Roll Suggestions:** Tag each script beat with B-roll or prop ideas.
- **Trend Listener:** Scrape trend reports/Twitter lists to seed hook prompts.
- **Campaign Memory:** Group hooks into weekly campaign arcs with escalating CTAs.
- **Distribution Assistant:** Auto-queue approved scripts into social schedulers.

---

## 10. Next Steps Checklist

1. Document your profile & offers inside `profile.yaml`.
2. Gather 50–100 knowledge artifacts; run through an embedding pipeline.
3. Configure a vector store + metadata DB.
4. Build the cron job that runs the pipeline + posts to your chosen surface.
5. Track performance and keep feeding the strategist new proof points.

This blueprint should give you everything needed to turn the repository into a thinking partner that never runs out of hooks or scripts. Customize the components, but keep the daily cadence + knowledge-grounding principles intact.
