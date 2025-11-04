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

**AUTONOMY PRINCIPLE:** This skill operates independently. Proceed with reasonable assumptions. Only stop for critical errors or genuinely incomprehensible queries.

### 1. Clarify (Rarely Needed - Prefer Autonomy)

**DEFAULT: Proceed autonomously. Make reasonable assumptions based on query context.**

**ONLY ask if CRITICALLY ambiguous:**
- Query is genuinely incomprehensible (e.g., "research the thing")
- Contradictory requirements (e.g., "quick 50-source ultradeep analysis")

**When in doubt: PROCEED with standard mode. User can redirect if needed.**

**Good autonomous assumptions:**
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

**Announce plan (then proceed immediately):**
- Briefly state: selected mode, estimated time, number of sources
- Example: "Starting standard mode research (5-10 min, 15-30 sources)"
- NO need to wait for approval - proceed directly to execution

---

### 3. Act (Phase Execution)

**All modes execute:**
- Phase 1: SCOPE - Define boundaries ([method](./reference/methodology.md#phase-1-scope))
- Phase 3: RETRIEVE - Gather 15-30 sources, spawn parallel agents
- Phase 8: PACKAGE - Generate report using [template](./templates/report_template.md)

**Standard+ adds:**
- Phase 2: PLAN - Strategy formulation
- Phase 4: TRIANGULATE - Verify 3+ sources per claim
- Phase 5: SYNTHESIZE - Generate novel insights

**Deep+ adds:**
- Phase 6: CRITIQUE - Red-team analysis
- Phase 7: REFINE - Address gaps

**Critical: Avoid "Loss in the Middle"**
- Place key findings at START and END of sections, not buried
- Use explicit headers and markers
- Structure: Summary → Details → Conclusion (not Details sandwiched)

**Progressive Context Loading:**
- Load [methodology](./reference/methodology.md) sections on-demand
- Load [template](./templates/report_template.md) only for Phase 8
- Don't inline everything - use references

---

### 4. Verify (Always Execute)

```bash
python scripts/validate_report.py --report [path]
```

**8 automated checks:**
1. Executive summary length (50-250 words)
2. Required sections present
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

**File Output:**
- Save as `.md` file to `~/.claude/research_output/`
- Filename format: `research_report_YYYYMMDD_HHMMSS.md`
- Example: `research_report_20251104_153045.md`

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
- Precision: Every word deliberately chosen, carries intention
- Economy: No fluff, eliminate fancy grammar, unnecessary modifiers
- Clarity: Exact numbers ("23% reduction"), not vague ("significant improvement")
- Directness: State findings without embellishment
- High signal-to-noise: Dense information, respect reader's time

**Deliver to user:**
1. Executive summary (inline in chat)
2. Confirmation that full report saved with file path
3. Source quality assessment summary
4. Next steps (optional)

**Offer:**
- Deep-dive any section
- Follow-up questions
- Alternative formats

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
- **Precision**: Choose each word deliberately - every word must carry intention
- **Economy**: Eliminate fluff, unnecessary adjectives, fancy grammar
- **Clarity**: Use precise technical terms, avoid ambiguity
- **Directness**: State findings clearly without embellishment
- **Signal-to-noise**: High information density, respect reader's time
- **Examples of precision**:
  - Bad: "significantly improved outcomes" → Good: "reduced mortality 23% (p<0.01)"
  - Bad: "several studies suggest" → Good: "5 RCTs (n=1,847) show"
  - Bad: "potentially beneficial" → Good: "increased biomarker X by 15%"

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
- <5 sources after exhaustive search → Report limitation, ask to proceed
- User interrupts/changes scope → Confirm new direction

**Graceful degradation:**
- 5-10 sources → Note in limitations, proceed with extra verification
- Time constraint hit → Package partial results, document gaps
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

**When uncertain:** Be thorough, not fast. Quality > speed.

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
- User wants verified, citation-backed info
- 10-50 sources available on topic
- Extended reasoning acceptable (5-45 min)

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

**Context Management:** Load these files only when explicitly needed for current phase. Do not preload all content.

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
