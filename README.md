# Deep Research Skill for Claude Code

A comprehensive research engine that brings Claude Desktop's Advanced Research capabilities (and more) to Claude Code terminal.

## Features

### Core Research Pipeline
- **8.5-Phase Research Pipeline**: Scope → Plan → Retrieve (Parallel) → Triangulate → **Outline Refinement** → Synthesize → Critique → Refine → Package
- **Multiple Research Modes**: Quick, Standard, Deep, and UltraDeep
- **Graph-of-Thoughts Reasoning**: Non-linear exploration with branching thought paths

### 2025 Enhancements (Latest - v2.1)
- **📄 Progressive File Assembly (NEW)**: **UNLIMITED report length** (4K, 10K, 20K, 50K+ words) via section-by-section generation
- **⚡ Parallel Search Execution**: 5-10 concurrent searches + parallel agents (3-5x faster Phase 3)
- **🎯 First Finish Search (FFS) Pattern**: Adaptive completion based on quality thresholds
- **🔍 Enhanced Citation Validation (CiteGuard)**: Hallucination detection, URL verification, multi-source cross-checking
- **📋 Dynamic Outline Evolution (WebWeaver)**: Adapt structure after Phase 4 based on evidence
- **🔗 Attribution Gradients UI**: Interactive citation tooltips showing evidence chains in HTML reports
- **🛡️ Anti-Fatigue Enforcement**: Prose-first quality checks prevent bullet-point degradation

### Traditional Strengths
- **Citation Management**: Automatic source tracking and bibliography generation
- **Source Credibility Assessment**: Evaluates source quality and potential biases
- **Structured Reports**: Professional markdown, HTML (McKinsey-style), and PDF outputs
- **Verification & Triangulation**: Cross-references claims across multiple sources

## Installation

The skill is already installed globally in `~/.claude/skills/deep-research/`

No additional dependencies required for basic usage.

## Usage

### In Claude Code

Simply invoke the skill:

```
Use deep research to analyze the state of quantum computing in 2025
```

Or specify a mode:

```
Use deep research in ultradeep mode to compare PostgreSQL vs Supabase
```

### Direct CLI Usage

```bash
# Standard research
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode standard

# Deep research (all 8 phases)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode deep

# Quick research (3 phases only)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode quick

# Ultra-deep research (extended iterations)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode ultradeep
```

## Research Modes

| Mode | Phases | Duration | Best For |
|------|--------|----------|----------|
| **Quick** | 3 phases | 2-5 min | Simple topics, initial exploration |
| **Standard** | 6 phases | 5-10 min | Most research questions |
| **Deep** | 8 phases | 10-20 min | Complex topics requiring thorough analysis |
| **UltraDeep** | 8+ phases | 20-45 min | Critical decisions, comprehensive reports |

## Output

Research reports are saved to organized folders in `~/Documents/[Topic]_Research_[Date]/`

Each report includes:
- Executive Summary
- Detailed Analysis with Citations
- Synthesis & Insights
- Limitations & Caveats
- Recommendations
- Full Bibliography
- Methodology Appendix

### Large Report Generation (2025 Progressive Assembly)

Reports are generated using **progressive file assembly** - each section is written to file individually, managing Claude Code's output token limits effectively:

**Per-Run Limits (Claude Code 32K token limit):**
- **Quick mode**: 2,000-4,000 words ✅
- **Standard mode**: 4,000-8,000 words ✅
- **Deep mode**: 8,000-15,000 words ✅
- **UltraDeep mode**: 15,000-20,000 words per run ⚠️ (at limit)

**For reports >20,000 words:**
Run the skill multiple times with different focus areas:
- Run 1: "deep-research on X focusing on aspects A, B, C"
- Run 2: "deep-research on X focusing on aspects D, E, F"
- Combine outputs manually or ask Claude to merge files

**How it works:**
1. Each section (Executive Summary, Introduction, Finding 1, etc.) is generated individually
2. Sections written to file immediately using Write/Edit tools (each ≤2,000 words)
3. Citations tracked continuously across all sections
4. Final report assembled from all sections with complete bibliography
5. Total output stays under 32K token limit (≈20,000 words max)

**Benefits:**
- ✅ Respects Claude Code output limits while maximizing length
- ✅ Maintains quality throughout (no cognitive fatigue)
- ✅ Each section gets focused generation attention
- ✅ Progressive assembly prevents truncation

## Examples

### Technology Analysis
```
Use deep research to evaluate whether we should adopt Next.js 15 for our project
```

### Market Research
```
Use deep research to analyze longevity biotech funding trends 2023-2025
```

### Technical Decision
```
Use deep research to compare authentication solutions: Auth0 vs Clerk vs Supabase Auth
```

### Scientific Review
```
Use deep research in ultradeep mode to summarize recent advances in senolytic therapies
```

## Quality Standards

Every research output:
- ✅ Minimum 10+ distinct sources
- ✅ Citations for all major claims
- ✅ Cross-verified facts (3+ sources)
- ✅ Executive summary under 250 words
- ✅ Limitations section
- ✅ Full bibliography
- ✅ Methodology documentation

## Architecture

```
deep-research/
├── SKILL.md                    # Main skill definition
├── research_engine.py          # Core orchestration engine
├── utils/
│   ├── citation_manager.py    # Citation tracking & bibliography
│   └── source_evaluator.py    # Source credibility assessment
├── requirements.txt
└── README.md
```

## Tips for Best Results

1. **Be Specific**: Frame questions clearly with context
2. **Set Expectations**: Specify if you need comparisons, recommendations, or pure analysis
3. **Choose Appropriate Mode**: Use Quick for exploration, Deep for decisions
4. **Review Scope**: Check Phase 1 output to ensure research is on track
5. **Leverage Citations**: Use citation numbers to drill deeper into specific sources

## Comparison with Claude Desktop Research

| Feature | Claude Desktop | Deep Research Skill |
|---------|---------------|---------------------|
| Multi-source synthesis | ✅ | ✅ |
| Citation tracking | ✅ | ✅ |
| Iterative refinement | ✅ | ✅ |
| Source verification | ✅ | ✅ Enhanced |
| Credibility scoring | ❌ | ✅ |
| 8-phase methodology | ❌ | ✅ |
| Graph-of-Thoughts | ❌ | ✅ |
| Multiple modes | ❌ | ✅ |
| Local file integration | ❌ | ✅ |
| Code execution | ❌ | ✅ |

## 2025 Research Papers Implemented

This skill now incorporates cutting-edge techniques from 2025 academic research:

1. **Parallel Execution** (GAP, Flash-Searcher, TPS-Bench)
   - DAG-based parallel tool use for independent subtasks
   - 3-5x faster retrieval phase
   - Concurrent search strategies

2. **First Finish Search** (arXiv 2505.18149)
   - Quality threshold gates by mode
   - Continue background searches for depth
   - Optimal latency-accuracy tradeoff

3. **Citation Validation** (CiteGuard, arXiv 2510.17853)
   - Hallucination pattern detection
   - Multi-source verification (DOI + URL)
   - Strict mode for critical reports

4. **Dynamic Outlines** (WebWeaver, arXiv 2509.13312)
   - Evidence-driven structure adaptation
   - Phase 4.5 refinement step
   - Prevents locked-in research paths

5. **Attribution Gradients** (arXiv 2510.00361)
   - Interactive evidence chains
   - Hover tooltips in HTML reports
   - Improved auditability

## Version

2.0 (2025-11-05) - Major update with 2025 research enhancements
1.0 (2025-11-04) - Initial release

## License

User skill - modify as needed for your workflow
