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
Mermaid source can be edited and re-rendered, slides can be added/duplicated/
deleted, and Export HTML downloads the edited deck as a new re-editable file.
Explain these controls after delivering the deck.

Do not fabricate facts, endpoints, ownership, or source links. Mark anything
unverified as TODO and keep the deck focused on the requested subject.
