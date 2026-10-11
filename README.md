# SpinDoctor Qwerty skill for Grok Bot

An **Agent Skills** folder (`SKILL.md` + bundled scripts) that lets Grok Bot - or any agent that loads skills and has a shell - run
the **SpinDoctor 3.1.2 quantum-circuit simulator**: `q.*` circuit scripts (1-298 logical qubits), the 241 built-in presets, folders
of command files (`q.folder`), and theory tests from a file, pasted text or the chat itself, each with TXT, PDF, JSON and CSV reports.

> **Honest limits.** SpinDoctor is a classical FP64 simulator. It is not a quantum computer, does not connect to quantum hardware,
> and gives no quantum speed-up or advantage. One entangled group is limited to 59 qubits and dense groups are limited by memory
> (2^n x 16 bytes). Registers wider than 29 qubits sample in basis Z only. Histograms are seeded Born samples.

Version 1.1.0 - engine 1.1.0 (SpinDoctor 3.1.2 parity) - Python 3.8+, standard library only - no network, no account, no keys.

## Skill or plugin? (this repo vs. spindoctor-qwerty-grok-build)

| | **This repo: Grok Bot skill** | [spindoctor-qwerty-grok-build](https://github.com/LKVexa/spindoctor-qwerty-grok-build) |
|---|---|---|
| For | Grok Bot and other agents that load Agent Skills folders | The Grok Build coding CLI (`grok`) |
| What you install | One folder, `spindoctor-qwerty/` (or the zip built from it) | A plugin marketplace: `grok plugin marketplace add` + `grok plugin install` |
| How the engine runs | The agent runs `scripts/spindoctor_cli.py` with its shell tool | A local MCP server with 6 tools, plus a skill, 5 slash commands and a subagent |
| Paths | Relative to the skill folder | `${GROK_PLUGIN_ROOT}` |

Same engine, same results and reports; pick the one that matches your host. Using `grok`? Go to the Grok Build repo.

## Install

The skill is the `spindoctor-qwerty/` folder. Give it to your agent host as a skill:

- **Folder:** copy `spindoctor-qwerty/` into the host's skills directory, keeping the folder name (it must match `name:` in SKILL.md).
- **Upload:** `python3 tools/build_skill_zip.py` writes `dist/spindoctor-qwerty-skill-1.1.0.zip` (one top folder, reproducible bytes)
  for hosts that take a skill as a zip.
- **Grok Bot:** add the folder or zip as a skill wherever your Grok Bot setup accepts skills. Packaging a downloadable Grok Bot is
  separate and not part of this repo. Where skills can't be added, you can still give Grok Bot the folder and ask it to follow
  `SKILL.md`: everything it needs is inside.

Requirements on the machine the agent's shell runs on: Python 3.8 or newer (`python3`; `py -3` or `python` on Windows). Nothing to
install; NumPy is used if present.

## What's in the repo

| Path | What it is |
|---|---|
| `spindoctor-qwerty/SKILL.md` | The skill: frontmatter (name, description, license, compatibility, metadata) and instructions |
| `spindoctor-qwerty/scripts/spindoctor_cli.py` | The CLI the agent runs (`functions`, `run`, `script`, `presets`, `preset`, `theory`, `report`, `tool`) |
| `spindoctor-qwerty/scripts/spindoctor_mcp.py` | Optional stdio MCP server with the same 6 tools, for hosts that connect one |
| `spindoctor-qwerty/spindoctor/` | The bundled engine (standard library only) |
| `spindoctor-qwerty/examples/` | `bell_theory_args.json`, sample theory files and chat transcripts |
| `spindoctor-qwerty/LICENSE` | GPL-3.0, so the folder is complete when copied on its own |
| `tools/build_skill_zip.py` | Builds the reproducible upload zip |
| `FUNCTIONS.md` | The full function table with a runnable example for every command |
| `tests/` | Stand-in skill loader, host check, shared end-to-end suite, reference outputs |

## Using it

Ask in plain language: "show the SpinDoctor functions", "run a 3-qubit GHZ circuit with 1000 shots", "run preset qc-061",
"test the theory we discussed". The agent reads SKILL.md and runs the CLI from the skill folder, for example:

```bash
python3 scripts/spindoctor_cli.py functions
python3 scripts/spindoctor_cli.py run "q.circuit new bell 2" "q.circuit add h 0" "q.circuit add cx 0 1" "q.circuit run shots 1000 basis z"
python3 scripts/spindoctor_cli.py theory examples/bell_theory_args.json
```

Reports go to `~/spindoctor-workspace` (or `--workspace DIR`, or `$SPINDOCTOR_WORKSPACE`); every command prints the TXT, JSON, PDF
(and CSV) paths. In Grok Bot the commands run on its box, uploads are passed by their saved path, and the agent can send you the PDF.

| Function | What it does | Ask | CLI |
|---|---|---|---|
| Function table | Show every command family with runnable examples | "show the SpinDoctor functions" | `functions` (`functions presets`, `functions commands noise`) |
| Run a script | Run q.* lines; results + TXT/JSON/CSV/PDF report paths | "run q.circuit new bell 2 / q.circuit add h 0 / ..." | `run "q..." "q..."` or `script FILE` |
| Run a preset | Run qc-001..qc-241 with overrides | "run preset qc-067 with shots=64" | `preset qc-067 shots=64` |
| List presets | Search the 241 presets | "list presets about Grover" | `presets grover` |
| Read a report | List/read TXT reports (PDF/JSON paths alongside) | "show the newest SpinDoctor report" | `report [NAME]` |
| Test a theory | File, pasted text or the chat -> prediction -> q.* script -> verdict + TXT/PDF theory report | "test the theory we discussed" | `theory ARGS.json` |
| One tool call | JSON in, JSON out, for any of the 6 tools | - | `tool spindoctor_run_script < args.json` |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)**: circuits (`q.circuit`, including
298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register (`q.tranche`), the procedural grid, presets and
sequences, resource planning, math calculators, physics models, lessons, noise, error correction, compilation, algorithms,
inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

The `theory` command (tool `spindoctor_test_theory`) turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. Give the file's path; in Grok Bot, files you put in the chat are saved on the box and the agent passes that path.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The skill cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.


## Testing

| Test | Command |
|---|---|
| Stand-in loader (catalog) | `python3 tests/skill_loader.py .` |
| Run every documented command | `python3 tests/skill_loader.py . --run spindoctor-qwerty` |
| Full host check | `python3 tests/skill_host_check.py` (add `--skills-ref "$(command -v agentskills)"` after `pip install skills-ref`) |
| End-to-end suite only | `python3 tests/e2e_mcp.py --server python3 spindoctor-qwerty/scripts/spindoctor_mcp.py --examples spindoctor-qwerty/examples/theory` |

**Stand-in host (limitation).** Skills can't be installed into Grok Bot from outside, so the tests don't run inside Grok Bot. Instead
`tests/skill_loader.py` does what a skills-capable host does, following the Agent Skills format: discover the folder, validate the
frontmatter against the spec's rules, build the `<available_skills>` catalog, activate the skill and check the bundled files it
mentions, and run its documented commands from the skill folder the way an agent's shell tool would. The reference validator
(`skills-ref` 0.1.1) checks the folder as well. Not tested: Grok Bot itself (how it ranks and picks skills, its approval prompts, its
upload and file-sending tools), a real model following the instructions, Windows, macOS. Results: [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). Grok is a trademark of xAI; this project is not affiliated with xAI.
