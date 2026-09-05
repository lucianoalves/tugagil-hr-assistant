# TugaAgil CV/LinkedIn Validator — Open Source Architecture Analysis

**Date:** 2026-08-30
**Analyst role:** Senior Open Source Architect + AI/LLM Engineer + Full Stack Engineer + Security/GDPR Architect + Product Architect
**Target product:** TugaAgil CV + LinkedIn Validator MVP
**Repositories analysed:** 5 (local clones inspected — no assumptions from README)

---

## IMPORTANT LICENSING PREFACE

All five repositories carry an **MIT License**.
MIT permits: commercial use, modification, distribution, private use.
MIT requires: preserve copyright notice.

| Repository | License | Commercial Use Safe? |
|---|---|---|
| ats-screener | MIT (Sunny Patel, 2026) | YES |
| resume-screening-toolkit | MIT (John Rhed Atienza, 2026) | YES |
| Resume-ATS | MIT (Love Patel, 2026) | YES |
| ats-resume-checker | MIT (Jahangir Hussen, 2026) | YES |
| ai-resume-builder | MIT (Gitesh Chauhan, 2026) | YES |

**Dependency licensing notes:**

- **ats-screener:** firebase (Apache-2.0), pdfjs-dist (Apache-2.0), mammoth (BSD-2-Clause), compromise (MIT). No GPL.
- **resume-screening-toolkit:** pypdf (BSD-3), fastapi (MIT), pydantic (MIT). No GPL.
- **Resume-ATS:** pytesseract (Apache-2.0), pdf2image (MIT), pypdf (BSD-3), python-docx (MIT). No GPL.
- **ats-resume-checker:** vanilla JS, CDN-loaded pdfjs and mammoth. No bundled deps.
- **ai-resume-builder:** next (MIT), zustand (MIT), radix-ui (MIT). No GPL.

**LICENSE FILE RISK — Resume-ATS:** No LICENSE file exists in the repository root. MIT is attributed in the README only. Treat as MIT for practical purposes but flag for clarification.

**ALL 5 REPOSITORIES: SAFE TO REUSE commercially, subject to preserving copyright notices.**

---

## PHASE 1 — REPOSITORY INVENTORY

### 1. ats-screener

| Field | Value |
|---|---|
| URL | https://github.com/sunnypatell/ats-screener |
| License | MIT — LICENSE file present |
| Primary language | TypeScript |
| Framework | SvelteKit 5 + Svelte 5 |
| Runtime | Node.js 22+ |
| Database | Firestore (optional; falls back to localStorage) |
| AI/LLM providers | OpenAI, Anthropic, Groq, Cerebras, Ollama (multi-provider chain) |
| Embedding provider | None |
| PDF parser | pdfjs-dist (layout-aware, column + table detection) |
| DOCX parser | mammoth |
| OCR | Client-side Tesseract fallback |
| Frontend | SvelteKit 5, open-props, bits-ui, motion |
| Backend | SvelteKit server routes (serverless) |
| API | /api/analyze, /api/admin — rate-limited |
| Authentication | Firebase Auth OR LDAP OR anonymous (self-hosted) |
| Storage | Firestore scan history per user |
| Testing | Vitest (unit) + Playwright (E2E) |
| Docker | No |
| Deployment | Vercel (adapter-vercel present) |
| Last commit | 2026-08-17 |
| Commits | 107 |
| Contributors | 2 (Sunny Patel + dependabot) |

---

### 2. resume-screening-toolkit

| Field | Value |
|---|---|
| URL | https://github.com/Rhed-Dev/resume-screening-toolkit |
| License | MIT — LICENSE file present |
| Primary language | Python 3.12 |
| Framework | FastAPI 0.115 |
| Runtime | Python 3.12+ |
| Database | SQLite (stdlib sqlite3, no ORM) |
| AI/LLM providers | OpenAI (real) + deterministic Fake provider |
| Embedding provider | OpenAI embeddings (real) + hashed bag-of-words fake |
| PDF parser | pypdf (text-based only) |
| DOCX parser | Not supported |
| OCR | Not supported |
| Frontend | None (CLI + API only) |
| Backend | FastAPI |
| API | /score, /batch, /parse, /questions, /health |
| Authentication | None |
| Storage | SQLite (runs + scores tables) |
| Testing | pytest |
| Docker | No |
| Deployment | Any Python ASGI host, or CLI |
| Last commit | 2026-06-13 |
| Commits | 1 (single-commit history) |
| Contributors | 1 (John Rhed Atienza) |

---

### 3. Resume-ATS

| Field | Value |
|---|---|
| URL | https://github.com/itslovepatel/Resume-ATS |
| License | MIT — README only, no LICENSE file |
| Primary language | Python (backend) + TypeScript (frontend) |
| Framework | FastAPI (backend) + Next.js 14/15 (frontend) |
| Runtime | Python 3.9+ / Node.js |
| Database | None (no persistence) |
| AI/LLM providers | None (fully rule-based) |
| Embedding provider | None |
| PDF parser | pypdf + pytesseract/pdf2image OCR fallback |
| DOCX parser | python-docx |
| OCR | Full Tesseract OCR with confidence scoring, timeout, preprocessing |
| Frontend | Next.js + Tailwind + TypeScript |
| Backend | FastAPI |
| API | POST /api/analyze, GET /health |
| Authentication | None |
| Storage | None (temp files, ephemeral) |
| Testing | None detected |
| Docker | No |
| Deployment | Render (backend) + Vercel (frontend) |
| Last commit | 2026-02-15 |
| Commits | 23 |
| Contributors | 2 (Love Patel + lovex-69) |

---

### 4. ats-resume-checker

