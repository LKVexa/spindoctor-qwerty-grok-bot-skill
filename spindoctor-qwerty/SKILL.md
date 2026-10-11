---
name: spindoctor-qwerty
description: Run the SpinDoctor 3.1.2 quantum-circuit simulator (classical FP64, not a quantum computer) with the bundled Python scripts - build q.* circuits (up to 298 logical qubits), run the 241 presets qc-001..qc-241, process folders with q.folder, test theories from files, pasted text or the chat, and produce TXT/PDF/JSON/CSV reports. Use for quantum-circuit experiments, Bell/GHZ/QFT demos, noise/QEC calculators, "show the SpinDoctor functions" and SpinDoctor reports.
license: GPL-3.0-or-later
compatibility: Needs Python 3.8+ (standard library only; NumPy optional) and a shell tool that can run scripts from this folder. No network, no installs, no API keys.
metadata:
  version: "1.1.0"
  engine: "SpinDoctor 3.1.2 parity (update 3.1.2-298-20261010)"
  author: "RUSSELL PHILIP SMITHSON"
---

# SpinDoctor Qwerty 1.1.0 - q.* quantum-circuit simulator (SpinDoctor 3.1.2 parity)

Use this skill when the user wants to build, run or explain quantum circuits, run a SpinDoctor preset
(qc-001 ... qc-241), run a folder of command files, test a theory, or get a TXT/PDF report of a simulation.

**Honesty rules (always follow):** SpinDoctor is a classical FP64 simulator running on this computer. It is not a
quantum computer and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
group (factor) is limited to 59 qubits and dense factors are limited by memory (2^n x 16 bytes). Registers wider than
29 qubits sample in basis Z only. Histograms come from seeded Born sampling, so counts fluctuate around the exact
probabilities. Never describe results as coming from quantum hardware or as a quantum advantage.

## How to run it

Everything is in this skill folder: `scripts/spindoctor_cli.py` (the CLI), `scripts/spindoctor_mcp.py` (an optional MCP
server), the `spindoctor/` engine and `examples/`. Run the CLI with your shell tool, from this folder or with the full path
to it (`python3` on macOS/Linux and most agent sandboxes; `py -3` or `python` on Windows):

```bash
python3 scripts/spindoctor_cli.py functions
python3 scripts/spindoctor_cli.py run "q.circuit new bell 2" "q.circuit add h 0" "q.circuit add cx 0 1" "q.circuit run shots 1000 basis z"
python3 scripts/spindoctor_cli.py script examples/theory/xbasis.q
python3 scripts/spindoctor_cli.py presets ghz
python3 scripts/spindoctor_cli.py preset qc-061 shots=500
python3 scripts/spindoctor_cli.py theory examples/bell_theory_args.json
python3 scripts/spindoctor_cli.py report
```

- `functions [commands|gates|tools|presets|all] [FILTER]` prints the function table (Markdown); `script FILE` runs one q.*
  command per line (`#` comments allowed); `presets [FILTER]` lists presets; `preset ID [name=value ...]` runs one;
  `theory ARGS.json` tests a theory; `report [NAME]` lists or shows reports.
- `--workspace DIR` (before the action) chooses where state and reports go; default `~/spindoctor-workspace`, or
  `$SPINDOCTOR_WORKSPACE`. Every run writes TXT, JSON, PDF (and CSV where tabular) reports and prints their paths.
- `tool TOOL_NAME < args.json` runs one tool call with JSON in and out (`spindoctor_run_script`, `spindoctor_run_preset`,
  `spindoctor_list_presets`, `spindoctor_report`, `spindoctor_functions`, `spindoctor_test_theory`).
- If your host has connected the bundled MCP server (`python3 scripts/spindoctor_mcp.py`), the same six tools are available
  directly as `spindoctor_*`; prefer them.

## Command grammar (most used)

- `q.circuit new NAME QUBITS` (1..298) - `q.circuit add GATE [angles...] QUBITS|all` - gates include h x y z s sdg t tdg
  sx rx ry rz p u cx cy cz ch swap cp crx cry crz ccx cswap and `mcx7` (controls 0..6 of the operands, target last).
- `q.circuit run shots N basis z|x|y` then `q.circuit result` / `q.circuit status`; `q.query ...` on the last run.
- `q.folder run path="FOLDER"` runs every .txt/.csv/.json/.qasm/.qasm2/.circuit/.pdf file at the top level of a folder
  (1-128 files, 4 MiB each, 1-128 commands per file, 4096 characters per command, strict UTF-8; other files are skipped
  and listed; the first failing file stops the job).
- Calculators `q.math`, `q.resource`, `q.model`, `q.lesson`, `q.noise`, `q.qec`, `q.compile`, `q.algorithm`;
  tranche register `q.tranche`; procedural grid `q.prepare/q.gate/q.measure`; `q.preset list|show|run`; `q.help`.

## Function table (show it in chat)

On first use, and whenever the user asks what SpinDoctor can do, asks for help, "functions", "commands" or a "menu",
run `functions` (or the `spindoctor_functions` tool) and show the Markdown table **verbatim** (Function | What it does |
Command to type). `functions presets` lists the 241 presets; `functions commands noise` narrows the table.

## Testing a theory (file, pasted text, or the chat itself)

1. **Get the theory.** A file (txt, md, pdf, py, json, csv or q.* script): `"source": "file"`, `"path": ...`,
   `"action": "extract"` first. Pasted text: `"source": "text"`. **From the chat history** ("test the theory we
   discussed"): gather the theory from the conversation you can see and write a short summary - claims, assumptions,
   variables, measurable prediction. **Show it to the user and ask them to confirm or correct it before running.** Then
   use `"source": "chat"`, `"text": <confirmed summary>` and `"excerpts": [...]` (short verbatim quotes "User: ...",
   "Assistant: ..."). An exported chat transcript (.txt/.md/.json/.html) can be passed as `path`. This skill cannot read
   the chat by itself, and very long chats may already be cut off by your context window - say so if that may matter.
2. **Restate the hypothesis** and a **measurable prediction**.
3. **Write a q.* script** and machine `checks`, e.g. `{"kind":"probability","outcome":"11","expected":0.5,"tolerance":0.05}`
   (bitstrings put qubit 0 on the RIGHT) or `{"kind":"value","command":5,"path":"result.fidelity","op":"approx","value":1,"tolerance":1e-9}`.
4. **Run**: write the fields to a JSON file and run `theory FILE.json` (or pipe them to `tool spindoctor_test_theory`), with
   `"action": "run"`. `examples/bell_theory_args.json` is a complete example. Each run uses a fresh sub-workspace.
5. **Report**: verdict (supported / not supported / inconclusive), observed vs predicted numbers, and the TXT + PDF theory
   report paths. Repeat the limits: classical simulation of an idealised model, shot noise, qubit limits.

## Files, attachments and reports

- The scripts read local paths only. If the user attached a file and your host saved it to disk (many agent hosts keep
  uploads in a working folder), pass that path; otherwise ask them to paste the text.
- Report paths are printed by every command. If your host can send or attach files, offer the PDF; otherwise give the path
  and summarise the TXT report in chat.
- **In Grok Bot:** run the commands with the shell tool on the box (Linux, `python3`). Files the user puts in the chat are
  saved on the box (in an uploads folder of the workspace); pass that saved path. Reports stay on the box in the default
  workspace (or `--workspace DIR`); share the PDF with the tool that sends files to the user.
- `q.compile synthesize` is not implemented in SpinDoctor 3.1.2 either (it returns an explanatory error).
