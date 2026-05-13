# Auto-Continuation Protocol

## When to Use

Trigger auto-continuation when report exceeds 18,000 words in single run.

---

## Strategy Overview

1. Generate sections 1-10 (stay under 18K words)
2. Save continuation state file with context preservation
3. Spawn continuation agent via Task tool
4. Continuation agent: Reads state -> Generates next batch -> Spawns next if needed
5. Chain continues recursively until complete

---

## Continuation State File

**Location:** `./[topic]_[YYYYMMDD]/research_output/continuation_state_[report_id].json` (inside the topic folder created in the cwd, not in `~/.claude/`)

```json
{
  "version": "3.0.0",
  "report_id": "[unique_id]",
  "file_path": "[absolute_path_to_report.md]",
  "mode": "[quick|standard|deep|ultradeep]",

  "progress": {
    "sections_completed": ["list of section IDs"],
    "total_planned_sections": 15,
    "word_count_so_far": 12000,
    "continuation_count": 1
  },

  "artifacts": {
    "sources_path": "[folder]/sources.jsonl",
    "evidence_path": "[folder]/evidence.jsonl",
    "claims_path": "[folder]/claims.jsonl",
    "run_manifest_path": "[folder]/run_manifest.json"
  },

  "research_context": {
    "research_question": "[original question]",
    "key_themes": ["theme1", "theme2"],
    "main_findings_summary": [
      "Finding 1: [100-word summary]",
      "Finding 2: [100-word summary]"
    ],
    "narrative_arc": "middle"
  },

  "quality_metrics": {
    "avg_words_per_finding": 1500,
    "citation_density": 5.2,
    "prose_vs_bullets_ratio": "85% prose",
    "writing_style": "technical-precise-data-driven"
  },

  "next_sections": [
    {"id": 11, "type": "finding", "title": "Finding X", "target_words": 1500},
    {"id": 12, "type": "synthesis", "title": "Synthesis", "target_words": 1000}
  ]
}
```

---

## Spawning Continuation Agent

Use Task tool:

```
Task(
  subagent_type="general-purpose",
  description="Continue deep-research report generation",
  prompt="""
CONTINUATION TASK: Continue existing deep-research report.

CRITICAL INSTRUCTIONS:
1. Read continuation state: [topic_dir]/research_output/continuation_state_[report_id].json
2. Read existing report: [file_path from state]
3. Read LAST 3 completed sections for flow/style
4. Load research context: themes, narrative arc, writing style
5. Load source registry from state.artifacts.sources_path — use stable source_ids, assign display numbers via citation_manager.py
6. Maintain quality metrics (avg words, citation density, prose ratio)

YOUR TASK:
Generate next batch (stay under 18,000 words):
[List next_sections from state]

Use Write/Edit to append to: [file_path]

QUALITY GATES:
- Words per section: Within +/-20% of avg_words_per_finding
- Citation density: Match +/-0.5 per 1K words
- Prose ratio: Maintain >=80%
- Theme alignment: Section ties to key_themes

After generating:
- If more sections remain: Update state, spawn next agent
- If final sections: Generate bibliography, verify report, cleanup state
"""
)
```

---

## Continuation Agent Quality Protocol

### Context Loading (CRITICAL)

1. Read continuation_state.json -> Load ALL context
2. Read existing report file -> Review last 3 sections
3. Extract patterns:
   - Sentence structure complexity
   - Technical terminology used
   - Citation placement patterns
   - Paragraph transition style

### Pre-Generation Checklist

- [ ] Loaded research context (themes, question, narrative arc)
- [ ] Reviewed previous sections for flow
- [ ] Loaded source registry from artifacts (stable source_ids, not citation numbers)
- [ ] Loaded quality targets (words, density, style)
- [ ] Understand narrative position (beginning/middle/end)

### Per-Section Generation

1. Generate section content
2. Quality checks:
   - Word count within +/-20%
   - Citation density matches
   - Prose ratio >=80%
   - Theme connection verified
   - Style consistent
3. If ANY fails: Regenerate
4. If passes: Write to file, update state

### Handoff Decision

Calculate: Current words + remaining sections x avg_words_per_section
- If total < 18K: Generate all + finish
- If total > 18K: Generate partial, update state, spawn next agent

### Final Agent Responsibilities

- Generate final content sections
- Generate COMPLETE bibliography from state.citations.bibliography_entries
- Read entire assembled report
- Run validation: `python scripts/validate_report.py --report [path]`
- Delete continuation_state.json (cleanup)
- Report complete to user

---

## User Communication

After spawning continuation:
```
Report Generation: Part 1 Complete (N sections, X words)
Auto-continuing via spawned agent...
   Next batch: [section list]
   Progress: [X%] complete
```