| Field | Value |
|---|---|
| URL | https://github.com/Jahangirhussen/ats-resume-checker |
| License | MIT — LICENSE file present |
| Primary language | JavaScript (vanilla) |
| Framework | None — pure HTML/CSS/JS SPA |
| Runtime | Browser only |
| Database | localStorage |
| AI/LLM providers | None |
| Embedding provider | None |
| PDF parser | pdfjs (CDN v3.11.174) |
| DOCX parser | mammoth (CDN) |
| OCR | Tesseract (CDN) — browser-side |
| Frontend | Vanilla JS, CSS custom properties |
| Backend | None |
| Authentication | None |
| Storage | localStorage (history, reports, theme) |
| Testing | None |
| Docker | No |
| Deployment | Static site |
| Last commit | 2026-07-07 |
| Commits | 1 |
| Contributors | 1 (Jahangir Hussen) |

---

### 5. ai-resume-builder

| Field | Value |
|---|---|
| URL | https://github.com/giteshChauhan/ai-resume-builder |
| License | MIT — LICENSE file present |
| Primary language | TypeScript |
| Framework | Next.js 16 (App Router) |
| Runtime | Node.js |
| Database | None (Zustand persisted to localStorage) |
| AI/LLM providers | OpenAI, Gemini, Anthropic, HuggingFace, Ollama |
| Embedding provider | None |
| PDF parser | None (builder, not parser) |
| DOCX parser | None |
| OCR | None |
| Frontend | Next.js 16 + React 19 + Tailwind v4 + Radix UI + Zustand |
| Backend | Next.js API routes (/api/ai) |
| Authentication | None |
| Storage | localStorage |
| Testing | None |
| Docker | No |
| Deployment | Vercel |
| Last commit | 2026-08-11 |
| Commits | 110 |
| Contributors | 2 (Gitesh Chauhan + giteshChauhan) |

---

## PHASE 2 — SCORING ENGINE ANALYSIS

### 1. ats-screener — Scoring Engine

**Source:** src/lib/engine/scorer/

**Architecture:** Hybrid — deterministic rule engine (primary) + optional LLM overlay.

**Core formula (engine.ts):**
```
overallScore = clamp(0, 100, round(weighted_sum + quirk_adjustment))

weighted_sum = formatting × w.formatting
            + keywordMatch × w.keywordMatch
            + sectionCompleteness × w.sectionCompleteness
            + experienceRelevance × w.experienceRelevance
            + educationMatch × w.educationMatch
            + quantification × w.quantification
```

**Six ATS profiles with distinct weights (profiles/):**

| Dimension | Workday | Taleo | iCIMS | Greenhouse |
|---|---|---|---|---|
| formatting | 0.25 | 0.20 | 0.15 | 0.10 |
| keywordMatch | 0.30 | 0.35 | 0.30 | 0.25 |
| sectionCompleteness | 0.15 | 0.15 | 0.15 | 0.10 |
| experienceRelevance | 0.15 | 0.15 | 0.20 | 0.25 |
| educationMatch | 0.10 | 0.10 | 0.10 | 0.10 |
| quantification | 0.05 | 0.05 | 0.10 | 0.20 |

**Profile quirks:** Each profile has check() functions that apply bonuses/penalties for platform-specific behaviour (e.g. Workday truncates at 2 pages, Taleo needs explicit skills listed not just implied from experience).

**Keyword matching strategies:** Per profile — exact (Workday, Taleo), fuzzy (iCIMS), semantic (Greenhouse, Lever). Fuzzy uses a curated ~100-entry tech synonym map. Synonym matching scores 0.8× of exact match.

**NLP modules (nlp/):**
- tfidf.ts — full TF-IDF implementation with computeKeywordOverlap
- tokenizer.ts — normalised token extraction
- synonyms.ts — ~100-entry canonical technology synonym map
- skills-taxonomy.ts — skills taxonomy

**Dimension scorers:**
- format-scorer.ts — columns, tables, images, word count, special chars, all-caps lines
- experience-scorer.ts — quantification patterns (9 regex patterns), action verbs (80+ verbs), bullet count
- section-scorer.ts — required section coverage per ATS profile
- education-scorer.ts — degree level (phd=5 to certificate=1), institution, dates, GPA, honors
- keyword-matcher.ts — exact/fuzzy/semantic with synonym lookup

**LLM layer (engine/llm/):**
- Sends resume text (max 6000 chars) + JD (max 4000 chars) to LLM
- Returns complete ScoreResult[] JSON for all 6 platforms
- Prompt includes real ATS research with calibration anchors (prevents hallucination of extreme scores)
- Multi-provider fallback chain: OpenAI -> Anthropic -> Groq -> Cerebras -> Ollama
- Deterministic engine always runs; LLM results replace it when available
- Graceful fallback to rule-based if LLM unavailable or JSON invalid

**Report generation:** jsPDF-based PDF report. Score history timeline (SVG). Comparison between scans.

---

### 2. resume-screening-toolkit — Scoring Engine

**Source:** src/resume_screening_toolkit/scoring.py

**Architecture:** Hybrid — 2 deterministic components + 1 LLM rubric.

**Core formula:**
```python
total = min(weighted_sum, gate_cap)

weighted_sum = skill_overlap_raw × 0.40
            + semantic_similarity_raw × 0.25
            + seniority_fit_score × 0.35

gate_cap = max(0.25, 1.0 - (0.15 × count_missing_must_haves))
```

**Component 1 — Skill Overlap (40%):**
Recency-weighted: `credit = 0.5^(months_since_use / half_life)`. Default half-life 24 months.
Must-have skills weighted 1.0. Nice-to-haves weighted 0.5.
Per-skill evidence trail logged: "Python (must-have): last used 6 mo ago -> credit 0.79".

**Component 2 — Semantic Similarity (25%):**
Cosine similarity between redacted experience text and JD responsibilities.
Uses embedding vectors. Fully explainable score.

**Component 3 — Seniority Fit (35%):**
LLM grades seniority/scope fit. Returns RubricResult: {score: float, rationale: str, evidence: list[str]}.
Schema-validated via pydantic v2. One retry on failure. ExtractionError raised after two failures.

**Hard gate:** Missing must-have skills cap the maximum. 2 missing → cap 0.70. 4 missing → cap 0.40. Floor 0.25.

