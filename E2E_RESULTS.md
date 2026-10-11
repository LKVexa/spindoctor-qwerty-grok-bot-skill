# E2E results - spindoctor-qwerty-grok-bot-skill 1.1.0

Host: **stand-in skill loader** (`tests/skill_loader.py`), not Grok Bot. Skills can't be installed into Grok Bot from outside, so the
loader does what a skills-capable host does, following the Agent Skills format: discover the folder, validate the frontmatter,
build the `<available_skills>` catalog, activate the skill, check the bundled files it mentions and run its documented commands
from the skill folder like an agent's shell tool. The reference validator `skills-ref` 0.1.1 (`agentskills validate` / `to-prompt`)
checks the folder too. The upload zip is built twice (same SHA-256) and loaded from a read-only extracted copy. Python 3.13.5, Linux.

Not tested: Grok Bot itself (how it ranks and picks skills, approval prompts, its upload and file-sending tools), a real model
following SKILL.md, Windows, macOS.

## Host check: 29 passed, 0 failed, 0 skipped

| Result | Check |
|---|---|
| PASS | static: every .py file has a GPL-3.0-or-later SPDX header (27 files) |
| PASS | static: SKILL.md frontmatter valid (name, description, license, compatibility, metadata) |
| PASS | static: metadata version 1.1.0, engine SpinDoctor 3.1.2, license GPL-3.0-or-later |
| PASS | static: guardrail in description and body |
| PASS | static: skill folder carries the GPL-3.0 LICENSE (self-contained when copied alone) |
| PASS | static: no host-specific plugin variables or personal paths in the skill |
| PASS | skills-ref: `agentskills validate` accepts the folder |
| PASS | skills-ref: `agentskills to-prompt` catalog entry names spindoctor-qwerty |
| PASS | loader: discovers exactly one valid skill in the repo (spindoctor-qwerty) |
| PASS | loader: <available_skills> catalog has name, description and SKILL.md location |
| PASS | loader: every bundled file the body mentions exists (4) |
| PASS | loader: documented commands found (7) |
| PASS | run (skill folder): functions |
| PASS | run (skill folder): run "q.circuit new bell 2" "q.circuit add h 0" "q.circuit add cx 0 1"  |
| PASS | run (skill folder): script examples/theory/xbasis.q |
| PASS | run (skill folder): presets ghz |
| PASS | run (skill folder): preset qc-061 shots=500 |
| PASS | run (skill folder): theory examples/bell_theory_args.json |
| PASS | run (skill folder): report |
| PASS | output: function table is Markdown (Function \| What it does \| Command to type) |
| PASS | output: Bell theory verdict supported; TXT+PDF theory reports valid |
| PASS | output: Bell run ok; reports under ~/spindoctor-workspace; PDF valid |
| PASS | run (other folder, full path, --workspace): preset qc-001 ok, reports in that workspace |
| PASS | tool bridge: chat theory supported, excerpts recorded under 'Source: chat history', PDF valid |
| PASS | tool bridge: 300-qubit register refused (1..298, SpinDoctor's own range error) |
| PASS | zip: build is reproducible (same SHA-256 twice): 7018b18d3326e046 |
| PASS | zip: one top folder spindoctor-qwerty/ with SKILL.md; no caches or generated PDFs (38 files) |
| PASS | zip: extracted read-only copy loads and runs the theory example (no writes into the skill) |
| PASS | mcp: tests/e2e_mcp.py against the bundled MCP server: SUMMARY 12/12 passed in 13.0s |

## Shared end-to-end suite through the bundled MCP server: 12/12

Started as `python3 spindoctor-qwerty/scripts/spindoctor_mcp.py` (the optional MCP route of the skill).

| Result | Check |
|---|---|
| PASS | initialize (server spindoctor-qwerty 1.1.0) |
| PASS | tools/list exposes the 6 tools |
| PASS | function table (Markdown, 19 sections, 298-qubit limits listed) |
| PASS | 241 presets listed |
| PASS | one script per command family (16 families, every table example) |
| PASS | 298-qubit circuit with mcx7 (prepared-factor-Born-Z) |
| PASS | q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped) |
| PASS | theory from a file -> supported, TXT+PDF report |
| PASS | theory from a chat summary + quoted excerpts -> supported |
| PASS | theory from an exported chat transcript -> supported |
| PASS | presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences) |
| PASS | TXT+PDF reports valid (255 PDFs, 255 TXT twins) |

## Runs

- Clean-room copy, 2026-10-11 PT: host check 29/29 (0 skipped), shared E2E suite 12/12; upload zip SHA-256 7018b18d3326e046ad7bca089ded40884852dcb08e6730c1a0a43f60adbe931d (38 files), identical on rebuild.
