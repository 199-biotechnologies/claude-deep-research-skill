---
name: deep-research
description: Conduct enterprise-grade research with multi-source synthesis, citation tracking, and verification. Use when user needs comprehensive analysis requiring 10+ sources, verified claims, or comparison of approaches. Triggers include "deep research", "comprehensive analysis", "research report", "compare X vs Y", or "analyze trends". Do NOT use for simple lookups, debugging, or questions answerable with 1-2 searches.
---

# Deep Research

<!-- STATIC CONTEXT BLOCK START - Optimized for prompt caching -->
<!-- All static instructions, methodology, and templates below this line -->
<!-- Dynamic content (user queries, results) added after this block -->

## Core System Instructions

**Purpose:** Deliver citation-backed, verified research reports through 8-phase pipeline (Scope → Plan → Retrieve → Triangulate → Synthesize → Critique → Refine → Package) with source credibility scoring and progressive context management.

**Context Strategy:** This skill uses 2025 context engineering best practices:
- Static instructions cached (this section)
- Progressive disclosure (load references only when needed)
- Avoid "loss in the middle" (critical info at start/end, not buried)
- Explicit section markers for context navigation

---

## Decision Tree (Execute First)

```
Request Analysis
├─ Simple lookup? → STOP: Use WebSearch, not this skill
├─ Debugging? → STOP: Use standard tools, not this skill
└─ Complex analysis needed? → CONTINUE

Mode Selection
├─ Initial exploration? → quick (3 phases, 2-5 min)
├─ Standard research? → standard (6 phases, 5-10 min) [DEFAULT]
├─ Critical decision? → deep (8 phases, 10-20 min)
└─ Comprehensive review? → ultradeep (8+ phases, 20-45 min)

Execution Loop (per phase)
├─ Load phase instructions from [methodology](./reference/methodology.md#phase-N)
├─ Execute phase tasks
├─ Spawn parallel agents if applicable
└─ Update progress

Validation Gate
├─ Run `python scripts/validate_report.py --report [path]`
├─ Pass? → Deliver
└─ Fail? → Fix (max 2 attempts) → Still fails? → Escalate
```

---

## Workflow (Clarify → Plan → Act → Verify → Report)

**AUTONOMY PRINCIPLE:** This skill operates independently. Infer assumptions from query context. Only stop for critical errors or incomprehensible queries.

### 1. Clarify (Rarely Needed - Prefer Autonomy)

**DEFAULT: Proceed autonomously. Derive assumptions from query signals.**

**ONLY ask if CRITICALLY ambiguous:**
- Query is incomprehensible (e.g., "research the thing")
- Contradictory requirements (e.g., "quick 50-source ultradeep analysis")

**When in doubt: PROCEED with standard mode. User will redirect if incorrect.**

**Default assumptions:**
- Technical query → Assume technical audience
- Comparison query → Assume balanced perspective needed
- Trend query → Assume recent 1-2 years unless specified
- Standard mode is default for most queries

---

### 2. Plan

**Mode selection criteria:**
- **Quick** (2-5 min): Exploration, broad overview, time-sensitive
- **Standard** (5-10 min): Most use cases, balanced depth/speed [DEFAULT]
- **Deep** (10-20 min): Important decisions, need thorough verification
- **UltraDeep** (20-45 min): Critical analysis, maximum rigor

**Announce plan and execute:**
- Briefly state: selected mode, estimated time, number of sources
- Example: "Starting standard mode research (5-10 min, 15-30 sources)"
- Proceed without waiting for approval

---

### 3. Act (Phase Execution)

