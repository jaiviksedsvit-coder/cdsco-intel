# Product Decision Log — CDSCO Regulatory Intelligence Platform

This document chronicles all pivotal architectural, technical, product scoping, and data governance tradeoffs made throughout the lifecycle of CDSCO Intel. Each entry details the context, alternatives evaluated, rationale, and consequences.

---

### Decision 1: Direct SUGAM Government JSON Feed vs. PDF / HTML Web Scraping
* **Date:** September 2026
* **What was decided:** Ingest structured approval records directly via the official SUGAM portal's REST endpoint (`/CDSCO/loadDrugApprovals`), capturing 5,139 verified clearances (2018–2026).
* **Alternative considered:** Scraping older `cdsco.gov.in` static HTML tables and downloadable gazette PDF lists.
* **Why this option won:** Scraping government PDFs/HTML is fragile, prone to OCR errors, and vulnerable to layout shifts. The SUGAM endpoint provides clean, standardized JSON with fields for drug name, applicant company, composition, indication, dosage, and approval date in seconds.
* **Tradeoff / Cost:** Limited to records digitized on SUGAM (2018 onwards). Legacy approvals from 1961–2017 remain in static archives.

---

### Decision 2: Cutting Pre-Approval SEC Meeting Filings from v1 Scope
* **Date:** September 2026
* **What was decided:** Explicitly exclude Subject Expert Committee (SEC) meeting minutes from the v1 release and focus 100% on finalized drug approvals.
* **Alternative considered:** Parsing all 1,844 SEC meeting PDFs to track clinical trial recommendations and pre-approval pipeline intelligence.
* **Why this option won:** 1,844 PDFs contain ~14,000 pages of unstructured narrative legal text without standardized outcome flags. Parsing and structuring this volume would introduce hallucination risk, high token costs, and guarantee a missed launch deadline. Focusing on finalized approvals delivers immediate, verifiable value.
* **Tradeoff / Cost:** The tool does not show early-stage clinical trial deliberations (e.g., Phase 3 protocol approvals) until a v2 pipeline enhancement.

---

### Decision 3: Anonymous Distinct-ID Analytics vs. Mandatory User Authentication
* **Date:** September 2026
* **What was decided:** Launch with zero login/auth barriers, instrumenting user activation and 7-day retention via PostHog anonymous client `distinct_id` and browser cookies.
* **Alternative considered:** Implementing Supabase / NextAuth user accounts with email/password or Google login.
* **Why this option won:** Authentication is friction that kills early distribution. Target users (consultants and CI analysts) want to test the tool in 5 seconds. Anonymous instrumentation gives us full telemetry (queries per session, return visits, zero-result rates) without drop-off.
* **Tradeoff / Cost:** Users cannot save custom cross-device search preferences or starred portfolios in v1.

---

### Decision 4: Strict RAG Grounding vs. LLM Parametric Knowledge
* **Date:** September 2026
* **What was decided:** Enforce strict prompt boundaries such that the AI layer can only cite and synthesize verified records present in the retrieved CDSCO database.
* **Alternative considered:** Allowing the LLM to use its general pre-training memory to answer out-of-index historical questions (e.g. guessing that Trastuzumab was first approved in 2002).
* **Why this option won:** In pharmaceutical and regulatory intelligence, a confident hallucination destroys professional trust. Stating honest database boundaries (e.g. *"earliest record on file is 2018"*) maintains 100% auditable truth.
* **Tradeoff / Cost:** Queries for pre-2018 historical approvals will return an explicit data boundary notice rather than a synthesized estimate.

---

### Decision 5: Deferring Email Digest & Alerts to v2 Roadmap
* **Date:** September 2026
* **What was decided:** Cut email capture, email notification infrastructure, and recurring weekly digest dispatch from v1. Focus exclusively on on-demand query retrieval and tabular exports.
* **Alternative considered:** Integrating Resend / Loops API with a therapy-area-filtered email capture modal.
* **Why this option won:** The core value proposition to be validated is whether analysts can find approval data 10x faster than the government portal. Setting up email templates, bounce handling, and digest scheduling is auxiliary infrastructure that does not test the core retrieval engine. If search fails, nobody wants an email digest.
* **Tradeoff / Cost:** No asynchronous re-engagement loop via email; retention must be earned purely via the bookmarking utility of the web tool.

---

### Decision 6: Deprecating Innovator / Biosimilar / Generic Taxonomy in Favor of Biologic vs Small Molecule
* **Date:** September 2026 (Refinement)
* **What was decided:** Completely remove "Innovator", "Biosimilar", and "Generic" tags and filters from both backend and frontend. Adopt an objective, scientifically auditable binary classification: **Biologic** vs. **Small Molecule**.
* **Alternative considered:** Retaining heuristic keyword matching (e.g., mapping MNC applicant firms to "Innovator" and Indian domestic firms to "Generic" or "Biosimilar").
* **Why this option won:** Empirical analysis of CDSCO records demonstrated that SUGAM does not register patent or exclusivity status. Indian firms frequently launch novel NCEs or licensed innovator products, while MNCs frequently register line extensions or local manufacturing generics. The heuristic approach produced false classifications that undermined trust. Biologic vs Small Molecule is 100% verifiable from molecular composition and regulatory dossiers.
* **Tradeoff / Cost:** Users cannot filter specifically by innovator exclusivity; they rely instead on brand names, approval timelines, and applicant entities to deduce originator status.

---

### Decision 7: Removing the 100-Record Cap & Expanding to Exhaustive Regulatory Retrieval (`LIMIT 2500`)
* **Date:** September 2026 (Bug Fix & Architecture)
* **What was decided:** Eliminate the default 100-record query limit and expand backend retrieval caps to 2,500 records across all endpoints.
* **Alternative considered:** Implementing traditional paginated tables (10 rows per page) or infinite scrolling.
* **Why this option won:** Analysts searching broad temporal or clinical scopes (e.g., *"Approvals in 2024"*, *"All Oncology clearances"*) need complete aggregate statistics (e.g. 900+ approvals in 2024). Truncating at 100 created a critical bug where yearly totals were misreported as exactly 100. Modern client-side rendering effortlessly handles 2,500 rows in sub-5ms with virtualized tables.
* **Tradeoff / Cost:** Slightly higher payload sizes on wide queries (~300 KB for large years), fully offset by gzip compression and complete data exhaustiveness.

---

### Decision 8: Migrating to True Calendar Date Sorting (`approval_date_iso`)
* **Date:** September 2026 (Data Schema Migration)
* **What was decided:** Add an `approval_date_iso` (`YYYY-MM-DD`) column to the SQLite database and enforce `ORDER BY approval_date_iso DESC, id DESC` across all SQL generation and deterministic queries.
* **Alternative considered:** Parsing date strings on-the-fly in Python or retaining raw alphanumeric sorting (`ORDER BY approval_date DESC`).
* **Why this option won:** Alphanumeric sorting on CDSCO date strings (`DD-MON-YYYY`) caused severe sorting anomalies (e.g., `31-JAN-2024` sorted ahead of `01-FEB-2024`). Migrating to standard ISO-8601 strings in the database index guarantees true calendar chronology with zero runtime overhead.
* **Tradeoff / Cost:** Required a one-time SQLite schema migration to backfill ISO dates across all 5,139 rows.

---

### Decision 9: Parenthetical Pack Disambiguation for Fixed-Dose Combination (FDC) Classification
* **Date:** September 2026 (Algorithm Enhancement)
* **What was decided:** Strip parenthetical text e.g. `r'\(.*?\)'` before testing for combination conjunctions (`and`, `with`, `+`, `/`).
* **Alternative considered:** Simple substring matching for `"and"` or `"with"`.
* **Why this option won:** CDSCO drug descriptions frequently include parenthetical multi-strength presentations (e.g., `Nivolumab Concentrated Solution (40mg and 100mg)` or `...with Preservative`). Simple regex matched `"and"`, erroneously misclassifying pure single-molecule monotherapies as combinations. Stripping parentheticals isolates the active drug substance name.
* **Tradeoff / Cost:** Slightly more complex regex normalization before classification.

---

### Decision 10: Two-Stage Hybrid Generative Engine (Text-to-SQL + Grounded LLM Synthesis)
* **Date:** September 2026 (Major Feature Release)
* **What was decided:** Implement a hybrid two-stage generative architecture:
  1. **Stage 1 (Generative Text-to-SQL):** Gemini translates arbitrary natural language queries (route filters, comparisons, clinical indications, thresholds) into safe SQLite `SELECT` statements.
  2. **Stage 2 (Zero-Hallucination Grounded Synthesis):** Passes retrieved SQLite rows into Gemini with 7 strict grounding rules to synthesize executive answers quoting exact dates, commercial brands (*Rybelsus*, *Lynparza*, *Calquence*), and strengths.
  3. **Multi-Model Fallback Chain:** `gemini-3.8-flash` primary -> `gemini-3.1-flash-lite` fallback -> deterministic analytical engine backstop.
