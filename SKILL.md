---
name: deep-dive-presentation
description: Produce a self-contained, editable .html slide-deck deep dive on a given subject with architecture, data flow, E2E walkthroughs, concepts, component responsibilities, why, and verified msazure source links. Expand to as many slides as the subject needs.
---

# Deep Dive Presentation Builder

Use this skill when the user wants a detailed knowledge-transfer presentation
for a service, feature, component, flow, or team transition.

Research the subject in the active repository before writing the deck. Ground
claims in real source/configuration, explain what each component does and why
it exists, trace the complete E2E request and data flows, and document failure
modes, observability, configuration, and ownership.

When LAIQ telemetry tools are available, telemetry investigation is required,
not optional:

1. Resolve the relevant service, deployment, operation names, metrics, logs,
   traces, dimensions, and identifiers from source and configuration.
2. Call `laiq-get_investigation_playbook` before querying service telemetry.
   Read the relevant files it lists with
   `laiq-read_investigation_knowledge_file`.
3. For Log Analytics or Application Insights, call
   `laiq-get_workspace_knowledge` before
   `laiq-loganalytics_query`. For ADX data, use `laiq-kusto_query` only after
   confirming the cluster, database, table, and required filters from the
   playbook or source. Use Geneva/MDM telemetry when it is the authoritative
   source for the area.
4. Query a useful recent window and, when meaningful, a comparable baseline.
   Prefer aggregates that illuminate the subject: request or event volume,
   throughput, p50/p95/p99 latency, success and failure rates, throttling,
   dependency health, resource utilization, regional or operation breakdowns,
   trend changes, and statistically notable outliers. Adapt the statistics to
   the component instead of mechanically including every metric.
5. Validate surprising results with a second query or breakdown. Distinguish
   correlation from causation, report sample sizes and denominators, and do not
   treat missing telemetry as zero.
6. Add one or more telemetry slides that explain what the statistics mean for
   the architecture, operating envelope, bottlenecks, and failure modes. Include
   the exact source, UTC time range, retrieval time, filters, aggregation, and
   query text in speaker notes so results are reproducible.

Use aggregate telemetry only. Do not expose tenant, subscription, workspace,
user, query-text, token, or other sensitive values. If LAIQ access is
unavailable, the relevant telemetry source cannot be resolved, or the sample
is too small, mark the statistics as unavailable or inconclusive rather than
fabricating representative numbers. Never substitute memory-bank targets,
documentation claims, or configuration limits for observed production data.

Create a single editable HTML file using the sibling `template.html` shipped
with this skill, or the repository template when available:

`<repo>/.github/skills/deep-dive-presentation/template.html`

The installed user-level template is next to this file under
`%USERPROFILE%\.copilot\skills\deep-dive-presentation\template.html`.

If no repository template is available, create a self-contained HTML deck with
Reveal.js and Mermaid loaded from CDN. Include:

- Architecture and component diagrams
- E2E sequence diagrams
- Data transformation/data-flow diagrams
- Concepts and glossary
- Detailed component slides explaining responsibility and why
- Configuration, dependencies, failure modes, telemetry, and mitigations
- LAIQ-backed operational statistics with scope, time range, sample size, and
  interpretation
- References and speaker notes with file:line citations
- A visible Sources row on every substantive slide

Every source row must contain clickable, verified `https://msazure...` links
where applicable. Prefer exact file/blob links with line anchors. Otherwise
link to the relevant repository directory, PR, work item, wiki page, or
pipeline. Derive URLs from the repository remote and never invent a link.
Repeat important links in speaker notes. For telemetry evidence without a
stable URL, identify the LAIQ source, workspace or cluster/database, UTC time
range, and query; link only to a portal URL returned by LAIQ or another verified
source.

There is no fixed slide count. A small topic may use 9-12 slides; a broad topic
may require 20, 30, or more. Add slides for each meaningful component,
transformation, branch, concept, or failure mode. Never compress a deep dive
to a target count.

The HTML must support in-browser editing: Edit Mode makes text contenteditable,
Mermaid source can be edited and re-rendered, and slides can be added/duplicated/
deleted. Include a prominent Save HTML control that uses the File System Access
API to choose a file once, persist the file handle in IndexedDB when supported,
and overwrite that file on later saves after permission is granted. Save must
serialize the complete current deck as a standalone, re-editable HTML file,
including text edits, slide changes, and editable Mermaid source. Show explicit
save success, cancellation, and failure status; never silently claim success.
Keep Export HTML as a fallback that downloads a new re-editable file when direct
save is unavailable. Explain these controls after delivering the deck.

Use a presentation-first, fixed-viewport layout matching the established Draft
KT deck style:

- Render exactly one Reveal slide at a time; never present slides as a vertically
  scrolling document.
- Bundle the pinned Reveal.js CSS/JavaScript and Mermaid JavaScript into the HTML
  instead of depending on CDN loading. Embedded Copilot browser canvases may
  block external scripts; a missing Reveal runtime degrades into a long scrolling
  page with nonfunctional navigation.
- Set `html`, `body`, and `.reveal` to the full viewport and hide page overflow.
- Use Reveal's native bottom-right previous/next arrow controls with faded back
  arrows, a progress bar, linear navigation, and keyboard navigation.
- Keep the editing toolbar fixed at the top-right and the add-slide control fixed
  near the bottom edge so neither participates in document flow.
- Size slide content to fit the 1280x800 stage at narrow embedded-canvas widths.
  Prefer responsive native HTML/CSS diagrams over unstable or cropped Mermaid
  layouts when a diagram does not fit.
- Before delivery, verify that both navigation arrows change slides, the browser
  page has no vertical scrollbar, and the deck remains usable in Edit Mode.

When opening a deck in an embedded Copilot browser canvas, direct browser file
writes may be blocked. In that case, use the sibling `deck_save_server.py`:
start it detached on `127.0.0.1` with the deck path, an available port, and a
fresh random token, then open `http://127.0.0.1:<port>/?token=<token>` in the
canvas. The template detects that URL and Save HTML posts the serialized deck
to the localhost-only server, which atomically overwrites only the configured
file. Never reuse or expose the token outside that local URL.

Do not fabricate facts, endpoints, ownership, or source links. Mark anything
unverified as TODO and keep the deck focused on the requested subject.
