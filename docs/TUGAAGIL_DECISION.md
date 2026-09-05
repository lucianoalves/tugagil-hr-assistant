# TugaAgil — Architecture Decision Record

**Date:** 2026-08-30
**Scope:** CV + LinkedIn Validator MVP
**Based on:** TUGAAGIL_OPEN_SOURCE_ANALYSIS.md (full analysis of 5 open-source repositories)

---

## 1. FINAL RANKING

| Rank | Repository | Weighted Score | Key Strength |
|:---:|---|:---:|---|
| 1 | ats-screener | 8.13 | Best TypeScript scoring engine + LLM hybrid + Vercel-native |
| 2 | resume-screening-toolkit | 7.53 | Best architecture + GDPR redaction + explainable scoring |
| 3 | Resume-ATS | 5.95 | Best OCR + production Next.js + FastAPI combo |
| 4 | ai-resume-builder | 5.90 | Best multi-provider LLM streaming + Next.js native |
| 5 | ats-resume-checker | 5.25 | Best client-side demo + ATS analysis algorithms |

All 5 repositories are MIT-licensed and safe for commercial reuse.

---

## 2. RECOMMENDED REPOSITORIES / COMPONENTS

### Primary: ats-screener (adapt)
- PDF parser with layout reconstruction — pdfjs-dist, column/table/image detection
- DOCX parser — mammoth
- Section detector (13 section types, multi-alias regex + heuristics)
- Contact extractor (email, phone, LinkedIn, GitHub)
- Scoring engine — format scorer, experience scorer, keyword matcher, education scorer
- ATS profiles — Workday, Taleo, iCIMS, Greenhouse, Lever, SuccessFactors with distinct weights
- NLP modules — TF-IDF, synonym map (100+ tech entries), tokenizer
- LLM prompts — research-backed ATS platform analysis prompts (most valuable single file)
- Multi-provider LLM chain with fallback and rate limiting

### Secondary: resume-screening-toolkit (adapt)
- PII redaction architecture (name, email, phone, company, pronouns, nationality, age, photos)
- YAML-backed scoring configuration with pydantic validation
- Recency-weighted skill scoring (exponential decay, half-life 24 months)
- LLM provider abstraction (Protocol pattern, fake provider for offline testing)
- Schema-validated LLM extraction with one retry on failure

### Tertiary: ai-resume-builder (adapt)
- Multi-provider streaming LLM API route pattern (OpenAI/Gemini/Anthropic/HuggingFace/Ollama)

### Tertiary: Resume-ATS (study/V2)
- OCR service — Tesseract with confidence scoring, timeout, preprocessing (defer to V2)
- Skill dictionaries — 600+ skills across 6 categories

---

## 3. RECOMMENDED ARCHITECTURE

```
Next.js 15 + TypeScript + Supabase + Vercel

User
 |
 v
Next.js / Vercel
 |
 +-- Supabase Auth (email/password + Google OAuth)
 |
 +-- /validate  (upload CV + LinkedIn input)
 |
 v
Next.js API Route: POST /api/validate
 |
 +-- [1] Auth check + usage limit (Supabase DB)
 +-- [2] File upload to Supabase Storage (temp, auto-expire)
 +-- [3] Document Parser (TypeScript — pdfjs-dist + mammoth)
 +-- [4] LinkedIn Processing (PDF export OR form fields)
 +-- [5] PII Redaction (BEFORE any LLM call)
 +-- [6] Deterministic Scoring
 |         CV Quality Score
 |         LinkedIn Quality Score
 |         CV/LinkedIn Consistency Score
 +-- [7] LLM Qualitative Analysis (GPT-4o-mini, schema-validated JSON)
 +-- [8] Assemble ValidationResult -> Supabase DB
 +-- [9] Delete raw CV from Storage
 |
 v
ValidationResult
 +-- CV Score (0-100) + sub-scores
 +-- LinkedIn Score (0-100) + sub-scores
 +-- Consistency Score (0-100) + red flags
 +-- Strengths (3-5 bullets)
 +-- Weaknesses (3-5 bullets)
 +-- Recommendations (ordered by impact)
 +-- Career Positioning (paragraph)
 +-- Action Plan (1/3/6 month milestones)
```

---

## 4. RECOMMENDED MVP STACK

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | Next.js 15 (App Router) + TypeScript | Most compatible with all adapted components |
| Styling | Tailwind CSS v4 | Fast iteration, consistent |
| State | Zustand or React Query | Lightweight, proven |
| Backend | Next.js API Routes (serverless) | No separate backend needed for V1 |
| Auth | Supabase Auth | Unified with DB, OAuth built-in |
| Database | Supabase PostgreSQL | Relational, Row Level Security, real-time |
| File Storage | Supabase Storage | Integrated, auto-expire buckets |
| PDF Parsing | pdfjs-dist (server-side) | Layout-aware, TypeScript native |
| DOCX Parsing | mammoth | MIT, simple, reliable |
| Scoring Engine | TypeScript (adapted from ats-screener) | Pure TS, no runtime dependency |
| LLM | OpenAI GPT-4o-mini | Fast, cheap, sufficient quality for V1 |
| LLM Validation | Zod schema validation + 1 retry | No hallucinated fields |
| Deployment | Vercel | Serverless, Next.js native |