**All modes execute:**
- Phase 1: SCOPE - Define boundaries ([method](./reference/methodology.md#phase-1-scope))
- Phase 3: RETRIEVE - Gather 15-30 sources, spawn parallel agents
- Phase 8: PACKAGE - Generate report using [template](./templates/report_template.md)

**Standard/Deep/UltraDeep execute:**
- Phase 2: PLAN - Strategy formulation
- Phase 4: TRIANGULATE - Verify 3+ sources per claim
- Phase 5: SYNTHESIZE - Generate novel insights

**Deep/UltraDeep execute:**
- Phase 6: CRITIQUE - Red-team analysis
- Phase 7: REFINE - Address gaps

**Critical: Avoid "Loss in the Middle"**
- Place key findings at START and END of sections, not buried
- Use explicit headers and markers
- Structure: Summary → Details → Conclusion (not Details sandwiched)

**Progressive Context Loading:**
- Load [methodology](./reference/methodology.md) sections on-demand
- Load [template](./templates/report_template.md) only for Phase 8
- Do not inline everything - reference external files

**Anti-Hallucination Protocol (CRITICAL):**
- **Source grounding**: Every factual claim MUST cite a specific source immediately [N]
- **Clear boundaries**: Distinguish between FACTS (from sources) and SYNTHESIS (your analysis)
- **Explicit markers**: Use "According to [1]..." or "[1] reports..." for source-grounded statements
- **No speculation without labeling**: Mark inferences as "This suggests..." not "Research shows..."
- **Verify before citing**: If unsure whether source actually says X, do NOT fabricate citation
- **When uncertain**: Say "No sources found for X" rather than inventing references

---

### 4. Verify (Always Execute)

**Step 1: Citation Verification (Catches Fabricated Sources)**

```bash
python scripts/verify_citations.py --report [path]
```

**Checks:**
- DOI resolution (verifies citation actually exists)
- Title/year matching (detects mismatched metadata)
- Flags suspicious entries (2024+ without DOI, no URL, failed verification)

**If suspicious citations found:**
- Review flagged entries manually
- Remove or replace fabricated sources
- Re-run until clean

**Step 2: Structure & Quality Validation**

```bash
python scripts/validate_report.py --report [path]
```

**8 automated checks:**
1. Executive summary length (50-250 words)
2. Required sections present (+ recommended: Claims table, Counterevidence)
3. Citations formatted [1], [2], [3]
4. Bibliography matches citations
5. No placeholder text (TBD, TODO)
6. Word count reasonable (500-10000)
7. Minimum 10 sources
8. No broken internal links

**If fails:**
- Attempt 1: Auto-fix formatting/links
- Attempt 2: Manual review + correction
- After 2 failures: **STOP** → Report issues → Ask user

---

### 5. Report

**CRITICAL: Generate COMPREHENSIVE, DETAILED markdown reports**

**File Organization (CRITICAL - Clean Accessibility):**

**1. Create Organized Folder in Documents:**
- ALWAYS create dedicated folder: `~/Documents/[TopicName]_Research_[YYYYMMDD]/`
- Extract clean topic name from research question (remove special chars, use underscores/CamelCase)
- Examples:
  - "psilocybin research 2025" → `~/Documents/Psilocybin_Research_20251104/`
  - "compare React vs Vue" → `~/Documents/React_vs_Vue_Research_20251104/`
  - "AI safety trends" → `~/Documents/AI_Safety_Trends_Research_20251104/`
- If folder exists, use it; if not, create it
- This ensures clean organization and easy accessibility

**2. Save All Formats to Same Folder:**

**Markdown (Primary Source):**
- Save to: `[Documents folder]/research_report_[YYYYMMDD]_[topic_slug].md`
- Also save copy to: `~/.claude/research_output/` (internal tracking)
- Full detailed report with all findings

**HTML (McKinsey Style - ALWAYS GENERATE):**
- Save to: `[Documents folder]/research_report_[YYYYMMDD]_[topic_slug].html`
- Use McKinsey template: [mckinsey_template](./templates/mckinsey_report_template.html)
- Design principles: Sharp corners (NO border-radius), muted corporate colors (navy #003d5c, gray #f8f9fa), ultra-compact layout, info-first structure
- Place critical metrics dashboard at top (extract 3-4 key quantitative findings)
- Use data tables for dense information presentation
- 14px base font, compact spacing, no decorative gradients or colors
- OPEN in browser automatically after generation

**PDF (Professional Print - ALWAYS GENERATE):**
- Save to: `[Documents folder]/research_report_[YYYYMMDD]_[topic_slug].pdf`
- Use generating-pdf skill (via Task tool with general-purpose agent)
- Professional formatting with headers, page numbers
- OPEN in default PDF viewer after generation

**3. File Naming Convention:**
All files use same base name for easy matching:
- `research_report_20251104_psilocybin_2025.md`
- `research_report_20251104_psilocybin_2025.html`
- `research_report_20251104_psilocybin_2025.pdf`

**Length Requirements:**
- Quick mode: 1,000-2,000 words minimum
- Standard mode: 2,000-5,000 words minimum
- Deep mode: 3,000-7,000 words minimum
- UltraDeep mode: 5,000-10,000 words minimum

**Content Requirements:**
- Use [template](./templates/report_template.md) as exact structure
- Write 4-8 detailed findings (300-500 words each)
- Include specific data, statistics, dates, numbers (not vague statements)
- Multiple paragraphs per finding with evidence
- Synthesis section 500-1000 words
- DO NOT write summaries - write FULL analysis

**Writing Standards:**
- **Narrative-driven**: Write in flowing prose. Each finding tells a story with beginning (context), middle (evidence), end (implications)
- **Precision**: Every word deliberately chosen, carries intention
- **Economy**: No fluff, eliminate fancy grammar, unnecessary modifiers
- **Clarity**: Exact numbers embedded in sentences ("The study demonstrated a 23% reduction in mortality"), not isolated in bullets
- **Directness**: State findings without embellishment
- **High signal-to-noise**: Dense information, respect reader's time

**Bullet Point Policy:**
- Use bullets SPARINGLY: Only for distinct lists (product names, company roster, enumerated steps)
- NEVER use bullets as primary content delivery - they fragment thinking
- Each section requires substantive prose paragraphs (3-5 paragraphs minimum per finding)
- Example: Instead of "• Market size: $2.4B" write "The global market reached $2.4 billion in 2023, driven by increasing consumer demand and regulatory tailwinds [1]."

**Source Attribution Standards (Critical for Preventing Fabrication):**
- **Immediate citation**: Every factual claim followed by [N] citation in same sentence
- **Quote sources directly**: Use "According to [1]..." or "[1] reports..." for factual statements
- **Distinguish fact from synthesis**:
  - ✅ GOOD: "Mortality decreased 23% (p<0.01) in the treatment group [1]."
  - ❌ BAD: "Studies show mortality improved significantly."
- **No vague attributions**:
  - ❌ NEVER: "Research suggests...", "Studies show...", "Experts believe..."
  - ✅ ALWAYS: "Smith et al. (2024) found..." [1], "According to FDA data..." [2]
- **Label speculation explicitly**:
  - ✅ GOOD: "This suggests a potential mechanism..." (analysis, not fact)
  - ❌ BAD: "The mechanism is..." (presented as fact without citation)
- **Admit uncertainty**:
  - ✅ GOOD: "No sources found addressing X directly."
  - ❌ BAD: Fabricating a citation to fill the gap
- **Template pattern**: "[Specific claim with numbers/data] [Citation]. [Analysis/implication]."

**Deliver to user:**
1. Executive summary (inline in chat)
2. Organized folder path (e.g., "📁 All files saved to: ~/Documents/Psilocybin_Research_20251104/")
3. Confirmation of all three formats generated:
   - ✅ Markdown (source)
   - ✅ HTML (McKinsey-style, opened in browser)
   - ✅ PDF (professional print, opened in viewer)
4. Source quality assessment summary (credibility score, source count)
5. Next steps (if relevant)

**Generation Workflow (Execute in Order):**

**Step 1: Create Folder**
```bash
# Extract topic slug from research question
# Create folder: ~/Documents/[TopicName]_Research_[YYYYMMDD]/
mkdir -p ~/Documents/[folder_name]
```

**Step 2: Generate Markdown**
- Write comprehensive report using [template](./templates/report_template.md)
- Save to: `[folder]/research_report_[YYYYMMDD]_[slug].md`
- Also save copy to: `~/.claude/research_output/` (internal tracking)

**Step 3: Generate HTML (McKinsey Style)**
1. Read McKinsey template from `./templates/mckinsey_report_template.html`
2. Extract 3-4 key quantitative metrics from findings for dashboard
3. Convert FULL markdown to HTML (use Python script for proper conversion):
   - Convert ALL sections including bibliography
   - Bibliography entries: format each [N] citation as separate `<div class="bib-entry">` with hanging indent
   - URLs in bibliography: make clickable with `<a href="..." target="_blank">`
   - Headers: ## → `<h2 class="section-title">`, ### → `<h3 class="subsection-title">`
   - Citations in text: [1], [2] → `<span class="citation">[N]</span>`
   - Lists: convert markdown bullets to `<ul><li>` properly
   - Paragraphs: wrap non-HTML lines in `<p>` tags
4. Replace placeholders: {{TITLE}}, {{DATE}}, {{MODE}}, {{SOURCE_COUNT}}, {{CREDIBILITY}}, {{METRICS_DASHBOARD}}, {{CONTENT}}, {{BIBLIOGRAPHY}}
5. **Minimal Footer (Critical):**
   - **DEFAULT:** Page numbers only: "Page X of Y"
   - **IF DATE REQUESTED:** "Date | Page X of Y"
   - Sans-serif font (Helvetica Neue), 10-11px, gray color
   - **NEVER include:**
     - ❌ Disclaimers (unsolicited, not needed)
     - ❌ Word counts (unnecessary)
     - ❌ Report type/analysis type (obvious from content)
     - ❌ File paths, filenames, internal metrics
     - ❌ "For informational purposes" or any legal text
   - Keep absolute minimum - just pagination
6. Save to: `[folder]/research_report_[YYYYMMDD]_[slug].html`
7. Open in browser: `open [html_path]`

**Step 4: Generate PDF**
1. Use Task tool with general-purpose agent
2. Invoke generating-pdf skill with markdown as input
3. Save to: `[folder]/research_report_[YYYYMMDD]_[slug].pdf`
4. PDF will auto-open when complete

---

## Output Contract

**Format:** Comprehensive markdown report following [template](./templates/report_template.md) EXACTLY

**Required sections (all must be detailed):**
- Executive Summary (3-5 bullets, 50-250 words)
- Introduction (2-3 paragraphs: question, scope, methodology, assumptions)
- Main Analysis (4-8 findings, each 300-500 words with citations [1], [2], [3])
- Synthesis & Insights (500-1000 words: patterns, novel insights, implications)
- Limitations & Caveats (2-3 paragraphs: gaps, assumptions, uncertainties)
- Recommendations (3-5 immediate actions, 3-5 next steps, 3-5 further research)
- Bibliography (15-30 full citations with URLs)
- Methodology Appendix (2-3 paragraphs: process, sources, verification)

**Strictly Prohibited:**
- Placeholder text (TBD, TODO, [citation needed])
- Uncited major claims
- Broken links
- Missing required sections
- **Short summaries instead of detailed analysis**
- **Vague statements without specific evidence**

**Writing Standards (Critical):**
- **Narrative-driven**: Write in flowing prose with complete sentences that build understanding progressively
- **Precision**: Choose each word deliberately - every word must carry intention
- **Economy**: Eliminate fluff, unnecessary adjectives, fancy grammar
- **Clarity**: Use precise technical terms, avoid ambiguity. Embed exact numbers in sentences, not bullets
- **Directness**: State findings clearly without embellishment
- **Signal-to-noise**: High information density, respect reader's time
- **Bullet discipline**: Use bullets only for distinct lists (products, companies, steps). Default to prose paragraphs
- **Examples of precision**:
  - Bad: "significantly improved outcomes" → Good: "reduced mortality 23% (p<0.01)"
  - Bad: "several studies suggest" → Good: "5 RCTs (n=1,847) show"
  - Bad: "potentially beneficial" → Good: "increased biomarker X by 15%"
  - Bad: "• Market: $2.4B" → Good: "The market reached $2.4 billion in 2023, driven by consumer demand [1]."

**Quality gates (enforced by validator):**
- Minimum 2,000 words (standard mode)
- Average credibility score >60/100
- 3+ sources per major claim
- Clear facts vs. analysis distinction
- All sections present and detailed

---

## Error Handling & Stop Rules

**Stop immediately if:**
- 2 validation failures on same error → Pause, report, ask user
- <5 sources after exhaustive search → Report limitation, request direction
- User interrupts/changes scope → Confirm new direction

**Graceful degradation:**
- 5-10 sources → Note in limitations, proceed with extra verification
- Time constraint reached → Package partial results, document gaps
- High-priority critique issue → Address immediately

**Error format:**
```
⚠️ Issue: [Description]
📊 Context: [What was attempted]
🔍 Tried: [Resolution attempts]
💡 Options:
   1. [Option 1]
   2. [Option 2]
   3. [Option 3]
```

---

## Quality Standards (Always Enforce)

Every report must:
- 10+ sources (document if fewer)
- 3+ sources per major claim
- Executive summary <250 words
- Full citations with URLs
- Credibility assessment
- Limitations section
- Methodology documented
- No placeholders

**Priority:** Thoroughness over speed. Quality > speed.

---

## Inputs & Assumptions

**Required:**
- Research question (string)

**Optional:**
- Mode (quick/standard/deep/ultradeep)
- Time constraints
- Required perspectives/sources
- Output format

**Assumptions:**
- User requires verified, citation-backed information
- 10-50 sources available on topic
- Time investment: 5-45 minutes

---

## When to Use / NOT Use

**Use when:**
- Comprehensive analysis (10+ sources needed)
- Comparing technologies/approaches/strategies
- State-of-the-art reviews
- Multi-perspective investigation
- Technical decisions
- Market/trend analysis

**Do NOT use:**
- Simple lookups (use WebSearch)
- Debugging (use standard tools)
- 1-2 search answers
- Time-sensitive quick answers

---

## Scripts (Offline, Python stdlib only)

**Location:** `./scripts/`

- **research_engine.py** - Orchestration engine
- **validate_report.py** - Quality validation (8 checks)
- **citation_manager.py** - Citation tracking
- **source_evaluator.py** - Credibility scoring (0-100)

**No external dependencies required.**

---

## Progressive References (Load On-Demand)

**Do not inline these - reference only:**
- [Complete Methodology](./reference/methodology.md) - 8-phase details
- [Report Template](./templates/report_template.md) - Output structure
- [README](./README.md) - Usage docs
- [Quick Start](./QUICK_START.md) - Fast reference
- [Competitive Analysis](./COMPETITIVE_ANALYSIS.md) - vs OpenAI/Gemini

**Context Management:** Load files on-demand for current phase only. Do not preload all content.

---

<!-- STATIC CONTEXT BLOCK END -->
<!-- ⚡ Above content is cacheable (>1024 tokens, static) -->
<!-- 📝 Below: Dynamic content (user queries, retrieved data, generated reports) -->
<!-- This structure enables 85% latency reduction via prompt caching -->

---

## Dynamic Execution Zone

**User Query Processing:**
[User research question will be inserted here during execution]

**Retrieved Information:**
[Search results and sources will be accumulated here]

**Generated Analysis:**
[Findings, synthesis, and report content generated here]

**Note:** This section remains empty in the skill definition. Content populated during runtime only.
