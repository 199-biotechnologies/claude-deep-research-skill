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
- Phase 3: RETRIEVE - Parallel search execution (5-10 concurrent searches + agents) ([method](./reference/methodology.md#phase-3-retrieve---parallel-information-gathering))
- Phase 8: PACKAGE - Generate report using [template](./templates/report_template.md)

**Standard/Deep/UltraDeep execute:**
- Phase 2: PLAN - Strategy formulation
- Phase 4: TRIANGULATE - Verify 3+ sources per claim
- Phase 4.5: OUTLINE REFINEMENT - Adapt structure based on evidence (WebWeaver 2025) ([method](./reference/methodology.md#phase-45-outline-refinement---dynamic-evolution-webweaver-2025))
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

**Parallel Execution Requirements (CRITICAL for Speed):**

**Phase 3 RETRIEVE - Mandatory Parallel Search:**
1. **Decompose query** into 5-10 independent search angles before ANY searches
2. **Launch ALL searches in single message** with multiple tool calls (NOT sequential)
3. **Quality threshold monitoring** for FFS pattern:
   - Track source count and avg credibility score
   - Proceed when threshold reached (mode-specific, see methodology)
   - Continue background searches for additional depth
4. **Spawn 3-5 parallel agents** using Task tool for deep-dive investigations

**Example correct execution:**
```
[Single message with 8+ parallel tool calls]
WebSearch #1: Core topic semantic
WebSearch #2: Technical keywords
WebSearch #3: Recent 2024-2025 filtered
WebSearch #4: Academic domains
WebSearch #5: Critical analysis
WebSearch #6: Industry trends
Task agent #1: Academic paper analysis
Task agent #2: Technical documentation deep dive
```

**❌ WRONG (sequential execution):**
```
WebSearch #1 → wait for results → WebSearch #2 → wait → WebSearch #3...
```

**✅ RIGHT (parallel execution):**
```
All searches + agents launched simultaneously in one message
```

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
- **Attribution Gradients (2025):** Wrap each citation [N] in `<span class="citation">` with nested tooltip div showing source details
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

**Length Requirements (UNLIMITED with Progressive Assembly):**
- Quick mode: 2,000+ words (baseline quality threshold)
- Standard mode: 4,000+ words (comprehensive analysis)
- Deep mode: 6,000+ words (thorough investigation)
- UltraDeep mode: 10,000-50,000+ words (NO UPPER LIMIT - as comprehensive as evidence warrants)

**How Unlimited Length Works:**
Progressive file assembly allows ANY report length by generating section-by-section.
Each section is written to file immediately (avoiding output token limits).
Complex topics with many findings? Generate 20, 30, 50+ findings - no constraint!

**Content Requirements:**
- Use [template](./templates/report_template.md) as exact structure
- Generate each section to APPROPRIATE depth (determined by evidence, not word targets)
- Include specific data, statistics, dates, numbers (not vague statements)
- Multiple paragraphs per finding with evidence (as many as needed)
- Each section gets focused generation attention
- DO NOT write summaries - write FULL analysis

**Writing Standards:**
- **Narrative-driven**: Write in flowing prose. Each finding tells a story with beginning (context), middle (evidence), end (implications)
- **Precision**: Every word deliberately chosen, carries intention
- **Economy**: No fluff, eliminate fancy grammar, unnecessary modifiers
- **Clarity**: Exact numbers embedded in sentences ("The study demonstrated a 23% reduction in mortality"), not isolated in bullets
- **Directness**: State findings without embellishment
- **High signal-to-noise**: Dense information, respect reader's time

**Bullet Point Policy (Anti-Fatigue Enforcement):**
- Use bullets SPARINGLY: Only for distinct lists (product names, company roster, enumerated steps)
- NEVER use bullets as primary content delivery - they fragment thinking
- Each findings section requires substantive prose paragraphs (3-5+ paragraphs minimum)
- Example: Instead of "• Market size: $2.4B" write "The global market reached $2.4 billion in 2023, driven by increasing consumer demand and regulatory tailwinds [1]."

**Anti-Fatigue Quality Check (Apply to EVERY Section):**
Before considering a section complete, verify:
- [ ] **Paragraph count**: ≥3 paragraphs for major sections (## headings)
- [ ] **Prose-first**: <20% of content is bullet points (≥80% must be flowing prose)
- [ ] **No placeholders**: Zero instances of "Content continues", "Due to length", "[Sections X-Y]"
- [ ] **Evidence-rich**: Specific data points, statistics, quotes (not vague statements)
- [ ] **Citation density**: Major claims cited within same sentence

**If ANY check fails:** Regenerate the section before moving to next.

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
2. Organized folder path (e.g., "All files saved to: ~/Documents/Psilocybin_Research_20251104/")
3. Confirmation of all three formats generated:
   - Markdown (source)
   - HTML (McKinsey-style, opened in browser)
   - PDF (professional print, opened in viewer)
4. Source quality assessment summary (source count)
5. Next steps (if relevant)

**Generation Workflow: Progressive File Assembly (Unlimited Length)**

**Phase 8.1: Setup**
```bash
# Extract topic slug from research question
# Create folder: ~/Documents/[TopicName]_Research_[YYYYMMDD]/
mkdir -p ~/Documents/[folder_name]

# Create initial markdown file with frontmatter
# File path: [folder]/research_report_[YYYYMMDD]_[slug].md
```

**Phase 8.2: Progressive Section Generation**

**CRITICAL STRATEGY:** Generate and write each section individually to file using Write/Edit tools.
This allows unlimited report length while keeping each generation manageable.

**Initialize Citation Tracking:**
```
citations_used = []  # Maintain this list in working memory throughout
```

**Section Generation Loop:**

1. **Executive Summary**
   - Generate: Comprehensive summary (as long as needed, typically 200-300 words)
   - Tool: Write initial file content
   - Track: Extract citations [N], append to citations_used list
   - Progress: "Generated Executive Summary ✓"

2. **Introduction**
   - Generate: Context, research question, scope (as long as needed)
   - Tool: Edit file (append to existing content)
   - Track: Extract new citations, append to citations_used
   - Progress: "Generated Introduction ✓"

3. **Main Analysis - Finding Generation Loop**

   FOR EACH finding (number determined in Phase 2 PLAN):
     a. Generate finding section completely
        - Length: As appropriate for evidence (could be 400 words, could be 1,500 words)
        - Structure: Opening paragraph + evidence paragraphs + implications
        - Style: 3-5+ paragraphs of narrative prose (NOT bullets)
        - Data: Specific numbers, statistics, quotes with citations

     b. Write to file immediately
        - Tool: Edit (append to file)
        - Track: Extract citations used, append to citations_used

     c. Report progress
        - Example: "Generated Finding 3 of 12 ✓ (847 words, citations [15]-[21])"

     d. Move to next finding

   **No limit on number of findings!** Generate as many as evidence supports.
   If topic requires 30 findings for comprehensive coverage, generate all 30.

4. **Synthesis & Insights**
   - Generate: Novel insights beyond source statements (as long as needed for synthesis)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Synthesis ✓"

5. **Limitations & Caveats**
   - Generate: Counterevidence, gaps, uncertainties (appropriate depth)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Limitations ✓"

6. **Recommendations**
   - Generate: Immediate actions, next steps, research needs (appropriate depth)
   - Tool: Edit (append to file)
   - Track: Extract citations, append to citations_used
   - Progress: "Generated Recommendations ✓"

7. **Bibliography (CRITICAL - ALL Citations)**
   - Generate: COMPLETE bibliography with EVERY citation from citations_used list
   - Format: [1], [2], [3]... [N] - each citation gets full entry
   - Verification: Check citations_used list - if list contains [1] through [73], generate all 73 entries
   - NO ranges ([1-50]), NO placeholders ("Additional citations"), NO truncation
   - Tool: Edit (append to file)
   - Progress: "Generated Bibliography ✓ (N citations)"

8. **Methodology Appendix**
   - Generate: Research process, verification approach (appropriate depth)
   - Tool: Edit (append to file)
   - Progress: "Generated Methodology ✓"

**Phase 8.3: Verify Complete Report**
- Read final assembled markdown file
- Count sections (verify all present)
- Check for truncation patterns (validate no placeholders)
- Confirm citations_used matches bibliography entries
- Save copy to: `~/.claude/research_output/` (internal tracking)

**Anti-Fatigue Built-In:**
Because each section is generated independently with focused attention,
quality remains high throughout. No cognitive overload from generating
20,000 words in one shot. Each 500-1,500 word generation is manageable.

**Generate HTML (McKinsey Style)**
1. Read McKinsey template from `./templates/mckinsey_report_template.html`
2. Extract 3-4 key quantitative metrics from findings for dashboard
3. Convert markdown to HTML in TWO parts (use Python script for proper conversion):

   **Part A: {{CONTENT}} - Sections 1-6 + Appendix (NOT Bibliography):**
   - Executive Summary → Synthesis & Insights → Limitations → Recommendations → Appendix: Methodology
   - Headers: ## → `<h2 class="section-title">`, ### → `<h3 class="subsection-title">`

   **Part B: {{BIBLIOGRAPHY}} - Section 7 only (separate from content):**
   - Extract "## Bibliography" section from markdown
   - Format each [N] citation as separate `<div class="bib-entry">` with hanging indent
   - URLs: make clickable with `<a href="..." target="_blank">`
   - DO NOT include Bibliography in {{CONTENT}} - it goes in {{BIBLIOGRAPHY}} placeholder only

   **Formatting rules for both parts:**
   - **Citations with Attribution Gradients (in {{CONTENT}} only):** Convert [N] to interactive tooltips:
     ```html
     <span class="citation">[N]
       <span class="citation-tooltip">
         <div class="tooltip-title">[Source Title]</div>
         <div class="tooltip-source">[Author (Year)]</div>
         <div class="tooltip-claim">
           <div class="tooltip-claim-label">Supports Claim:</div>
           [Extract sentence containing this citation from report]
         </div>
       </span>
     </span>
     ```
   - Lists: convert markdown bullets to `<ul><li>` properly
   - Paragraphs: wrap non-HTML lines in `<p>` tags

4. Replace placeholders in template:
   - {{TITLE}} - Report title
   - {{DATE}} - Generation date
   - {{MODE}} - Research mode (Quick/Standard/Deep/UltraDeep)
   - {{SOURCE_COUNT}} - Number of sources
   - {{CREDIBILITY}} - Average credibility score
   - {{METRICS_DASHBOARD}} - Metrics HTML from step 2
   - {{CONTENT}} - Sections 1-6 + Appendix (from Part A above)
   - {{BIBLIOGRAPHY}} - Bibliography HTML only (from Part B above)
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

**Generate PDF**
1. Use Task tool with general-purpose agent
2. Invoke generating-pdf skill with markdown as input
3. Save to: `[folder]/research_report_[YYYYMMDD]_[slug].pdf`
4. PDF will auto-open when complete

---

## Output Contract

**Format:** Comprehensive markdown report following [template](./templates/report_template.md) EXACTLY

**Required sections (all must be detailed):**
- Executive Summary (2-3 concise paragraphs, 50-250 words)
- Introduction (2-3 paragraphs: question, scope, methodology, assumptions)
- Main Analysis (4-8 findings, each 300-500 words with citations [1], [2], [3])
- Synthesis & Insights (500-1000 words: patterns, novel insights, implications)
- Limitations & Caveats (2-3 paragraphs: gaps, assumptions, uncertainties)
- Recommendations (3-5 immediate actions, 3-5 next steps, 3-5 further research)
- **Bibliography (CRITICAL - see rules below)**
- Methodology Appendix (2-3 paragraphs: process, sources, verification)

**Bibliography Requirements (ZERO TOLERANCE - Report is UNUSABLE without complete bibliography):**
- ✅ MUST include EVERY citation [N] used in report body (if report has [1]-[50], write all 50 entries)
- ✅ Format: [N] Author/Org (Year). "Title". Publication. URL (Retrieved: Date)
- ✅ Each entry on its own line, complete with all metadata
- ❌ NO placeholders: NEVER use "[8-75] Additional citations", "...continue...", "etc.", "[Continue with sources...]"
- ❌ NO ranges: Write [3], [4], [5]... individually, NOT "[3-50]"
- ❌ NO truncation: If 30 sources cited, write all 30 entries in full
- ⚠️ Validation WILL FAIL if bibliography contains placeholders or missing citations
- ⚠️ Report is GARBAGE without complete bibliography - no way to verify claims

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