---

## 5. BUILD VS REUSE DECISION

### Reuse / Adapt (do not build from scratch)

| Component | Source | Effort |
|---|---|---|
| PDF/DOCX parser | ats-screener engine | 1 day |
| Section detector | ats-screener engine | 0.5 days |
| Contact extractor | ats-screener engine | 0.5 days |
| Formatting scorer | ats-screener engine | 0.5 days |
| Experience scorer | ats-screener engine | 0.5 days |
| Keyword matcher + synonyms + TF-IDF | ats-screener engine | 1 day |
| ATS profiles (Workday/Taleo etc.) | ats-screener engine | 0.5 days |
| PII redaction layer | resume-screening-toolkit | 1 day |
| Scoring config (YAML weights) | resume-screening-toolkit | 0.5 days |
| Recency-weighted skill scorer | resume-screening-toolkit | 1 day |
| Multi-provider LLM API route | ai-resume-builder | 0.5 days |
| LLM prompts foundation | ats-screener prompts.ts | 1 day (extend) |

### Build from scratch (TugaAgil proprietary layer)

| Component | Effort |
|---|---|
| LinkedIn quality scoring module | 2-3 days |
| CV/LinkedIn consistency scorer | 2 days |
| TugaAgil composite scoring formula | 1 day |
| Associate/Admin/Mentor role system | 1-2 days |
| Monthly usage limit system | 1 day |
| Validation history UX | 2-3 days |
| Portuguese market LLM prompts | 1-2 days |
| Supabase data model + RLS policies | 1-2 days |
| Overall application UX/UI | 5-8 days |

**Estimated V1 total: 3-4 weeks for a senior developer working full-time.**

---

## 6. MAIN RISKS

| Risk | Severity | Mitigation |
|---|---|---|
| GDPR: raw CV text sent to OpenAI | HIGH | Implement PII redaction before any LLM call. Sign DPA with OpenAI. |
| LinkedIn legal: scraping ToS violation | HIGH | Use PDF export or form input only. Never scrape. |
| Scoring validity: LLM produces inconsistent scores | MEDIUM | LLM is NOT the score. Deterministic scoring is always the score. LLM only provides narrative. |
| Parser quality: complex CV layouts | MEDIUM | pdfjs-dist handles layout well but some edge cases will fail. OCR deferred to V2. |
| Resume-ATS license: no LICENSE file | LOW | README attributes MIT. Treat as MIT. Use only for inspiration/patterns, not direct code copy. |
| LLM cost at scale | MEDIUM | Use GPT-4o-mini (cheap). Deterministic scoring runs without LLM if needed. Usage limits cap cost. |
| Scanned CVs (V1) | LOW | Not supported in V1. Users prompted to upload digital CVs. |
| Dependency drift (pdfjs-dist) | LOW | Pin versions. Review on major pdfjs updates. |

---

## 7. NEXT STEPS (in priority order)

1. Create new Next.js 15 + TypeScript project with Supabase integration
2. Set up Supabase: Auth, database schema, Storage buckets, Row Level Security
3. Extract src/lib/engine/ from ats-screener into the new project (MIT — preserve copyright)
4. Adapt PDF/DOCX parser to run server-side in Next.js API routes
5. Port PII redaction from resume-screening-toolkit Python to TypeScript
6. Build LinkedIn input: accept PDF export + structured form (no scraping)
7. Build CV/LinkedIn consistency scorer
8. Build LinkedIn quality scorer
9. Implement TugaAgil composite scoring formula with YAML-backed weights
10. Integrate GPT-4o-mini with Zod-validated structured output + one retry
11. Extend LLM prompts from ats-screener with LinkedIn context + Portuguese market framing
12. Build role system (Associate/Admin/Mentor) and usage limits
13. Build validation history list + detail views
14. Sign DPA with OpenAI before any production use with EU users
15. Internal testing with real CVs before opening to Associates

---

# FINAL RECOMMENDATION

- **Do NOT fork** any repository. Start clean.
- **Primary source:** ats-screener scoring engine + parser (TypeScript, adapt to Next.js)
- **Secondary source:** resume-screening-toolkit redaction + config patterns (port to TypeScript)
- **Scoring:** Deterministic always. LLM for narrative enrichment only.
- **Stack:** Next.js 15 + TypeScript + Supabase + Vercel + OpenAI GPT-4o-mini
- **LinkedIn:** PDF export or form input. No scraping. No official API needed for V1.
- **GDPR:** Redact before LLM. Delete files after extraction. DPA with OpenAI.
- **V1 focus:** CV quality + LinkedIn quality + consistency + LLM narrative. Nothing more.
- **Timeline estimate:** 3-4 weeks to a working MVP, single senior developer.
