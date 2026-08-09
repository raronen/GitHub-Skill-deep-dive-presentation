# Deep Dive Presentation Skill

A Copilot skill for producing editable HTML deep-dive presentations grounded
in source code, architecture, end-to-end flows, and operational telemetry.

When LAIQ is available, the skill investigates live telemetry and adds
reproducible statistics such as traffic volume, latency percentiles, failure
rates, regional breakdowns, trends, and notable outliers.

## Install

Copy this repository to:

```text
%USERPROFILE%\.copilot\skills\deep-dive-presentation
```

The directory must contain both `SKILL.md` and `template.html`.

## Contents

- `SKILL.md` - research and presentation-generation instructions
- `template.html` - editable Reveal.js and Mermaid presentation template