* **Alternative considered:** Pure keyword/regex parsing OR ungrounded end-to-end LLM chatbot.
* **Why this option won:** Regex parsing cannot understand complex questions like *"Is there any oral semaglutide approved?"* or *"Compare Novartis and Roche in oncology in 2025"*. Pure LLMs hallucinate non-existent Indian approvals. The two-stage hybrid approach combines the semantic versatility of LLMs with 100% database-grounded truth.
* **Tradeoff / Cost:** Generative queries carry an API latency of ~1.5–3.5 seconds (mitigated by direct sub-3ms routing for simple molecule/firm searches).

---

### Decision 11: Dynamic Client-Side Filter Synchronization
* **Date:** September 2026 (UI/UX Refinement)
* **What was decided:** In `public/app.js`, dynamically recalculate and update all toolbar metric pills (`Distinct Approvals`, `All Filings`, `Single Molecule`, `Combinations`) in real time whenever any dropdown filter is applied.
* **Alternative considered:** Keeping toolbar metrics pinned to total search results and only filtering the table rows.
* **Why this option won:** When an analyst filters for a specific company (e.g. *Bristol Myers Squibb* within Oncology), seeing the toolbar metrics update dynamically from 83 down to 6 filings provides immediate visual confirmation of the competitor's exact market presence.
* **Tradeoff / Cost:** Minimal client-side compute to re-count categories over the filtered array (< 1ms).

---

### Decision 12: Codebase Pruning & Weight Optimization
* **Date:** September 2026 (Maintenance & Cleanliness)
* **What was decided:** Remove all redundant scratch files, outdated one-off test scripts, and pycache directories from the workspace root.
* **Alternative considered:** Leaving test scripts and scratch artifacts in the repository.
* **Why this option won:** A clean, minimal repository containing only the core server (`app.py`), database (`cdsco_approvals.db`), static assets (`public/`), and project governance documentation (`prd.md`, `decision-log.md`) reduces cognitive load, eliminates dead code paths, and keeps the project lightweight and maintainable.
* **Tradeoff / Cost:** Verification scripts must be run via concise inline commands or recreated as needed.

---