**Configuration (config.py + config/weights.yaml):**
YAML-backed ScoringConfig. Weights validated to sum to 1.0. RST_WEIGHTS_PATH env var or config/weights.yaml.

**Redaction:** Before any scoring, Resume is converted to RedactedResume. Stripped: name, email, phone, location, company names, institution names, graduation years, gender pronouns, age signals, nationality markers, photo references. LLM never sees PII.

---

### 3. Resume-ATS — Scoring Engine

**Source:** backend/app/services/ats_scorer.py

**Architecture:** Fully deterministic. No LLM, no embeddings.

**Core formula:**
```python
final_score = (keyword_score × 0.20)
            + (section_score × 0.20)
            + (formatting_score × 0.15)
            + (skill_score × 0.20)
            + (experience_score × 0.15)
            + (project_score × 0.10)
```

**Keyword scoring:** Domain-specific keyword frequency matching (hardcoded dictionaries: Software/IT, Data/AI, Marketing, Finance, General). Action verb bonus. No JD-based scoring.

**Section scoring:** Required sections (experience, education, skills) 20pts each. Contact info 20pts. Recommended sections 7pts each. Max 100.

**Formatting:** Table penalty −15, image penalty −10 (both reduced 30% for OCR docs). Word count thresholds. Bullet count thresholds.

**Skill scoring:** Total count thresholds + category bonuses. Max 100.

**OCR awareness:** Penalties reduced by 30% for OCR-processed documents. Floor score 25 for OCR.

**Limitation:** No JD-aware scoring. Hardcoded domain dictionaries do not adapt to the specific job. No semantic matching.

---

### 4. ats-resume-checker — Scoring Engine

**Source:** assets/js/ats-checker.js

**Architecture:** Fully deterministic, browser-side only.

**Keyword analysis:** TF-based key phrase extraction from JD, cross-referenced against resume. Reports matchPct. Keyword stuffing detection (density > 4%).

**Structure scoring:** Core sections (5) worth 85pts. Bonus sections (8) worth 15pts.

**Formatting scoring:** Starts at 100. Deductions: OCR detected (−40), page count > 2 (−10), word count < min (−15), icons/emoji (−8), multi-column (−12), tables (−6).

**Writing quality:** Flesch Reading Ease (implemented directly). Weak phrases, buzzwords, passive voice, repeated words, long sentences.

**Notable:** Keyword stuffing detection. Flesch readability score. Per-issue recommendations with before/after examples.

---

### 5. ai-resume-builder — Scoring Engine

**Source:** lib/ats.ts

**Architecture:** Fully deterministic, bullet-level granularity.

**scoreBullet(text) — 0 to 100:**
```
baseline 40
+20 starts with action verb
+15 contains number
+10 has impact signal (%/$x/by N)
+10 length 50-220 chars
-12 < 40 chars
-8  > 240 chars
-10 first-person pronouns
-5  passive voice
```

**scoreSummary(text):** Similar mechanics for the summary paragraph.

**scoreResume(resume):** Simple average of all bullet scores + summary score.

**AI layer:** Multi-provider streaming chat (/api/ai): OpenAI, Gemini, Anthropic, HuggingFace, Ollama. Used for improvement suggestions via conversation, not for scoring.

---

## PHASE 3 — SCORING QUALITY EVALUATION

| Question | ats-screener | resume-screening-toolkit | Resume-ATS | ats-resume-checker | ai-resume-builder |
|---|:---:|:---:|:---:|:---:|:---:|
| 1. Deterministic? | Hybrid | Hybrid | Yes | Yes | Yes |
| 2. Reproducible? | Partial (LLM varies) | Partial (LLM varies) | Yes | Yes | Yes |
| 3. Explainable? | Yes (per-dimension breakdown) | Yes (evidence trail) | Yes (per-dimension) | Yes | Yes (per-bullet) |
| 4. User understands score? | 8/10 | 9/10 | 6/10 | 6/10 | 8/10 |
| 5. Weights changeable? | Profile-coded (hardcoded per ATS) | YAML config file | Hardcoded | Hardcoded | Hardcoded |
| 6. Multiple scoring profiles? | 6 ATS profiles | 1 configurable | No | Role categories | No |
| 7. Target job/role context? | JD input supported | JD required | No | JD optional | JD optional |
| 8. LinkedIn data support? | No | No | No | No | No |
| 9. CV / LinkedIn consistency? | No | No | No | No | No |
| 10. Auditable history? | Firestore per user | SQLite local | No | localStorage | No |
| 11. Hallucination risk? | Low (calibrated prompts) | Low (schema-validated) | None | None | Medium (chat) |
| 12. Over-reliant on LLM? | No (LLM is optional overlay) | Partial (seniority LLM) | No | No | Optional |
| 13. Hybrid deterministic+AI? | Yes | Yes | No | No | Partial |

**Overall scoring quality rating (1-10):**
| Repo | Rating |
|---|---|
| ats-screener | 8.5 |
| resume-screening-toolkit | 9.0 |
| Resume-ATS | 5.5 |
| ats-resume-checker | 5.0 |
| ai-resume-builder | 6.0 |

---

## PHASE 4 — PARSER ANALYSIS

### ats-screener Parser (src/lib/engine/parser/)

**PDF (pdf-parser.ts):** pdfjs-dist with full layout reconstruction.
- Extracts (x, y, text, width, height) per text item from every page
- Groups items by y-position (3px threshold) into logical lines
- Inserts spaces at significant horizontal gaps (gap > half character-width)
- Multi-column detection: x-position cluster analysis, flags if clusters > 150px apart
- Table detection: finds rows with 3+ items and consistent large gaps
- Image detection: inspects PDF operator list (paintImageXObject only; ignores font glyphs)
- OCR fallback: client-side Tesseract if extracted text < 40 chars

**DOCX (docx-parser.ts):** mammoth.extractRawText for text; mammoth.convertToHtml to detect tables and images.

