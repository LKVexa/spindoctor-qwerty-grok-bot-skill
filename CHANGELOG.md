# Changelog

## 1.1.0 - 2026-10-11

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics, CSV report copies and measurement-CSV fitting equations. All 241
  presets replayed. Function table and theory testing (file, pasted text or the chat; TXT+JSON+PDF theory reports). 1.0's SKILL.md
  described SpinDoctor 3.0.3, a 29-qubit cap and TXT/JSON/PDF reports only.
- **Skill folder named after the skill.** The skill now lives in `spindoctor-qwerty/` (folder name = `name:` in the frontmatter, as
  the Agent Skills format requires); 1.0 kept SKILL.md at the root of a folder called `grok_bot_skill`, which strict loaders reject.
- **Frontmatter.** `license` corrected from MIT to GPL-3.0-or-later; `compatibility` added (Python 3.8+, a shell tool, no network);
  `metadata` carries version, engine and author. Validated with the reference validator (`skills-ref`).
- **Instructions written for a skill, not a plugin.** The CLI is the main route (no MCP tools are assumed); every command in SKILL.md
  runs as written from the skill folder using only bundled files (new `examples/bell_theory_args.json` for the `theory` command; 1.0
  used placeholder files, `my_circuit.q` and `theory_args.json`, that are not in the folder). A Grok Bot section covers the box, uploads and sending the
  PDF; the optional MCP server is described for hosts that connect it.
- **Self-contained.** The skill folder carries its own LICENSE. `tools/build_skill_zip.py` builds a reproducible upload zip
  (one top folder, no caches or generated PDFs).
- Tests: `tests/skill_loader.py` (a stand-in Agent Skills loader: discover, validate, catalog, activate, run) and
  `tests/skill_host_check.py` (static checks, every documented command, a chat theory through the JSON tool bridge, the zip loaded
  read-only, and the shared end-to-end suite through the bundled MCP server).
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `SKILL.md` + `scripts/` + `spindoctor/` engine, described as SpinDoctor 3.0.3.