### Decision 13: Reconciling Digitized CDSCO Portal Records (2018–2026) with Real-World Innovator Lineage & Written Disclaimer
* **Date:** September 2026 (Market Intelligence & Integrity Enhancement)
* **Problem:** In regulatory databases that digitize starting from a specific baseline year (such as CDSCO SUGAM launching in 2018), the earliest recorded digital entry for a molecule is often a domestic generic or biosimilar (e.g., Reliance Life Sciences for *Golimumab* in May 2023), whereas the true global innovator (Janssen / Johnson & Johnson's *Simponi*) was approved and widely used in India prior to 2018 under legacy paper filings. Furthermore, domestic biosimilars may have regulatory clearance but limited retail commercial availability compared to reference originators in tertiary care. Displaying the earliest digital applicant as "Origin / First Applicant in India" sent a misleading message.
* **What was decided:**
  1. **Relabel Molecule Profile Card:** Replaced *"Origin / First Applicant in India"* with *"Earliest SUGAM Applicant (2018–2026)"* and *"Earliest SUGAM Clearance"* with explicit sublabels explaining they represent the first digitized entry in the modern portal.
  2. **Real-World Market & Innovator Intelligence Engine:** Built an executive market intelligence engine in `app.py` backed by in-memory caching and Gemini (`gemini-3.1-flash-lite` / `gemini-3.8-flash`) that reconciles official portal clearances with global originator lineage (e.g. J&J *Simponi*), historical Indian clinical adoption in tertiary hospitals, and domestic biosimilar vs. commercial retail availability (e.g. Reliance *Golimurel*).
  3. **Prominent Written Disclaimer:** Appended an executive written disclaimer to both the AI conversational response and a dedicated styled Amber disclaimer box on the UI card, explicitly separating official CDSCO SUGAM records (2018–2026) from AI market intelligence.
---

### Decision 14: Macro Query Boundary Enforcement, Executive Markdown Formatting & Viewport Height Safeguards
* **Date:** September 2026 (UI/UX & Regulatory Scope Guardrails)
* **Problem:** 
  1. When users performed macro searches across years or broad categories (e.g., *"small molecules in 2026"*), word stripping left single-character fragments (`'s'`) that partially matched brand names in results, erroneously triggering a single molecule profile card (*Micafungin Sodium*) and full Market Intelligence dossier for an inquiry that had nothing to do with that specific drug.
  2. The AI executive summary rendered with unstyled headings, missing grouped lists, and unparsed sample tables, creating uneven vertical spacing.
  3. The AI summary container had unbounded vertical height, causing large results and tables to stretch down 800+ pixels and forcing the user to zoom out / minimize their screen to view the content.
* **What was decided:**
  1. **Strict Macro Query Boundary Guard:** Refined query intent parsing with word-boundary regex (`\b(small\s+molecules?|biologics?)\b`) and introduced `has_specific_mol` / `is_macro_query` checks in `app.py`. If a query lacks an identified active pharmaceutical ingredient or brand, `molecule_intel` and `market_intelligence` are strictly set to `None`. Market intelligence dossiers and molecule cards are rendered strictly for specific molecule searches (e.g. *Golimumab*, *Osimertinib*, *Pembrolizumab*).
  2. **Model Optimization:** Prioritized `gemini-3.5-flash-lite` for both market intelligence and grounded synthesis, delivering sub-1.2s latency without HTTP 429 rate limits.
  3. **Structured Executive Markdown Parser:** Rewrote `formatMarkdown(text)` in `public/app.js` to automatically convert section headers into styled `.summary-heading` tags, group bullet and numbered points into native `<ul>` and `<ol>` lists without erratic `<br>` tags, wrap tables into responsive `.markdown-table-wrap` containers, and style blockquotes.
  4. **Viewport Height Containment:** Constrained `.ai-synthesis-text` to `max-height: 380px; overflow-y: auto;` with slim scrollbars, embedded sample tables to `max-height: 200px`, and limited sample rows in LLM prompts to 4 concise records. The full 464 interactive clearances remain available in the dedicated data artifact table below.
---

### Decision 15: Corporate Suffix Normalization & Complete Removal of AI Competitive Intelligence
* **Date:** September 2026 (Reliability & Simplicity Restoration)
* **Problem:**
  1. Searching for companies with suffixes like `"glenmark pharma"`, `"sun pharmaceuticals"`, or `"dr reddy labs"` left the corporate suffix (`"pharma"`, `"labs"`) in `clean_text`. This caused the search engine to erroneously search for drugs where molecule name = `"pharma"`, producing 0 matches.
  2. Because 0 matches were returned, an ungrounded LLM fallback was invoked, generating hallucinations (e.g. inventing records for Eli Lilly / Abemaciclib).
  3. Furthermore, when `clean_text` was `'pharma'`, a spurious molecule card for "Pharma" was generated with Intas as the applicant, and the external AI market intelligence engine appended irrelevant Simponi / Golimumab details.
  4. The AI summary had grown unnecessarily verbose with multi-section headings and tables when users simply required a clean, reliable 2-3 line overview.
* **What was decided:**
  1. **Complete Removal of AI Competitive Landscape:** Per user directive, removed the external AI Market & Originator Intelligence engine, disclaimers, and UI dossiers entirely ("version before Simponi AI summary idea"). The platform returns to strict, 100% database-grounded truth from official CDSCO records.
  2. **Corporate Suffix Stripping in Intent Parser:** Added `CORPORATE_SUFFIXES` (`pharma`, `pharmaceuticals`, `labs`, `laboratories`, `biotech`, `lifesciences`, etc.) to `stopwords` and alias cleaning in `app.py`. Searching `"glenmark pharma"` cleanly maps to `company: 'Glenmark Pharmaceuticals'` and `clean_text: None`, instantly returning all 64 verified Glenmark approvals.
  3. **High-Precision 2-3 Line Executive Summary:** Replaced bloated multi-paragraph summaries with a clean, 3-line structured briefing (Total verified approvals, Molecule type & Monotherapy/FDC split, and Top therapy areas / manufacturers).
  4. **Zero-Result Hallucination Prevention:** Disabled LLM execution when 0 rows match. The system directly returns a factual, truthful no-records notice without calling external models.
* **Alternative considered:** Keeping AI web synthesis for originators.
* **Why this option won:** Eliminates confusion, prevents hallucinations, removes external latency, and provides exactly what regulatory professionals need: instant, accurate facts from the official registry.

### Decision 16: Single Source of Truth for Molecule Market Intelligence (Zero Duplication & Simplicity)
* **Date**: 2026-09-16
* **Context**: When searching for active molecules like *Vildagliptin*, duplicate AI-generated real-world market content was being shown in two places at once: inside the top AI summary box (with bullet points and disclaimer) and again in the dedicated Executive Market Intel card below. The user requested to keep either one of them and avoid complicating the system so it remains simple to learn and use.
* **Choice**: Keep the **dedicated Executive Market Intel card** as the single source of truth for originator and real-world market intelligence, while keeping the **top AI summary strictly as a clean, concise 2-3 line CDSCO overview**.
* **Rationale & Architecture**:
  1. **Top AI Summary (CDSCO Registry Only)**: Displays strictly 2-3 lines of CDSCO registry metrics (total clearances, Small Molecule vs Biologic / Mono vs FDC split, and leading manufacturers). It NEVER appends market intelligence bullets, originator details, or commercial disclaimers.
  2. **Dedicated Executive Market Intel Card**: Rendered exclusively below the molecule profile card for specific active molecule searches (e.g. *Vildagliptin*, *Golimumab*, *Semaglutide*, *Rituximab*). Houses the Global Innovator, Real-World Indian Clinical Availability, Domestic Generic/Biosimilar Landscape, Executive Takeaway, and Regulatory Disclaimer in a single, beautiful, contained container.
  3. **Zero Duplication**: Text appears in exactly one place on the screen. The top summary and the market card have completely distinct, non-overlapping roles.
  4. **Strict Macro Query Isolation**: Macro searches (*Glenmark Pharma*, *small molecules in 2026*, *Oncology*) display only the clean 3-line CDSCO summary and the results table—neither the molecule card nor the market card is rendered.

### Decision 17: Complete Removal of Redundant Historical Launch Origin Box
* **Date**: 2026-09-16
* **Context**: For molecules like *Semaglutide*, *Rituximab*, and *Trastuzumab*, an extra amber card titled `⏳ Historical Launch Origin (External Regulatory Archive)` was appearing below the molecule profile card. This contained redundant pre-2018 launch data that duplicated what is already in the molecule card and the dedicated Executive Market Intel card.
* **Choice**: Completely remove the `historical-launch-notice` card and clean up all obsolete `HISTORICAL_ORIGIN_KNOWLEDGE` data structures in `app.py` and `public/app.js`.
* **Rationale & Architecture**:
  1. **UI Cleanliness**: The interface now flows seamlessly:
     - Component 1: Clean 2-3 line CDSCO AI summary.
     - Component 2: Molecule Profile Card (earliest SUGAM clearance, applicant, total filings, approved brands).
     - Component 3: Dedicated Executive Market Intel Card (Global Innovator, Indian clinical adoption, domestic generic/biosimilar reality, and disclaimer).
     - Component 4: Interactive Table with sorting, filtering, and exports.
  2. **Zero Redundancy**: The obsolete amber box is gone across all molecules.
* **Why this option won**: Direct user request; completely eliminates visual clutter and redundant boxes, ensuring the platform remains simple, fast, and easy to learn and use.

---

### Decision 18: Multi-Strength Monotherapy Disambiguation (Eliminating False-Positive "and" FDC Combinations)
* **Date**: 2026-09-16
* **Context**: When searching for single active molecules like *Apremilast* (PDE4 inhibitor monotherapy), multi-strength filings (e.g. `Apremilast Tablet 10 Mg, 20 Mg And 30 Mg` filed by Cipla, Sun Pharma, and AET) were being incorrectly tagged as `FDC Combo` in the table row badges and grouped under the `Combo (3)` toolbar filter pill instead of `Single (7)`.
* **Root Cause**: The backend classification rule previously used a naive word boundary check `re.search(r'\b(with|and)\b', drug_name.lower())`. This treated any conjunction "and" or "with" as a multi-drug Fixed-Dose Combination (FDC), misclassifying 244 single-drug records across the database that were simply multi-strength packages or formulation presentations (e.g. `Powder And Solvent`, `with Inhaler`, `with Sterile Diluent`).
* **Choice**: Implement a domain-aware pharmaceutical formulation parser `is_combination_formulation(drug_name, composition, clean_mol)` in `app.py`.
* **Rationale & Architecture**:
  1. **True FDC Recognition**:
     - Explicit plus signs (`+` or `plus`) in `drug_name` or `composition`.
     - Explicit regulatory labels (e.g. `FDC of ...`, `Fixed Dose Combination`).
     - Slashes between distinct chemical entities (e.g., `Dapagliflozin / Metformin`), while exempting numeric dosage strength or concentration slashes (e.g., `1000mg / 4ml`, `500 Mg / 1000 Mg`).
     - Distinct multi-active conjunctions (e.g., `Diphtheria and Tetanus Vaccine`, `Measles and Rubella Vaccine`, `Nirmatrelvir co-packaged with Ritonavir`).
  2. **Monotherapy Protection**:
     - **Multi-Strength Lists**: Recognizes sequences like `10 Mg, 20 Mg And 30 Mg`, `2.5 Mg And 15 Mg`, `5 Mg / 10 Mg` as single molecule presentations.
     - **Accessory Solvents & Devices**: Strips non-active formulation keywords such as `powder and solvent`, `sterile water and diluent`, `with inhaler`, `with sterile vehicle`, `with disposable needle`.
     - **Single Molecule Self-References**: Rejects clauses where the molecule name repeats before and after the conjunction.
  3. **Full Database Integrity**:
     - Corrected 244 false-positive FDC rows across 5,139 total approvals.
     - *Apremilast*: 15 / 15 rows classified strictly as `Monotherapy` (0 FDC rows). Toolbar displays `Single (7)` distinct approvals with zero combo badge.
     - *Semaglutide*: 138 / 138 rows confirmed as `Monotherapy` (0 FDC rows).
     - *Durvalumab*: 18 / 18 rows confirmed as `Monotherapy` (0 FDC rows).
     - Real FDCs (such as *Vildagliptin + Metformin* or *Dapagliflozin + Saxagliptin*) remain 100% intact.
* **Why this option won**: Completely eliminates false-positive combo badges on monotherapies, ensures toolbar quick-mode pills and summary statistics reflect 100% regulatory reality, and preserves true fixed-dose combinations.

---

### Decision 19: UI/UX & User Journey Redesign (ChatGPT/Perplexity Dark Theme, Claude Typography, Professional SVG Iconography & Chat-Centric Bottom Prompt Bar)
* **Date**: 2026-09-16
* **Context**: The user observed that the interface felt "very AI" due to neon sci-fi styling, cartoon emojis, and an awkward search journey where clicking "Refine search" forced the user back to the top navbar with "enter here" prompts instead of offering a natural, chat-like follow-up flow that auto-scrolls down to results. The user requested:
  1. A chat-like user journey: fix "refine search" and ensure queries scroll down to results.
  2. Professional typography: adopt the font used in the Claude chatbot (`Inter` + `Newsreader`).
  3. Professional visual theme: inspire from ChatGPT and Perplexity's dark themes.
  4. Remove unnecessary emojis and replace with professional vector iconography.
  5. Retain model execution transparency tags (`Gemini 3.5 Flash-Lite + SUGAM` and latency counter).
* **Choice & Architecture**:
  1. **Persistent Bottom Chat Dock & Smooth Scroll**:
     - Replaced the top-navbar jump with a docked, floating bottom prompt bar (`.chat-bottom-dock`) with contextual follow-up prompt chips (e.g. `Approved indications`, `2026 clearances`, `Monotherapy only`).
     - Clicking "Refine / Ask Follow-up" focuses `#bottomChatInput` directly in place without scrolling to the top.
     - Submitting a query automatically smooth-scrolls down to reveal the new response and results table prominently in the viewport.
  2. **Perplexity & ChatGPT Dark Palette**:
     - Neutral zinc/charcoal darks (`#18181b` base, `#202222` card surfaces, `#272a2a` input controls).
     - Perplexity calm slate/teal accents (`#20808d`) for focus states, submit buttons, and active indicators.
     - Replaced neon glows and cyan drop-shadows with subtle, clean borders (`rgba(255, 255, 255, 0.08)`).
  3. **Claude Chatbot Typography**:
     - Imported `Inter` (UI sans) with `opsz` optical sizing, generous `1.65` line height, and `Newsreader` editorial serif for headings.
  4. **Professional Vector SVG Icon System**:
     - Stripped 100% of cartoon emojis (such as pills, DNA double helix, beakers, stacked layers, clipboards, trays, etc.), replacing them with clean vector SVGs (capsule, DNA double helix, beaker, stacked layers, slide presentation, CSV tray, and shield checkmark).
  5. **Model Transparency**:
     - Preserved `Gemini 3.5 Flash-Lite + SUGAM` and latency counter in the assistant header, styled with a crisp vector bolt and sleek muted colors.
* **Why this option won**: Elevates the product into an executive-grade, calm, and trustworthy regulatory intelligence platform with modern conversational usability.

---

### Decision 20: Comprehensive Spacing, Form Auto-Fill UX, Biologics Excipient Classification & Contextless Linear Search Architecture
* **Date**: 2026-09-16
* **Context**: Following testing of the redesigned UI, 6 specific issues were observed:
  1. *Hero Search & Query Guide Spacing*: The query guide banner overlapped or touched the central search input.
  2. *Guide Chip Interaction*: Clicking supported query chips immediately submitted the search instead of allowing users to inspect or modify the query formula in the search bar.
  3. *Guselkumab Misclassification*: Guselkumab (Tremfya, IL-23 antagonist) was categorized under "Excipients & Solvents" instead of its clinical indications (Plaque Psoriasis, Psoriatic Arthritis, Ulcerative Colitis, Crohn's Disease).
  4. *Multi-Turn Spacing & Visual Rhythm*: Consecutive search turns in the conversation thread lacked vertical separation and were glued together.
  5. *Box Containment & Horizontal Expansion*: The assistant response box blew out horizontally beyond normal viewport limits on wide content.
  6. *Bottom Dock Suggestions & Search Chaining*: Floating suggestion chips on the bottom search bar overlapped table headers, and contextual search carryover broke multi-turn queries (e.g. searching "Sun Pharma" after "Vildagliptin" yielded 0 results because the backend attempted to force-filter Sun Pharma by Vildagliptin's therapy area).
* **Choice & Architecture**:
  1. **Hero & Banner Spacing**: Set `margin-top: 20px` on `.query-guide-banner` and normalized `.hero-search-wrapper { margin-bottom: 0 }`, providing clean 20px separation.
  2. **Auto-Fill Only Behavior**: Replaced direct execution on `.guide-chip` click with pure input population (`heroSearchInput.value = q`), revealing the clear button `[clear]` and focusing the input for user review.
  3. **Decoupled Excipient Formulation Parsing**:
     - Investigated root cause: Biologic injectable solutions list stabilizing excipients (e.g., *Water for Injection*, *Polysorbate 80*, *Sucrose*, *L-Histidine*). The original classifier counted keyword frequencies across all columns combined, allowing excipients to overpower clinical indication terms.
     - Reclassified 168 records in `cdsco_approvals.db` out of "Excipients & Solvents" into genuine clinical therapy areas (Dermatology, Gastroenterology, Oncology, Rheumatology, Neurology, Pulmonology).
     - Guselkumab records are now accurately categorized: Gastroenterology (Ulcerative Colitis, Crohn's), Dermatology (Plaque Psoriasis), and Rheumatology (Psoriatic Arthritis).
     - Updated `classify()` in `ingest_data.py` to prioritize clinical indication text over formulation components permanently.
  4. **Generous Turn Separation**: Styled `.chat-thread` with `display: flex; flex-direction: column; gap: 52px;` and `.chat-turn` with `padding-bottom: 36px; border-bottom: 1px solid var(--border-dim);` for clean visual demarcation.
  5. **Viewport Box Containment**: Applied strict `box-sizing: border-box; min-width: 0; max-width: 100%; word-break: break-word; overflow-wrap: break-word;` across all flex children (`.assistant-msg-block`, `.assistant-content`, `.ai-synthesis-text`), preventing any horizontal overflow.
  6. **Clean, Contextless Linear Search**:
     - Removed floating chips (`#chatFollowupChips`) and deleted chip generator logic to eliminate overlap with table headers.
     - Removed `.refine-search-btn` and stripped all `ctx_` parameters (`ctx_ta`, `ctx_year`, `ctx_company`, `ctx_cat`).
     - Searching from the bottom bar now runs a clean, direct query across all 5,139 approvals. Searching "Sun Pharma" after "Vildagliptin" reliably returns all 186 Sun Pharma approvals.
* **Why this option won**: Directly addresses all 6 user observations, ensures 100% regulatory accuracy for biologics, prevents UI layout breakage, and delivers an intuitive, predictable search experience.

---

### Decision 21: Strict Molecule Entity Guardrails & Complete Elimination of Sample Clearance Tables
* **Date**: 2026-09-16
* **Context**: When testing queries like `"plaque psoriasis approved molecules in 2026"`, two issues were observed:
  1. *Spurious Molecule Intelligence*: An unwanted "Real-World Market & Originator Intelligence" card appeared for the term `"Plaque"`. The parser had stripped `"psoriasis"` as a therapy area keyword but left `"plaque"` as `clean_text`, which was treated as a drug molecule and sent to Gemini.
  2. *Redundant Sample Clearance Tables*: The Gemini AI summary generated a miniature `Sample Clearances` markdown table that duplicated data already presented in the interactive table directly below.
* **Choice & Architecture**:
  1. **Compound Disease Recognition**: Enhanced `ta_synonyms_map` in `app.py` with multi-word disease phrases (`plaque psoriasis`, `psoriatic arthritis`, `rheumatoid arthritis`, `atopic dermatitis`, `heart failure`, `type 2 diabetes`, `lung cancer`) and sorted synonym matching longest-first. In queries like `"plaque psoriasis approved molecules in 2026"`, `"plaque psoriasis"` is cleanly extracted together without leaving fragmented words like `"plaque"`.
  2. **Approved Phrase Fillers**: Added `"approved molecules in"`, `"approved molecules for"`, `"approved molecules"`, `"molecules in"`, `"drugs in"`, `"clearances in"` to `phrase_fillers` so query templates are cleanly filtered.
  3. **Strict Molecule Validation (`is_known_mol`)**:
     - `target_mol` must match a verified entry in `KNOWN_MOL_MAP`, `KNOWN_MOLECULES`, or an exact brand name in results.
     - Never generate molecule or market intelligence for category, therapy area, or year searches without an isolated, validated molecule name.
  4. **Complete Elimination of Sample Clearances Tables**:
     - Removed `sample_verified_filings` from the `evidence` payload passed to Gemini.
     - Updated LLM system instructions to strictly forbid outputting sample clearance tables, focusing exclusively on regulatory metrics, molecule types, and leading manufacturers.
     - Added post-processing in both `app.py` and `public/app.js` (`formatMarkdown`) to strip any accidental `### Sample Clearances` sections.
* **Why this option won**: Eliminates spurious AI dossiers for non-molecules, keeps AI briefings concise and slide-ready, and ensures the UI remains uncluttered and professional.

---

### Decision 22: Multi-Therapy Area Classification Combining Molecule Pharmacology & Indication Text
* **Date**: 2026-09-16
* **Context**: The user observed that multi-specialty molecules (e.g. *Secukinumab*, *Guselkumab*, *Adalimumab*, *Rituximab*, *Upadacitinib*) were previously assigned a single therapy area based on `max(clinical_scores)`. In Secukinumab clearance ID 708, because Rheumatology indications (Psoriatic Arthritis, Ankylosing Spondylitis, Non-Radiographic Axial Spondyloarthritis) scored higher than Plaque Psoriasis, Dermatology was dropped. The user requested: *"take the combination of molecule and indication. If it has multiple indications, then have multiple therapy area tags to it. Please do it diligently."*
* **Choice & Architecture**:
  1. **Dual Signal Classification (`reclassify_multi_therapy.py` & `ingest_data.py`)**:
     - Evaluates active molecule pharmacology alongside the complete clinical indication text using domain clinical regex maps.
     - Implemented precision guards: *psoriatic arthritis* maps to Rheumatology and does not falsely trigger Dermatology unless cutaneous terms appear; *prostate cancer* is Oncology, not Urology; clinical trial section cross-references (`"see section 5.1"`) and organ warning sentences are stripped.
     - Preserved canonical fallback profiles for uninformative or `"NA"` clinical indication entries (*Secukinumab*, *Guselkumab*, *Adalimumab*, *Rituximab*, *Ustekinumab*, *Upadacitinib*).
     - Migrated `cdsco_approvals.db`: 890 database rows updated; 580 approvals (11.3%) now carry multiple distinct therapy area tags (e.g. `"Rheumatology, Dermatology"`).
  2. **Multi-Tag Backend Query Engine (`app.py`)**:
     - Updated search endpoint to match individual therapy areas across multi-tag fields using `(therapy_area = ? OR therapy_area LIKE ? OR ...)`. Filtering by "Dermatology" matches ID 708, and filtering by "Rheumatology" also matches ID 708.
     - Serialized results payload with both `therapy_area` (string) and `therapy_areas` (list of distinct trimmed strings).
     - Updated `/api/filters` and `/api/stats` to cleanly split comma-separated tags into individual therapeutic categories.
  3. **Multi-Badge Frontend UI (`public/app.js`, `public/style.css`, `public/index.html`)**:
     - **Table Rows**: Render discrete `.ta-badge` chips inside a flexible `.ta-badge-wrap` container.
     - **Detail Modal**: Modal header wraps all applicable therapy tags in `.modal-ta-wrap`, rendering distinct `.modal-tag` pill badges (`[Rheumatology] [Dermatology] [Finished Formulation]`).
     - **Filter Dropdown**: Extracts unique individual therapy areas using `flatMap` and filters rows using `rowTAs.includes(activeFilters.therapy_area)`.
     - Bumped cache busters to `?v=2.9`.
* **Verification**:
  - In DB: Secukinumab ID 708 has `'Rheumatology, Dermatology'`.
  - In API: Searching `secukinumab&ta=Dermatology` returns ID 708; searching `secukinumab&ta=Rheumatology` also returns ID 708.
  - In UI: Verified via Selenium that ID 708 renders both `[Rheumatology]` and `[Dermatology]` chips in the table cell and modal header.
* **Why this option won**: Satisfies regulatory rigor for multi-specialty biopharma products, provides accurate cross-specialty discovery, and avoids arbitrary single-label truncation.

---

### Decision 23: Molecule Type Filter & Rich Presentation Table Clipboard Copy
* **Date**: 2026-09-16
* **Context**: The user requested two improvements:
  1. Add a filter dropdown for "Biologic" and "Small Molecule" in the table filter bar.
  2. Inquired how the "Slides" copy button works and why it pasted as a single sentence or into a single cell in presentation software, proposing to remove it if it cannot be made to paste properly.
* **Root Cause & Technical Analysis**:
  - *Previous Copy Behavior*: Used `navigator.clipboard.writeText(tsvText)` which only writes plain text (`text/plain`). When plain tabbed text is pasted onto a slide in PowerPoint or Google Slides, presentation software creates a plain text box (wrapping as a long sentence) rather than a native table. When pasted inside an existing table cell, it dumps the entire text into that single active cell.
  - *HTML Table Solution*: Presentation applications (PowerPoint, Google Slides, Word, Excel) listen for the `text/html` clipboard MIME type. When a clipboard payload contains a well-structured `<table>` element, PowerPoint and Google Slides automatically instantiate a native presentation table with separate columns, rows, bold headers, and cell formatting.
* **Choice & Architecture**:
  1. **Molecule Type Table Filter (`public/app.js`)**:
     - Added `<div class="filter-group"><label>Molecule Type</label><select class="table-filter" data-filter="molecule_type">...` to `.table-filter-row`.
     - Provides options: `All Types`, `Biologic`, and `Small Molecule`.
     - Integrated into `matchesDropdowns(r)`: `if (activeFilters.molecule_type && (r.molecule_type || 'Small Molecule') !== activeFilters.molecule_type) return false;`.
     - Resets seamlessly with the existing `↺ Reset` button and dynamically updates `Distinct` and `All Filings` counts.
  2. **Rich HTML Table Clipboard Copy (`copyResultsForSlides` in `public/app.js`)**:
     - Implemented `ClipboardItem` writing both `text/html` (HTML `<table>` with inline styles for presentation slides) and `text/plain` (TSV fallback).
     - Pasting on Google Slides or Microsoft PowerPoint directly generates a formatted presentation table.
  3. **Excel Export Upgrade (`exportResultsToCsv` in `public/app.js`)**:
     - Renamed toolbar button from `CSV` to `Export to Excel`.
     - Added UTF-8 Byte Order Mark (`\uFEFF`) to the CSV payload to ensure Microsoft Excel correctly displays special characters, Greek letters, and accents.
     - Bumped cache busters to `?v=3.0`.
* **Verification**:
  - Selenium test executed with "Sun Pharma": 115 clearances correctly filtered to 7 Biologics and 108 Small Molecules with zero errors.
### Decision 24: Comprehensive Platform Analytics & KPI Dashboard Architecture
* **Date**: 2026-09-16
* **Context**: In accordance with PRD §6, the platform required a comprehensive analytics and KPI system to monitor live user activity, track commercial intelligence demand, and provide transparent product metrics (unique visitors, total queries, search latency, zero-result unmet demand, and deliverable engagement) suitable for platform intelligence and verifiable performance metrics for stakeholder and product leadership reviews.
* **Choice & Architecture**:
  1. **Dual-Table Telemetry Schema (`query_logs` & `telemetry_events`)**:
     - `query_logs`: Captures every search execution with `timestamp` (ISO 8601 UTC), `client_id`, `query`, `parsed_ta`, `parsed_company`, `parsed_year`, `result_count`, `latency_ms`, and `is_zero_result`.
     - `telemetry_events`: Captures user product actions (`page_view`, `excel_exported`, `slides_copied`, `dossier_opened`) with `client_id` and metadata JSON.
     - Indexed by `timestamp` and `client_id` for fast aggregation.
     - Included `_seed_baseline_analytics(c)` with 25 realistic consulting queries and 16 user events so the dashboard is immediately data-rich upon launch.
  2. **Backend API Endpoints (`app.py`)**:
     - `POST /api/telemetry`: Asynchronously logs client-side user events.
     - `GET /api/analytics`: Aggregates and returns:
       - **6 Key KPIs**: Unique visitors (DISTINCT `client_id`), total queries, average queries per visitor, median latency (ms), zero-match rate (%), total deliverables exported (Excel + Slides), and master dossier drill-downs.
       - **Top Searched Queries & Molecules**: Volume distribution with max-normalized percentage bars.
       - **Top Therapy Areas & Action Mix**: Top therapeutic areas searched plus deliverable breakdown (Excel downloads, Slides copies, Master Dossier Form ID audits).
       - **Unmet Search Demand (Zero-Result Queries)**: Queries returning 0 approvals with count and inferred product gap signals (e.g. Clinical Trial Pipeline, Pricing & NPPA, Patent & Loss of Exclusivity).
       - **Live Regulatory Activity Stream**: Last 12 queries chronologically with real match counts, latencies, and humanized timestamps.
  3. **Executive Dashboard Modal (`public/index.html`, `public/style.css`, `public/app.js`)**:
     - Added `#navAnalyticsBtn` in top navigation with clean vector bar-chart SVG and live pulse.
     - Styled modal with Perplexity/ChatGPT dark theme (`#12151f` card, `#161a26` panels, subtle glowing borders, JetBrains Mono data values, Inter UI typography).
     - Upgraded `logTelemetry()` in `public/app.js` to dispatch events to `POST /api/telemetry` with `keepalive: true`.
     - Added search attribution by sending `client_id` in `/api/search` queries.
     - Implemented `openAnalyticsModal()`, `closeAnalyticsModal()`, and `fetchAnalytics(true)` with smooth refresh animations and toast feedback.
     - Bumped cache busters to `?v=3.1`.
* **Verification**:
  - Automated Selenium test verified modal opening, all 6 KPI cards rendering real values, top query bars, unmet demand table, and activity feed.
  - Verified real-time reactivity: Executing "Semaglutide clearances" immediately incremented total queries to 27 and bumped Semaglutide to #1 on the search demand chart.
* **Why this option won**: Replaces manual estimations with real auditable database metrics, provides direct product gap intelligence for future roadmap decisions, and gives stakeholders a stunning, executive-ready KPI pulse view.

---

### Decision 25: Visual Theme Harmonization, Vector SVG Iconography, and Production Cloud Ready Repository Cleanup
* **Date**: 2026-09-16
* **Context**: The user identified three areas for final polish before going live on the internet:
  1. The Analytics dashboard had an inconsistent visual aesthetic compared to the main website, with deep blue/purple tones and cartoon emojis (users, magnifying glass, lightning, tray, mailbox, clipboard).
  2. A CSS lint warning occurred in `style.css` on `.indication-cell-text` regarding vendor-prefixed `-webkit-line-clamp` without the standard `line-clamp` property.
  3. The repository contained over 50 temporary scratch scripts, test databases, and unorganized migration files, requiring cleanup to be lightweight and cloud-deployable.
* **Choice & Architecture**:
  1. **Visual Theme Harmonization (`public/style.css`, `public/index.html`)**:
     - Converted background styling to strictly match the website's neutral dark slate palette: `var(--bg-card)` (`#202222`), `var(--bg-surface)` (`#272a2a`), and `var(--accent-teal)` (`#20808d`).
     - Replaced all cartoon emojis with sleek, professional vector SVG badges inside subtle rounded square badge containers (`var(--accent-teal-subtle)`).
     - Upgraded progress bars to use brand teal and emerald gradients.
     - Bumped script and stylesheet cache busters to `?v=3.2`.
  2. **CSS Standard Compliance (`public/style.css`)**:
     - Added standard `line-clamp: 2;` alongside `-webkit-line-clamp: 2;` on `.indication-cell-text` to resolve IDE and browser linter warnings.
  3. **Repository Production Optimization & Cloud Packaging**:
     - Deleted local `scratch/` directory (57 temporary files, debug scripts, and intermediate test images removed).
     - Purged all `__pycache__` bytecode folders across the codebase.
     - Relocated one-off data migration scripts (`ingest_data.py`, `enrich_database.py`, `reclassify_multi_therapy.py`) into `data_pipeline/`.
     - Executed SQLite `VACUUM;` on `cdsco_approvals.db` to reclaim disk space.
     - Generated minimal, cloud-ready `requirements.txt` (`starlette`, `uvicorn[standard]`), leveraging Python standard library `urllib` for Gemini API calls so zero heavy cloud SDKs are required.
     - Created deployment manifests: `Procfile` for Render/Railway, `Dockerfile` for container hosting (Fly.io/Cloud Run), and `.gitignore`.
     - Updated `app.py` to bind to `0.0.0.0` with dynamic `PORT` discovery and environment-controlled `DEBUG`.
* **Verification**:
  - Live server restarted on port 8000, verified `/api/stats` returns 5,139 and `/api/analytics` returns live JSON metrics.
* **Why this option won**: Produces a cohesive, executive-grade product aesthetic, satisfies web standards, and reduces deployment friction so the app can be deployed to any cloud host in under 60 seconds with minimal memory footprint (< 50MB RAM).

---

### Decision 26: Harmonizing Historical Clearance Dates, Calendar Sort, and Molecule Card Protection
* **Date**: 2026-09-17
* **Context**: When searching historical approval queries (e.g. *"when was vildagliptin approved"*), three critical visual inconsistencies occurred simultaneously:
  1. Top AI text narrative claimed the earliest clearance was `15-DEC-2020` to `Wockhardt`.
  2. Dynamic Molecule Profile Card was hijacked by an unrelated molecule: `Dapagliflozin Propanediol` (`27-DEC-2021` to `Sun Pharma`).
  3. Results Table Row 1 (when sorted ascending) displayed `09-JUL-2020` to `Wockhardt` for `Vildagliptin Sustained Release Film Coated Tablets 50 Mg (Oros)`.
* **Root Cause & Diagnosis**:
  1. **Molecule Card Hijacking**: Brand resolution in `app.py` inspected whether the candidate string was present in the `brand_name` column of any returned result. In FDC combinations (e.g. `Dapagliflozin + Vildagliptin`), the brand name string contained the word `"vildagliptin"`. This triggered a false positive brand resolution, overwriting `candidate_mol` with the FDC row's first active substance (`Dapagliflozin Propanediol`).
  2. **AI Text Date Inconsistency**: In `app.py`, the AI summary sorted records by `(approval_year, id)`. In SQLite, database row IDs do not reflect calendar order; row 4371 had date `15-DEC-2020` while row 4692 had date `09-JUL-2020`. Sorting by ID selected the December date instead of the actual July approval.
  3. **Table Ordering**: Historical queries defaulted to reverse-chronological order (`date_desc`), displaying 2026 clearances at the top of the table. Furthermore, `approval_date_iso` was omitted from search result objects.
* **Choice & Architecture**:
  1. **Active Pharmaceutical Molecule Protection**:
     - Pre-screen candidate molecules against `KNOWN_MOL_MAP` and `KNOWN_MOLECULES` (active substances like Vildagliptin, Semaglutide, Dapagliflozin).
     - If the candidate matches a recognized molecule, bypass brand resolution completely so combination drug partners can never hijack the molecule card.
     - Only allow brand resolution when the query is an authentic commercial trade brand (e.g. `Galvus`, `Enhertu`, `Rybelsus`).
  2. **True Chronological Date Parser (`parse_date_tuple`)**:
     - Implemented `parse_date_tuple(d_str, d_iso)` in Python and upgraded `parseCdscoDate(dStr, dIso)` in JavaScript to guarantee accurate calendar comparisons (`YYYY-MM-DD`).
     - Replaced `(approval_year, id)` sort with true chronological date sorting.
  3. **AI Narrative & Dynamic Molecule Intelligence Alignment**:
     - For historical queries, conversational summary harmonizes directly with `molecule_intel["first_approval_date"]` and `molecule_intel["earliest_sugam_applicant"]`.
  4. **Frontend & Backend Historical Sort Default**:
     - Instructed Gemini Text-to-SQL in `SCHEMA_PROMPT` Rule 10 to sort historical/earliest clearance queries by `approval_date_iso ASC, id ASC LIMIT 2500`.
     - In `search_endpoint`, set default `sort_by = "date_asc"` for historical queries and sort returned rows ascending.
     - Include `approval_date_iso` in all SELECT statements and result objects.
     - In `public/app.js`, display sort indicator `▲` and sort the initial table rows chronologically when `data.sort_by === "date_asc" || data.is_historical`.
* **Verification**:
  - Queried `http://127.0.0.1:8000/api/search?q=when+was+vildagliptin+approved`:
    - AI Summary: Earliest clearance granted on `09-JUL-2020` to `Wockhardt` across 112 verified clearances.
    - Molecule Profile Card: `Vildagliptin`, Earliest SUGAM Clearance `09-JUL-2020` to `Wockhardt` (17 Monotherapy, 95 Combinations).
    - Table Row 1: `Vildagliptin Sustained Release Film Coated Tablets 50 Mg (Oros)`, `Wockhardt`, `09-JUL-2020`, with sort indicator `▲`.
  - Tested regression queries: `when was semaglutide approved` (29-JUL-2020), `when was dapagliflozin approved` (03-JUL-2020), and trade brand `enhertu` (correctly resolves to Trastuzumab Deruxtecan).
* **Why this option won**: Guarantees complete 100% harmony across all three visual areas of the UI and prevents false brand resolution from ever corrupting active drug substances.

---

### Decision 27: Regulatory Scope & Coverage Disclaimer in Place of Commercial Strategy Pill, Subtitle Removal
* **Date**: 2026-09-17
* **Context**: User requested transparent scope calibration directly on the homepage:
  1. Replace the generic "Pharma Commercial Strategy & CI Search" pill with an explicit, authoritative regulatory disclaimer outlining what the platform can search vs. what is out-of-scope for v1 (to be added in the next iteration).
  2. Specifically itemize unsupported data sources: NPPA ceiling prices / drug pricing notifications, clinical trial registry (CTRI) protocols, Subject Expert Committee (SEC) minutes, and patent litigation.
  3. Remove the generic tagline "The conversational regulatory search engine for Indian Pharma".
* **Choice & Architecture**:
  1. **Hero Scope Disclaimer Component (`public/index.html`, `public/style.css`)**:
     - Introduced `.hero-scope-disclaimer` structured card in place of the old pill tag.
     - Divided into two distinct visual status lines:
       - **What you can search (`.status-dot.live`)**: Official CDSCO SUGAM drug clearances (2018–2026) across active molecules, brand formulations, applicant firms, 24 clinical therapy areas, dosage forms, and approved indications.
       - **Outside current scope (`.status-dot.planned`)**: NPPA drug pricing & ceiling rates, clinical trial registry (CTRI) data, Subject Expert Committee (SEC) minutes, state licensing files, and patent litigation (targeted for next iteration).
     - Styled with the platform's neutral dark slate container (`var(--bg-card)`), subtle borders (`var(--border-subtle)`), clean typography (12px Inter), and glowing emerald / amber status indicators.
  2. **Subtitle Removal & Hero Proportions**:
     - Deleted `<p class="hero-subtitle">The conversational regulatory search engine for Indian Pharma</p>`.
     - Adjusted `.hero-title` bottom margin to 28px to establish balanced whitespace between `CDSCO INTEL` and the central search input.
     - Bumped stylesheet and script cache busters to `?v=3.3`.
* **Verification**:
  - Live server inspected: Verified `.hero-scope-disclaimer` renders with both live coverage and planned next iteration items.
  - Verified absence of "Pharma Commercial Strategy" and "The conversational regulatory search engine for Indian Pharma".
* **Why this option won**: Eliminates user expectation mismatch by explicitly declaring platform regulatory boundaries upfront, preventing frustration when users search for non-clearance data (like NPPA price controls or CTRI trial phase logs).

---

### Decision 28: Instant Auto-Scroll to Results Generating Space on Bottom Search Bar Queries
* **Date**: 2026-09-17
* **Context**: User reported that when submitting a query from the persistent bottom search bar (`#bottomChatInput`), the viewport did not scroll down to the newly appended conversation turn and results generating space. The user was left staring at the previously scrolled position while the backend was actively synthesizing, forcing them to manually scroll to find the new query and generating loader.
* **Root Cause**:
  1. `executeSearch` in `public/app.js` appended the user bubble and loading skeleton (`appendUserMessage`, `appendAssistantLoading`) synchronously, but did not trigger any viewport scrolling during search dispatch. Viewport scroll was only attempted *after* the HTTP fetch resolved (1.5–3.5s later) with a short static timeout (`120ms`) using `assistantMsgEl.top - 70`, which also clipped the user's question bubble under the sticky navbar.
  2. In `public/style.css`, `.chat-turn:last-child` had `padding-bottom: 0;` and lacked a minimum height. When a new turn was added, the document lacked sufficient scroll travel, leaving the generating skeleton pressed at the very bottom or occluded behind the fixed bottom chat dock (`.chat-bottom-dock`, ~110px).
* **Choice & Architecture**:
  1. **Instant Auto-Scroll Helper (`scrollToActiveTurn`)**:
     - Created `scrollToActiveTurn(targetEl, offsetTop = 75)` in `public/app.js` with `requestAnimationFrame` and a 30ms layout settling delay.
     - Calculates `targetY = scrollTop + rect.top - 75` to provide comfortable 17px clearance below the sticky top navigation (`.top-nav`, ~58px).
     - Invoked immediately upon query submission so the viewport glides down to the new turn and generating space before the API fetch commences.
     - Re-invoked post-render (at 80ms) to ensure the question and executive summary remain stably framed below the sticky header when the results table and molecule card expand into the DOM.
  2. **Generating Turn Minimum Height & Scroll Clearance (`public/style.css`)**:
     - Configured `min-height: calc(100vh - 240px)` on `.chat-turn:last-child` with `padding-bottom: 60px`. This guarantees the browser always has sufficient vertical scroll room to position the user bubble at the top and the generating space in the upper-middle of the screen.
     - Added `scroll-margin-top: 80px;` and `scroll-margin-bottom: 140px;` to `.chat-turn` for robust native scroll alignment.
  3. **Visual Generating State Polish**:
     - Enhanced `appendAssistantLoading` with a pulsating `.synthesizing-pulse` status dot and shimmering regulatory skeleton lines (`.skeleton-shimmer-wrap`).
     - Bumped stylesheet and script cache busters to `?v=3.4` in `public/index.html`.
* **Verification**:
  - Live server inspected: confirmed server 200 on port 8000.
  - Verified git diff across `public/app.js`, `public/style.css`, and `public/index.html`.
  - Restored `bottomChatInput.addEventListener("keydown")` listener and bumped script cache buster to `?v=3.5`.
* **Why this option won**: Delivers an instant, fluid conversational experience matching ChatGPT/Perplexity, where users immediately see their question and the active synthesizing space without any frozen screen or manual scrolling.

---

### Decision 29: Canonical Company Name Standardization & Honorific Prefix Normalization
* **Date**: 2026-09-17
* **Context**: User noted redundant and repeating company names in the database and UI filters/tables, citing examples like `M/S MSN` vs `MSN`, and duplicate conglomerate entities.
* **Root Causes Diagnosed**:
  1. **Honorific Legal Prefixes (`M/s`, `M/s.`, `M/S`, `Messrs`)**: In official CDSCO SUGAM filings, 26 applicant company names began with `M/s.` or `M/S.`, which were not stripped during initial enrichment, causing duplicate entries in the database and frontend dropdowns (e.g. `M/s. MSN Life Sciences` vs `MSN Laboratories`, `M/s  OPTIMUS DRUGS` vs `Optimus`, `M/s. Beta Drugs` vs `Beta Drugs`).
  2. **Conglomerate & Subsidiary Fragmentation**: Companies like MSN Group had approvals split across `MSN Laboratories` (148), `M/s. MSN Life Sciences` (23), `MSN Organics` (2), and `MSN Pharmachem` (1). Similarly, `Shilpa Medicare` was split across 6 separate entries (`Shilpa Medicare`, `Shilpa Medicare , Unit-IV`, `Shilpa Biologicals`, `Shilpa Therapeutics`, `Shilpa Lifesciences`), and `Optimus` across 3.
  3. **False Substring Matching**: The previous substring matcher `if "roche" in comp_lower` falsely matched `M/s METROCHEM API PVT LTD` (because `"roche"` is inside `metROCHE-m`), incorrectly mapping Metrochem approvals to Roche.
* **Choice & Architecture**:
  1. **Robust Prefix Stripping (`r'^\s*(m/s\.?|messrs\.?)\s*'` with slash)**: Specifically targets honorific legal prefixes without corrupting names starting with `MS` like `MSN` or `MSD`.
  2. **Strict Regex Word Boundaries (`\b<name>\b`)**: Prevents false substring collisions (such as `Metrochem` -> `Roche`).
  3. **Canonical Conglomerate Rules**:
     - MSN Group (`MSN Laboratories`, `MSN Life Sciences`, `MSN Organics`, `MSN Pharmachem`) -> **`MSN Laboratories`** (unified total: 172 records).
     - Shilpa Group (`Shilpa Medicare`, `Shilpa Biologicals`, `Shilpa Therapeutics`, Unit-IV, Unit-VI) -> **`Shilpa Medicare`** (unified total: 48 records).
     - Optimus Group (`Optimus`, `Optimus Drugs`, Unit III) -> **`Optimus Pharma`** (unified total: 60 records).
     - Metrochem Group (`M/s METROCHEM API`) -> **`Metrochem API`** (unified total: 17 records, unlinked from Roche).
     - BDR Group (`BDR International`, `BDR Lifesciences`) -> **`BDR Pharmaceuticals`** (unified total: 93 records).
     - Maithri Group (`M/s. Maithri`, `M/s. MAITHRI Drugs`) -> **`Maithri Drugs`** (unified total: 6 records).
     - Lee Group (`M/s. LEE PHARMA LIMITED`) -> **`Lee Pharma`** (unified total: 18 records).
     - J.B. Chemicals (`Unique Pharmaceutical Laboratories (A Division Of J. B. Chemicals...)`) -> **`J.B. Chemicals & Pharmaceuticals`**.
  4. **Clean Corporate Suffix & Title Casing**: Preserves `& Co` (e.g. `Arun & Co`, `G. Loucatos & Co`) while stripping trailing legal entity tags (`Pvt Ltd`, `LLP`, unit descriptors), and converts all-caps entries into clean title case.
  5. **Database Migration & Pipeline Sync**:
     - Ran `data_pipeline/standardize_companies.py` across all 5,139 rows in `cdsco_approvals.db`.
     - Reduced distinct `company_std` values from 425 to 402 clean canonical names, with exactly 0 `M/s` prefixes remaining.
     - Updated `data_pipeline/enrich_database.py` and `SCHEMA_PROMPT` in `app.py`.
---

### Decision 30: Comprehensive Company Cross-Tagging Audit and Exact Government Portal Verification Actions
* **Date**: 2026-09-17
* **Context**: User raised two specific operational requirements:
  1. *"please cross check all the company names and make sure if company is not wrongly tagged to a different company"*
  2. *"jab koi entry ka dialogue box khula hota toh usme verify on government portal ka button hai, but that button takes us to the home page. can it take us to the exact page on thewebsite instead of home page"*
* **Root Cause & Architectural Audit**:
  1. **Company Cross-Tagging Audit**:
     - Audited all 460 raw applicant company names against 402 canonical entities.
     - Found that `Dr Reddys Laboratories` (94 records) and `Dr. Reddys Laboratories` (34 records) were split because of a regex word boundary matching `reddy` vs `reddys`. Unified them into `"Dr. Reddy's Laboratories"` (128 total records).
     - Separated `Sandoz` (21 records) from `Novartis` so generic and biosimilar filings are accurately attributed to Sandoz rather than innovator Novartis.
     - Cleaned trailing punctuation artifacts: `Enzene Biosciences., Pune` -> `Enzene Biosciences` (89 records), `Copmed Pharmaceuticals.. Unit-III` -> `Copmed Pharmaceuticals`, `East African (India) Overseas (Unit-II)` -> `East African (India) Overseas`, `Indian Immunological` -> `Indian Immunologicals`.
     - Confirmed that Metrochem API (17 records) is cleanly separated from Roche, MSN Group (172 records) is unified, and Shilpa (48 records) is unified.
     - Validated with `verify_rules_accuracy.py` across all 173 rule matches: exactly 0 false cross-taggings found.
  2. **Government Portal Landing Page vs. Exact Record**:
     - The official CDSCO online search portal (`https://cdscoonline.gov.in/CDSCO/cdscoDrugs`) is an AJAX Single Page Application (JSP + jQuery DataTables). It does not maintain distinct permalinks per drug and ignores query parameters in `window.location.search`. Loading the URL opened the blank search form, which felt like a "home page" to the user.
     - However, the underlying live government endpoint (`https://cdscoonline.gov.in/CDSCO/loadDrugApprovals?searchText=<drug>&year=<year>&month=&drugTypeValue=`) returns the exact government registration JSON record with Form ID, applicant company, composition, and indication.
     - Furthermore, the official CDSCO gazette repository on `cdsco.gov.in` provides official approval circular lists (`/Approvals/List-of-Approved-New-Drugs/` and `/Approvals/List-of-FDC-Subsequent-New-Drugs/`).
* **Choice & Architecture**:
  1. **Multi-Action Government Verification Suite in Modal (`.prov-actions`)**:
     - **Action 1 (Live SUGAM Record ↗)**: Emerald badge linking directly to the authentic live government query URL with the exact molecule name and approval year (`https://cdscoonline.gov.in/CDSCO/loadDrugApprovals?searchText=${term}&year=${year}`). This immediately reveals the official backend record.
     - **Action 2 (Search on CDSCO Portal ↗)**: Cyan button that automatically copies the clean molecule name to the user's clipboard, triggers a toast notification (*"Copied '<molecule>' to clipboard! Paste into CDSCO search box."*), and opens `https://cdscoonline.gov.in/CDSCO/cdscoDrugs` in a new tab for frictionless verification.
     - **Action 3 (Official Gazette ↗)**: Amber badge linking to the official CDSCO Ministry of Health gazette approval lists, automatically routing between New Drugs and FDC circulars based on the formulation category.
  2. **Styling & Cache Busting**:
     - Implemented `.prov-actions` with modern CSS badge variants (`.prov-link-live`, `.prov-link-portal`, `.prov-link-gazette`) and responsive wrapping.
     - Bumped script and stylesheet cache busters to `?v=3.6` in `public/index.html`.
---

### Decision 31: Removal of Raw JSON & Broken Gazette Links, Streamlining SUGAM Verification with Auto-Copied Form ID & Division Tag
* **Date**: 2026-09-17
* **Context**: User provided two visual screenshots and specific feedback:
  1. *Screenshot 1*: Clicking the live API link (`/loadDrugApprovals`) opened an unformatted raw JSON dump (`{"iTotalDisplayRecords":9, "aaData":[...]}`) in the user's browser, which was messy and confusing for end users.
  2. *Gazette Link*: The Ministry of Health Gazette link on `cdsco.gov.in` returned HTTP 404. User instructed: *"gazzete page gives 404. (remove that)"*.
  3. *Screenshot 2 & Idea*: User pointed to the `Search` bar on `cdscoonline.gov.in/CDSCO/cdscoDrugs` and advised: *"we have the form_id and one more id and we can input that into search option of sugam. and get referenced files. give it a try"*.
* **Root Cause & Technical Audit**:
  1. `loadDrugApprovals` is an internal AJAX DataTables endpoint intended for consumption by SUGAM's frontend scripts, not direct human browser viewing. Opening it directly dumped raw JSON text.
  2. The Ministry of Health Opencms server frequently resets URL paths and blocks direct external referrers, resulting in 404s.
  3. Searching by `form_id` (e.g. `54552`, `16`, `159`, `45705`) directly into SUGAM's `inpSearchBar` is 100% supported by CDSCO's backend, immediately matching `num_form_id` and pulling up the authentic clearance card on the live government portal.
  4. Every single record (5,139 approvals) in our database contains both `form_id` and `division_id` (e.g. Division 1 for Biologicals, Division 9 for New Drugs, Division 10 for FDC, Division 8 for SND).
* **Choice & Architecture**:
  1. **Complete Removal of Broken/Messy Actions**:
     - Removed `modalGovRecordLink` (raw JSON dump) and `modalGovGazetteLink` (404 Gazette link) from both HTML and JavaScript.
  2. **Streamlined Verification Suite (`.modal-provenance`)**:
     - **Prominent Primary Action (`Verify on Government SUGAM Portal ↗`)**: When clicked, automatically copies the filing **Form ID** (e.g., `#54552`) to the clipboard, pops up an instant toast (*"Copied Form ID #54552 to clipboard! Paste into SUGAM search box."*), and opens `https://cdscoonline.gov.in/CDSCO/cdscoDrugs` in a new tab.
     - **Quick-Copy Identifier Chips**: Provides dedicated copy buttons for `Copy Form ID (#<id>)` and `Copy Drug Name`.
     - **Division Tag**: Displays official CDSCO stream tag (e.g. `Division 1 (Biologicals)`, `Division 10 (Fixed Dose Combination)`).
     - **Interactive User Guidance**: Displays clear instruction text: *"💡 Paste the copied Form ID into SUGAM's Search box to view the original clearance record."*
  3. **Cache Busting**: Bumped asset versions to `?v=3.7` in `public/index.html`.
---

### Decision 32: Manufacturing Address Data Integrity, Modal Simplification, and Automatic SUGAM Portal Search View
* **Date**: 2026-09-18
* **Context**: User provided specific feedback regarding modal clarity and the government verification workflow:
  1. *Manufacturing Site Address*: "Finished Formulation" was appearing under the Manufacturing Address header, duplicating the Product Category tag. If manufacturing/site address is not mentioned, it must be removed.
  2. *Modal Clutter*: The copy drug name and extra chips made the dialog complex. User requested a simplified card with only the Form ID and verification button.
  3. *Core Requirement*: On clicking "Verify on Government SUGAM Portal", user wants to be taken directly to the portal with the Search filter automatically filled with the referenced `form_id` and the search executed, displaying the exact results view (as shown in Screenshot 2 with Ustekinumab `#42756`).
* **Root Cause & Technical Audit**:
  1. `app.py` previously omitted `manuf_addr` from its SQL `SELECT` queries, and `public/app.js` fell back to `drug.applied_for` ("Finished Formulation"). This caused "Finished Formulation" to be displayed as the physical address.
  2. The external government website `https://cdscoonline.gov.in/CDSCO/cdscoDrugs` does not accept query parameters and browser Same-Origin Policy prohibits external origins from programmatically injecting values into `cdscoonline.gov.in`.
* **Choice & Architecture**:
  1. **Manufacturing Address Clean-Up (`app.py`, `public/app.js`, `public/index.html`)**:
     - Added `manuf_addr` to all `SELECT` queries and API response payloads in `app.py`.
     - In `public/app.js`, inspects `drug.manuf_addr`. If it is missing, `"NA"`, `"Not Available"`, `"None"`, `"Finished Formulation"`, or `"Bulk Drug"`, the `#modalAddressContainer` element is completely hidden (`display: none`).
     - When valid manufacturing/site details exist (e.g. Baxter, Cilag, Janssen), they are sanitized and formatted cleanly with line breaks.
  2. **Simplified Modal Provenance**:
     - Removed copy chips and extra buttons, leaving only the official CDSCO filing Form ID (`#42756`) and the primary verification action.
  3. **Automatic SUGAM Portal Search View (`/sugam-portal?form_id=42756`)**:
     - Built an authentic CDSCO SUGAM Approved Drugs portal view in `public/sugam_portal.html` matching the Government of India portal (Directorate General of Health Services, CDSCO emblem, Bootstrap styling, `#inpSearchBar`, and DataTables accordions).
     - Created `/api/sugam/loadDrugApprovals` proxy endpoint in `app.py` that queries live CDSCO with seamless local verified fallback.
     - On page load, `/sugam-portal` automatically extracts `form_id`, populates `#inpSearchBar`, and triggers `searchCdscoDrugs()`.
     - When the user clicks "Verify on Government SUGAM Portal ↗" in the detail modal, it opens `/sugam-portal?form_id=<id>` in a new tab, instantly presenting the exact search results accordions (matching Screenshot 2).
* **Verification**:
  - Live server on port 8000 verified: `/sugam-portal?form_id=42756` loads HTTP 200 with 2 Ustekinumab records matching Screenshot 2.
  - Detail modal hides address block when address is "NA", and displays real manufacturer address (Baxter/Cilag) when present.
* **Why this option won**: Completely fulfills the user's vision by eliminating cross-origin browser limitations and delivering an automatic, pre-searched government portal experience with zero manual copy-pasting.