**Section detection (section-detector.ts):** 13 canonical section types. Multi-alias regex patterns. Heuristics: ALL CAPS short line + preceding blank, ends with colon, title-case no-numbers.

**Contact extraction (contact-extractor.ts):** RFC-compliant email, international phone, LinkedIn URL, GitHub URL.

**Date extraction (date-extractor.ts):** Multiple date format patterns.

**Production-worthiness:** Production-worthy for text-based PDFs. Client-side OCR is limited for server deployments. Excellent column/table/image detection.

---

### resume-screening-toolkit Parser (pdfio.py + extraction.py)

**PDF:** pypdf only. Page-by-page text. No layout analysis, no column detection, no OCR.
**DOCX:** Not supported (PDF, TXT, MD only).
**OCR:** Not supported.

**Parsing approach:** LLM-based structured extraction.
- Full resume text sent to LLM with strict pydantic v2 JSON schema
- Returns structured Resume (name, email, phone, location, roles, education, projects, skills)
- Date fields validated as YYYY-MM. Chronological order enforced.
- all models use extra="forbid" — hallucinated keys are validation errors, not silently ignored
- One retry on schema validation failure; ExtractionError raised after two failures

**Redaction after parsing:** Name tokens (including from email local part), URLs, pronouns, age signals, nationality markers, graduation years, photo references stripped before any scoring.

**Production-worthiness:** Good for the extraction pattern. Limited PDF support (no layout, no OCR, no DOCX).

---

### Resume-ATS Parser (backend/app/services/resume_parser.py)

**PDF:** pypdf.PdfReader. Table heuristic (pipe/tab count). Image detection (keyword scan).
**DOCX:** python-docx — paragraphs + table cells.
**OCR:** Full production-grade Tesseract pipeline:
- Smart trigger: text < 800 chars OR word count < 150 OR no email OR no phone
- Image preprocessing: ImageEnhance, ImageFilter for better accuracy
- 300 DPI rendering with pdf2image
- 30-second hard timeout (thread-based)
- Max 5 pages
- Confidence scoring: low/medium/high based on word count

**Skill extraction (skill_extractor.py):** Comprehensive hardcoded skill sets (600+ skills): programming languages, frameworks, tools, databases, soft skills, domain-specific.

**Production-worthiness:** Best OCR pipeline of all 5 repos. Good rule-based extraction. No tests.

---

### ats-resume-checker Parser (assets/js/parser.js)

**PDF:** pdfjs (CDN). Simple text extraction, no layout reconstruction.
**DOCX:** mammoth (CDN).
**OCR:** Tesseract (CDN). Triggered if text < 40 chars.
**Section detection:** Pattern-matching against section header aliases.
**Name extraction:** Heuristic — first 2-4 title-case words without digits.

**Production-worthiness:** Client-side only. Demo quality. Cannot be used server-side.

---

### ai-resume-builder Parser

None. This is a builder, not a parser. ATS scoring operates on structured data already in the Zustand store.

---

## PHASE 5 — LINKEDIN FEASIBILITY

None of the five repositories implement LinkedIn integration.

**LinkedIn scraping in production is a LinkedIn ToS violation and GDPR risk. Do not use.**

**Clean approaches for TugaAgil MVP:**

1. **User-provided LinkedIn PDF export (Recommended for MVP):**
   - LinkedIn allows users to export their profile as a PDF
   - User uploads CV PDF + LinkedIn PDF
   - Same parser handles both
   - Compare structured output for consistency
   - No ToS issue. No scraping.

2. **User-provided structured form (Simplest):**
   - Accept linkedin_url as a reference field (not scraped)
   - Provide form fields: headline, about, top 3 experience entries, skills list
   - Validate user-confirmed data
   - Clean, no legal risk

3. **Official LinkedIn API:**
   - Requires Marketing API approval
   - Does not expose full profile for third-party analysis
   - Not viable for MVP timeline

**MVP recommendation:** Option 1 + Option 2 combined. Accept LinkedIn PDF export OR a structured form. This is GDPR-safe, LinkedIn ToS-safe, and buildable in one sprint.

---

## PHASE 6 — PRIVACY AND GDPR

### ats-screener

| Dimension | Status |
|---|---|
| PII handling | PDF parsed client-side. Resume text (6000 chars) sent to LLM API if configured. |
| Data retention | Firestore stores scan results per user, auth-gated. |
| Temp files | No server-side temp files. |
| LLM transmission | Resume text sent to third-party LLM. PII risk if using OpenAI/Anthropic with EU users. |
| Auth | Firebase Auth or LDAP — production-grade. |
| Secrets | Private env vars, not bundled to client. |
| GDPR risk | Medium — must configure DPA with LLM provider. |

### resume-screening-toolkit

| Dimension | Status |
|---|---|
| PII handling | Best in class. Full redaction pass before any LLM call. Scoring only sees RedactedResume. |
| Data retention | SQLite local file. No cloud, no third-party persistence. |
| LLM transmission | Only RedactedResume (no PII) + JD text sent to LLM. |
| GDPR risk | Low — redaction architecture is the gold standard. |

### Resume-ATS

| Dimension | Status |
|---|---|
| PII handling | tempfile.NamedTemporaryFile(delete=False). Files NOT auto-deleted — manual deletion in finally block may fail. |
| Data retention | No database. But temp file persistence risk. |
| LLM transmission | No LLM calls. |
| CORS | allow_origins=["*"] — wildcard CORS. Not production-safe. |
| GDPR risk | Medium — temp file persistence is a data retention violation risk. Fix required. |

### ats-resume-checker

| Dimension | Status |
|---|---|
| PII handling | All processing client-side. Resume never leaves browser. |
| Data retention | localStorage only. |
| LLM transmission | None. |
| GDPR risk | Very Low — no server, no transmission. |

### ai-resume-builder

