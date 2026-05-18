# Research Presentation Deliverable Pattern

Use this when a deep-research request explicitly asks for a deck, presentation, slides, or board/client-ready visual artifact.

## Deliverable bundle

Create a self-contained folder under `~/Documents/[Topic]_Research_[YYYYMMDD]/` with:

- `research_brief.md` — narrative source-of-truth with executive summary, key findings, implications, limitations, and cited source notes.
- `sources.json` or `sources.jsonl` — stable source registry with canonical source IDs, title, publisher, URL, date/accessed date, and the claims supported.
- `.pptx` deck — concise, visual presentation artifact.
- `.pdf` deck export — render-verified shareable copy.
- Optional slide images/thumbnails for QA when useful.

## Research-to-deck workflow

1. Scope audience and topic from the prompt; if the user asks generally, assume a practical executive audience and recent 1-2 year trend horizon.
2. Collect source evidence before writing slides. Prioritize recent market reports, industry surveys, professional society stats, regulatory/earnings sources, and reputable consumer research.
3. Build a brief first, then transform it into a slide outline. Avoid inventing slide claims directly from memory.
4. Keep the deck insight-led: one main takeaway per slide, with chart/stat/callout support where possible.
5. Preserve evidence traceability: every quantitative or factual slide claim should map back to the source registry or brief.
6. Export `.pptx` to `.pdf` and perform visual QA before delivery. If the PowerPoint skill is available, follow its QA loop.
7. Deliver both `.pptx` and `.pdf` paths/media attachments, plus mention the brief and source registry paths.

## Slide structure that worked well

For market/trend requests, a good default is 8-12 slides:

1. Title / scope
2. Executive snapshot
3. Consumer attitudes / demand drivers
4. Market size and growth
5. Segment or procedure mix
6. Injectable trends and share shifts
7. Emerging growth vectors (e.g., wellness, GLP-1 adjacency, regenerative positioning)
8. Provider/channel landscape
9. Strategic implications
10. Watchouts, limitations, and sources

## Existing-materials / source-packet add-on

When the user asks whether something "already exists," asks to download decks/reports, or wants a combined evidence packet:

1. Run a targeted search for presentation/report files (`filetype:ppt`, `filetype:pptx`, `filetype:pdf`) plus query variants for the specific domain, audience, and recency window.
2. Create an `existing_decks/` or `source_materials/` subfolder inside the research folder.
3. Download every accessible source file and preserve exact filenames when practical. For blocked/form-protected sources, do **not** silently omit them; write a manifest note with URL, attempted method, HTTP/status/error, and suggested manual retrieval path.
4. Produce a shortlist Markdown file that ranks the best source materials and explains each source's likely bias (consultancy, investor deck, manufacturer, clinic/operator, survey vendor, etc.).
5. Build a combined PDF packet when useful: add front matter with title, access date, source list, blocked-source notes, and table of contents/bookmarks if tooling supports it.
6. Save manifests such as `download_manifest.json` and `combined_manifest.json` so a later agent can reproduce or audit the bundle.
7. If the user asks to "attach sources," send a zip containing the original downloaded files plus manifests and shortlist, not only the final merged PDF.
8. If the user asks for the presentation in another format after delivery, attach the exact requested artifact directly (`.pptx` for editing, `.pdf` for fixed review) without re-explaining the whole research process.

## Pitfalls

- Do not deliver only a deck without preserving the research substrate; future edits need the brief and source registry.
- Do not bury citations only in speaker notes unless the user asked for a clean client deck. At minimum, keep source IDs or source slide accessible.
- Avoid overclaiming early-stage trends. Label directional signals separately from hard market-size data.
- When data sources conflict, explain definition differences: procedure share, revenue share, patient count, and unit volume can all tell different stories.
- Do not overstate failed downloads as unavailable research. Many market decks are protected by forms, CDNs, or hotlink rules; capture them as blocked-source notes and include the original URLs for manual retrieval.