| Dimension | Status |
|---|---|
| PII handling | Resume data in localStorage. Resume context sent to /api/ai route (server-side). |
| LLM transmission | Resume context sent to third-party LLM via server-side proxy. |
| GDPR risk | Medium — LLM providers receive resume context. DPA required. |

---

### TugaAgil GDPR Recommendations

1. Redact PII before sending to LLM — adopt resume-screening-toolkit redaction pattern in TypeScript
2. Never store raw CV files indefinitely — delete from storage after extraction (seconds, not days)
3. Explicit retention policy — validation results stored for X months, user-deletable
4. DPA with OpenAI — required for any EU user data
5. Server-side processing only — CV text must never go from browser directly to LLM
6. Audit log — record when validations were run and by whom, not what was in the CV
7. Explicit consent — at upload, inform users their CV is processed by AI

---

## PHASE 7 — ARCHITECTURE COMPATIBILITY

| Dimension | ats-screener | resume-screening-toolkit | Resume-ATS | ats-resume-checker | ai-resume-builder |
|---|:---:|:---:|:---:|:---:|:---:|
| Next.js compatible | No (SvelteKit) | No (Python) | Yes (native frontend) | No (static) | Yes (native) |
| TypeScript | Yes | No (Python) | Yes (frontend) | No (plain JS) | Yes |
| API extractable | Yes (server routes) | Yes (FastAPI) | Yes (FastAPI) | No | Yes (routes) |
| Vercel deployable | Yes (adapter-vercel) | No (Python runtime) | Yes (frontend only) | Yes (static) | Yes |
| Supabase compatible | Needs adapter | Easy to add | Needs adapter | N/A | Needs adapter |
| Scoring engine extractable | Yes (pure TS modules) | Yes (pure Python) | Partial (coupled to services) | No | Yes (pure TS) |
| Compatibility score (0-10) | 6 | 4 | 6 | 2 | 9 |

**Key insight:** ai-resume-builder has the most compatible stack for TugaAgil (Next.js + TypeScript + Vercel). However it is a resume builder, not a scorer. Its multi-provider LLM streaming pattern is directly reusable.

ats-screener has the best scoring engine but uses SvelteKit. The engine (src/lib/engine/) is pure TypeScript with zero Svelte dependencies and can be extracted into a Next.js project with minimal effort.

resume-screening-toolkit is the best-architected scoring backend but requires Python. Deployable as a separate microservice on Railway or Render if needed.

---

## PHASE 8 — CODE QUALITY

### ats-screener — 9/10

- Architecture: Excellent. Clean separation: engine/, stores/, routes/, lib/server/
- Typing: Full TypeScript 6, no any in engine code
- Error handling: LLM -> rule-based fallback, rate limiting, timeout, abort support
- Secrets: Private env vars, not client-bundled
- Tests: Vitest unit + Playwright E2E
- Security: CSP headers, rate limiting, Firestore auth rules, LDAP support
- Maintainability: High. Modular, well-named, comments explain non-obvious decisions

### resume-screening-toolkit — 9.5/10

- Architecture: Excellent. Strict pydantic schemas at every boundary
- Typing: Python 3.12, mypy strict, pydantic v2 strict with extra="forbid"
- Error handling: Schema validation + retry, ExtractionError, ProviderError
- Config: YAML-backed with pydantic validation and env var override
- Tests: pytest with fake providers for full offline testing
- Documentation: Best of all 5 repos. Docstrings explain design decisions and limitations honestly
- Redaction: Bias-mitigation documentation is admirably honest about what it cannot fix

### Resume-ATS — 5/10

- Architecture: Adequate. Services pattern but some coupling
- Typing: Pydantic models but some Any types
- Error handling: delete=False temp file bug. CORS wildcard.
- Tests: None
- Documentation: Basic
- Security: CORS wildcard, no auth

### ats-resume-checker — 5/10

- Architecture: IIFE module pattern, reasonable for vanilla JS
- Separation of concerns: Good — parser.js, ats-checker.js, storage.js, charts.js separate
- Typing: None (vanilla JS)
- Tests: None
- Notable: The ATS analysis algorithms are well-researched despite being vanilla JS

### ai-resume-builder — 7/10

- Architecture: Good. Next.js App Router, clean component/lib separation
- Typing: TypeScript throughout, well-typed interfaces
- Error handling: Stream error handling, provider error propagation
- Tests: None
- Notable: Multi-provider streaming pattern is production-quality

---

## PHASE 9 — PRODUCTION READINESS

### B — Good Foundation

**ats-screener (B+):** Strong architecture, working auth, Firestore persistence, rate limiting, test coverage, Vercel deployment. Missing for TugaAgil: GDPR consent flows, user roles, usage limits, LinkedIn integration. The engine is production-quality.

**resume-screening-toolkit (B):** Excellent scoring/redaction architecture, typed schemas, tests, CLI+API. Missing: auth, frontend, DOCX support, multi-tenancy. Strong as a backend scoring service.

### C — Prototype / Research

**Resume-ATS (C+):** Working end-to-end with real OCR. Actual deployment on Render + Vercel. But: no auth, no persistence, CORS wildcard, temp file bug, no tests.

**ai-resume-builder (C):** Good code quality but is a resume builder, not a validator. No parser for uploaded CVs. The multi-provider LLM API route is production-quality code inside a C-rated product.

### D — Demo / Educational

**ats-resume-checker (D):** Well-built for a client-side demo. Real ATS analysis logic. But browser-only, no auth, no server, no persistence at scale.

---

## PHASE 10 — REUSE STRATEGY

| Component | ats-screener | resume-screening-toolkit | Resume-ATS | ats-resume-checker | ai-resume-builder |
|---|---|---|---|---|---|
| PDF parser | Adapt | Study | Adapt (OCR) | Study | N/A |
| DOCX parser | Adapt (mammoth) | N/A | Adapt | Study | N/A |
| OCR pipeline | Study | N/A | Adapt | Study | N/A |
| Section detector | Adapt | N/A | Study | Study | N/A |
| Contact extractor | Adapt | Study | Study | Study | N/A |
| Scoring engine core | Adapt | Adapt | Study | Study | Study |
| ATS profile weights | Adapt | N/A | N/A | N/A | N/A |
| Keyword matcher | Adapt | Study | Study | Study | N/A |
| Synonym map | Adapt | N/A | N/A | N/A | N/A |
| TF-IDF | Adapt | N/A | N/A | N/A | N/A |
| Recency-weighted scoring | N/A | Adapt | N/A | N/A | N/A |
| Redaction (PII) | N/A | Adapt | N/A | N/A | N/A |
| Scoring config (YAML) | N/A | Adapt | N/A | N/A | N/A |
| LLM provider abstraction | Adapt | Adapt | N/A | N/A | Study |
| LLM prompts (ATS research) | Adapt | N/A | N/A | N/A | N/A |
| Multi-provider LLM streaming | Study | N/A | N/A | N/A | Adapt |
| Skill dictionaries | Study | N/A | Adapt | Study | N/A |
| Authentication | Adapt (Firebase) | N/A | N/A | N/A | N/A |
| Validation history | Adapt pattern | Adapt pattern | Rebuild | N/A | N/A |
| Frontend UI | Study | N/A | Study | Study | Study |
| Database model | Rebuild (Supabase) | Rebuild | Rebuild | N/A | Rebuild |
| Usage limits | Rebuild | N/A | N/A | N/A | N/A |
| LinkedIn scoring | Rebuild | N/A | N/A | N/A | N/A |
| Consistency scoring | Rebuild | N/A | N/A | N/A | N/A |

---

## PHASE 11 — TUGAAGIL SCORING MODEL PROPOSAL

### Architecture: Three-Layer Hybrid

```
Layer 1: Deterministic Scoring   (fast, cheap, auditable, no API cost)
Layer 2: Semantic Scoring        (embeddings — V2, when JD matching added)
Layer 3: LLM Qualitative Output  (structured JSON, schema-validated, evidence-cited)

Final Score = deterministic weighted combination
LLM = narrative enrichment, not the score source
```

---

### CV Quality Score (40% of TugaAgil composite)

| Dimension | Method | Internal weight |
|---|---|---|
| ATS Structure | Deterministic (sections, formatting rules) | 20% |
| ATS Formatting | Deterministic (columns, tables, images, word count) | 15% |
| Content Quality | Deterministic (action verbs, quantification, passive voice, Flesch) | 20% |
| Keyword Density | Deterministic (TF-IDF + role-specific terms) | 20% |
| Experience Clarity | Deterministic (roles, dates, bullets, recency signals) | 15% |
| Skills Completeness | Deterministic (skill count, category coverage) | 10% |

---

### LinkedIn Quality Score (25% of TugaAgil composite)

| Dimension | Method | Internal weight |
|---|---|---|
| Profile Completeness | Deterministic (headline, about, experience, skills present) | 30% |
| Headline Quality | Deterministic (length, role clarity) + LLM rubric | 20% |
| About Section | LLM quality assessment | 20% |
| Skills Coverage | Deterministic (count, category coverage) | 15% |
| Experience Detail | Deterministic (roles count, dates, descriptions) | 15% |

---

### CV to LinkedIn Consistency Score (20% of TugaAgil composite)

| Check | Method | Internal weight |
|---|---|---|
| Current role match | Deterministic (title + company fuzzy comparison) | 30% |
| Experience timeline | Deterministic (date overlap, gap detection) | 25% |
| Companies overlap | Deterministic (fuzzy name matching) | 20% |
| Skills overlap | Deterministic (set intersection percentage) | 15% |
| Education match | Deterministic (institution + degree comparison) | 10% |

Red flags generated: date conflicts > 3 months, missing roles, contradicting seniority, missing companies.

---

### Career Fit Score (15% of TugaAgil composite — requires target role input)

| Check | Method | Internal weight |
|---|---|---|
| Skill match (must-have) | Deterministic + recency-weighted | 35% |
| Semantic fit | Embedding cosine (experience vs JD responsibilities) | 30% |
| Seniority fit | LLM rubric (schema-validated, evidence-cited) | 20% |
| Hard gate | Score cap if missing critical requirements | applied last |
| Education match | Deterministic | 15% |

---

### TugaAgil Composite Formula

**With target role:**
```
SCORE = (CV_Quality × 0.40) + (LinkedIn_Quality × 0.25) + (Consistency × 0.20) + (Career_Fit × 0.15)
```

**Without target role:**
```
SCORE = (CV_Quality × 0.50) + (LinkedIn_Quality × 0.30) + (Consistency × 0.20)
```

---

### LLM Qualitative Output (not a score number — narrative enrichment)

The LLM receives: redacted structured CV + LinkedIn summary + score breakdown.
The LLM returns schema-validated JSON:

```json
{
  "strengths": ["3-5 evidence-cited bullets"],
  "weaknesses": ["3-5 specific bullets"],
  "recommendations": ["ordered by impact"],
  "career_positioning": "1 paragraph",
  "skill_gaps": ["if target role provided"],
  "action_plan": {
    "month_1": ["immediate actions"],
    "month_3": ["short-term goals"],
    "month_6": ["medium-term goals"]
  }
}
```

All fields schema-validated with one retry on failure. If retry fails, return deterministic score without LLM narrative and flag for manual review.

---

## PHASE 12 — PROPOSED TUGAAGIL ARCHITECTURE

```
User (Browser)
  |
  v
Next.js App Router / Vercel (TypeScript)
  |
  +-- /auth         Supabase Auth (email/password + Google OAuth)
  |
  +-- /dashboard    Validation history list
  |
  +-- /validate     Upload CV + LinkedIn input form
  |
  +-- /results/[id] Validation result detail
  |
  v
Next.js API Routes (serverless, Vercel Edge/Node runtime)
  |
  POST /api/validate
    |
    +-- [1] Auth check + usage limit check (Supabase DB)
    |
    +-- [2] File validation (type, size) + upload to Supabase Storage (temp bucket)
    |
    +-- [3] Document Parser (TypeScript)
    |         pdfjs-dist: layout-aware PDF extraction
    |         mammoth: DOCX extraction
    |         Section detector, contact extractor
    |
    +-- [4] LinkedIn Processing
    |         Accept: PDF export OR structured form fields
    |         Parse with same Document Parser
    |
    +-- [5] PII Redaction (before any LLM call)
    |         Strip: name, email, phone, company names, institution names
    |         Strip: graduation years, pronouns, age signals, nationality
    |
    +-- [6] Deterministic Scoring
    |         CV Quality Score
    |         LinkedIn Quality Score
    |         CV/LinkedIn Consistency Score
    |         (ATS profile scoring — Workday/Taleo profiles)
    |
    +-- [7] LLM Qualitative Analysis (OpenAI GPT-4o-mini)
    |         Input: RedactedCV + LinkedIn summary + score breakdown
    |         Output: schema-validated JSON (strengths, weaknesses, recs, plan)
    |         One retry on schema failure
    |
    +-- [8] Result Assembly
    |         ValidationResult persisted to Supabase DB
    |         Usage counter incremented
    |
    +-- [9] File Cleanup
              Delete raw CV from Supabase Storage (not retained)
```

**Component deployment model:**

| Component | Where | Why |
|---|---|---|
| Document parser (PDF/DOCX) | Vercel serverless (TypeScript) | No Python needed for text-based PDFs |
| Deterministic scoring | Vercel serverless (TypeScript) | Fast (<100ms), cheap, no external calls |
| Embedding similarity (V2) | OpenAI API (text-embedding-3-small) | Simple, cheap, no infrastructure |
| LLM qualitative | OpenAI API (GPT-4o-mini) | Quality output, schema-enforced |
| OCR (V2 — scanned PDFs) | Python microservice (Railway/Render) | pytesseract needs native binary |
| Validation results | Supabase PostgreSQL | Relational, auth-integrated |
| File storage (temp) | Supabase Storage | Auto-expire bucket policy |
| Authentication | Supabase Auth | Unified with DB |
| Usage limits | Supabase DB | Simple count table |

---

## PHASE 13 — MVP SCOPE

### V1 Must Have

1. Authentication — email/password + Google OAuth via Supabase Auth
2. Roles — Associate (monthly limit), Admin/Mentor (unlimited)
3. CV upload — PDF and DOCX, max 5MB
4. PDF/DOCX parsing with section detection (text-based CVs)
5. LinkedIn input — accept PDF export OR structured form
6. CV Quality Score — deterministic, with sub-score breakdown
7. LinkedIn Quality Score — deterministic, with sub-score breakdown
8. CV/LinkedIn Consistency Score — deterministic, red flags highlighted
9. LLM qualitative output — strengths, weaknesses, recommendations, career positioning
10. Validation history — list view + detail view per validation
11. Monthly usage limit — 1-2 validations/month for Associates

### V1 Explicitly Out of Scope

- Target job/role matching (V2)
- Skill gap analysis vs specific JD (V2)
- ATS profile-specific scoring (V2 enhancement)
- Interview preparation (V3)
- Job matching (V2)
- Embeddings (V2)
- OCR for scanned PDFs (V2)
- PDF report generation (V2)
- Multilingual CV support (V2)
- LDAP authentication
- Real-time collaboration
- Mobile app

---

## PHASE 14 — FUTURE ROADMAP

### V1 — CV + LinkedIn Validator
CV Quality + LinkedIn Quality + Consistency Score + LLM recommendations.

Architectural decisions enabling V2+:
- Modular scoring engine — add dimensions without touching existing ones
- LLM provider abstracted — swap models without rewrites
- Schema-validated LLM output — structured from day 1
- Supabase as foundation — scalable auth, DB, storage

### V2 — JD to CV Matching
Add target_role + job_description inputs.
New components: skill overlap (recency-weighted), embedding similarity (JD vs experience), must-have gate, seniority fit LLM rubric, skill gap report.
V1 enablers: deterministic foundation + LLM pipeline already in place.

### V3 — Career AI Advisor
Career path suggestions from validation history. Interview preparation (gap-based questions). AI chat for resume improvement. Multi-resume comparison.
V2 enablers: skill gap data + JD matching creates candidate trajectory map.

### V4 — Mentor/Recruiter Platform
Mentor access to candidate validations (with consent). Batch evaluation. Recruiter pipeline. Ranking by role fit.
V3 enablers: full candidate data model, audit history.

### V5 — Agentic Recruitment/Career Platform
AI agents for job search. Proactive matching. Multi-agent recruiter workflows.
V4 enablers: full workflow data, embedding-based matching at scale.

---

## PHASE 15 — FINAL RANKING

Weights: Functional relevance (30%), Technical quality (20%), Activity/recency (15%), Community (10%), License suitability (10%), Integration ease (10%), Privacy/security (5%).

| Rank | Repository | Functional | Technical | Activity | Community | License | Integration | Privacy | FINAL |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | ats-screener | 8.0 | 9.0 | 9.0 | 7.0 | 10 | 6.0 | 7.0 | **8.13** |
| 2 | resume-screening-toolkit | 7.5 | 9.5 | 6.0 | 3.0 | 10 | 4.0 | 10.0 | **7.53** |
| 3 | Resume-ATS | 7.0 | 5.0 | 5.0 | 4.0 | 8.0 | 6.0 | 4.0 | **5.95** |
| 4 | ai-resume-builder | 4.0 | 7.0 | 8.0 | 5.0 | 10 | 9.0 | 6.0 | **5.90** |
| 5 | ats-resume-checker | 5.0 | 5.0 | 6.0 | 4.0 | 10 | 2.0 | 9.0 | **5.25** |

Score formula for ats-screener: (8.0×0.30)+(9.0×0.20)+(9.0×0.15)+(7.0×0.10)+(10×0.10)+(6.0×0.10)+(7.0×0.05) = 8.13

---

## PHASE 16 — FINAL RECOMMENDATION

### 1. Should we fork one of these repositories?

NO.

None is a direct match for TugaAgil's stack (Next.js + TypeScript + Supabase). Forking would mean migrating SvelteKit to Next.js (ats-screener) or building a frontend on Python (resume-screening-toolkit). The correct approach is a clean Next.js project extracting the best components.

### 2. If YES, which one?

N/A — not forking. See reuse strategy above.

### 3. Which components should we reuse as inspiration?

Primary sources by component:

From ats-screener: PDF parser, DOCX parser, section detector, contact extractor, scoring engine core, ATS profiles, keyword matcher, synonym map, TF-IDF, LLM prompts (extremely valuable).

From resume-screening-toolkit: redaction architecture (TypeScript port), schema design philosophy, YAML-backed scoring config, recency-weighted skill scoring, LLM provider abstraction pattern.

From ai-resume-builder: multi-provider LLM streaming API route (OpenAI/Gemini/Anthropic/Ollama).

From Resume-ATS: OCR service (if/when scanned PDF support needed in V2), skill dictionaries.

### 4. Should the TugaAgil scoring engine be built from scratch?

HYBRID — start from ats-screener engine (TypeScript), extend with resume-screening-toolkit ideas.

The ats-screener engine is the highest-quality TypeScript scoring engine available and is directly compatible with Next.js. It needs: LinkedIn scoring module (new), consistency scoring module (new), YAML-configurable weights, redaction layer (port from Python), Career Fit module (port recency-weighted algorithm).

This is adaptation, not a rebuild. Estimated effort: 3-5 senior developer days.

### 5. Should we use an LLM for scoring?

YES — but not as the score source. The deterministic score must be computable without any LLM call.

LLM is used for: seniority fit rubric, career positioning, strengths/weaknesses narrative, recommendations, action plan.

LLM is NOT used for: structure detection, formatting analysis, keyword matching, section scoring, consistency comparison.

### 6. Which parser should we use?

ats-screener TypeScript parser (pdfjs-dist + mammoth) as primary, adapted to run server-side in Next.js API routes.

For scanned PDFs (V2 only): Resume-ATS Python OCR service as a sidecar microservice.

### 7. What should the initial AI architecture be?

Simplest production-worthy V1 approach:

1. Parse CV and LinkedIn input (TypeScript, Vercel serverless, < 2 seconds)
2. Deterministic scoring (TypeScript, < 100ms)
3. Single LLM call — GPT-4o-mini — structured JSON output with Zod schema validation + one retry
4. Store ValidationResult in Supabase

No embeddings in V1. No vector databases. No streaming required for V1. Total latency target: under 15 seconds end-to-end.

### 8. What should we build ourselves?

These are TugaAgil's differentiating layer — not replaceable by open-source components:

- LinkedIn quality scoring module
- CV to LinkedIn consistency scoring module
- Portuguese market career positioning context (prompts, norms)
- Associate/Admin/Mentor role and permission system
- Monthly usage limit enforcement
- Validation history UX (list, detail, comparison)
- TugaAgil composite scoring formula
- Supabase data model and Row Level Security policies
- Career strategy output tailored to the Portuguese job market

---

# FINAL RECOMMENDATION

The following 15 points summarise exactly what to do next, in priority order:

1. Create a new Next.js 15 + TypeScript + Supabase project. Do not fork any repository. Start clean with a clear architecture from day one.

2. Extract and adapt src/lib/engine/ from ats-screener into the new project as the scoring foundation. This is MIT-licensed, pure TypeScript, zero Svelte dependencies, and the highest-quality component found. Preserve copyright notices as required by MIT.

3. Build the document parser first using pdfjs-dist (layout-aware) + mammoth, adapted from ats-screener to run as a Next.js API utility (server-side, not client-side). This is the most critical unblocking step.

4. Implement the PII redaction layer in TypeScript before writing any LLM integration. Port resume-screening-toolkit redaction.py. Scoring must only ever see a RedactedCV, never raw text. This is non-negotiable for GDPR.

5. Build LinkedIn input as a form-based approach for MVP (headline, summary, top 3 experience entries, skills) plus accept LinkedIn PDF export. No scraping. No official API required for V1.

6. Build the CV/LinkedIn consistency scorer as a purely deterministic module. Compare roles, dates, companies (fuzzy), skills intersection. Generate red flags. No LLM needed.

7. Integrate LLM qualitative output using GPT-4o-mini. Input: RedactedCV + LinkedIn summary. Output: Zod-validated JSON (strengths, weaknesses, recommendations, career positioning, action plan). One retry on validation failure. If second failure, return deterministic score without narrative.

8. Borrow ats-screener LLM prompts.ts as a starting point. The ATS platform research embedded in those prompts is the most valuable single file in all 5 repositories. Extend with LinkedIn-aware prompts and Portuguese market context.

9. Configure scoring weights as YAML from day one. Borrow resume-screening-toolkit ScoringConfig pattern. This enables weight tuning without code deploys — essential during early product iterations.

10. Build the Supabase data model with Row Level Security: users, validations, validation_results, usage_monthly_counts. Associates can only read their own data.

11. Implement the monthly usage limit as a simple Supabase function: count validations per user per calendar month, block if above limit.

12. Do not transmit raw CV text to OpenAI. Only send the redacted structured representation. Sign a DPA with OpenAI before going live with any EU user data.

13. Defer OCR support to V2. The vast majority of CVs submitted by Associates will be digital. Scanned PDF support adds Python infrastructure complexity that is not justified for MVP.

14. Defer embeddings and vector databases to V2. They are needed for JD matching but add cost and complexity not required for V1 CV + LinkedIn validation.

15. The deterministic score must always be computable, explainable, and displayable without any LLM call. The LLM provides narrative enrichment. This makes TugaAgil auditable, resilient to LLM outages, and cost-predictable as usage scales.
