#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty skill for Grok Bot: host check (stand-in skill loader)
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Check the skill the way a skills-capable agent host would use it, with the stand-in loader in tests/skill_loader.py.

  python tests/skill_host_check.py [--skills-ref PATH_TO_agentskills] [--out tests/host_check.json]

Static checks (licence headers, version, guardrail, frontmatter), then: discover + validate + catalog + activate with the
stand-in loader, run every documented command from the skill folder, run it again from another folder by full path, test a
theory from the chat through the JSON tool bridge, build the upload zip twice (same bytes), load the skill from the
extracted zip in a read-only folder, and run tests/e2e_mcp.py against the bundled MCP server. If the reference validator
`agentskills` (pip install skills-ref) is given or on PATH, it validates the folder too; otherwise that check is skipped.
Grok Bot itself is not involved: skills cannot be installed into it from outside. Standard library only.
"""
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); SKILL = os.path.join(ROOT, "spindoctor-qwerty")
sys.path.insert(0, HERE)
import skill_loader as L  # noqa: E402

res = []


def T(name, ok, detail=""):
    res.append({"check": name, "pass": None if ok is None else bool(ok), "detail": str(detail)[:400]})
    print(("SKIP " if ok is None else "PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + str(detail)[:300])); sys.stdout.flush()


def pdfs(o, acc):
    if isinstance(o, dict): [pdfs(v, acc) for v in o.values()]
    elif isinstance(o, list): [pdfs(v, acc) for v in o]
    elif isinstance(o, str) and o.endswith(".pdf"): acc.append(o)
    return acc


def is_pdf(p):
    try: b = open(p, "rb").read()
    except OSError: return False
    return b.startswith(b"%PDF-") and b.rstrip().endswith(b"%%EOF")


def main():
    a = sys.argv[1:]; opt = dict(zip(a[::2], a[1::2]))
    outp = opt.get("--out", os.path.join(HERE, "host_check.json"))
    tmp = tempfile.mkdtemp(prefix="sdq_skill_"); env = dict(os.environ, HOME=os.path.join(tmp, "home"), USERPROFILE=os.path.join(tmp, "home"))
    env.pop("SPINDOCTOR_WORKSPACE", None); os.makedirs(env["HOME"])
    # --- static
    py = [os.path.join(d, f) for d, _, fs in os.walk(ROOT) if "/." not in d and "__pycache__" not in d for f in fs if f.endswith(".py")]
    bad = [p for p in py if "SPDX-License-Identifier: GPL-3.0-or-later" not in open(p, encoding="utf-8").read(2000)]
    T("static: every .py file has a GPL-3.0-or-later SPDX header (%d files)" % len(py), not bad, bad[:3])
    fm, body, errs = L.validate(SKILL)
    T("static: SKILL.md frontmatter valid (name, description, license, compatibility, metadata)", not errs, errs)
    T("static: metadata version 1.1.0, engine SpinDoctor 3.1.2, license GPL-3.0-or-later",
      fm and fm["metadata"].get("version") == "1.1.0" and "3.1.2" in fm["metadata"].get("engine", "") and fm.get("license") == "GPL-3.0-or-later", fm and fm.get("metadata"))
    T("static: guardrail in description and body", fm and "not a quantum computer" in fm["description"] and "not a\nquantum computer" in body and "298" in body)
    lic = open(os.path.join(SKILL, "LICENSE"), encoding="utf-8").read()
    T("static: skill folder carries the GPL-3.0 LICENSE (self-contained when copied alone)", "GNU GENERAL PUBLIC LICENSE" in lic and "Version 3" in lic)
    allt = "".join(open(p, encoding="utf-8", errors="replace").read() for p in [os.path.join(SKILL, "SKILL.md")] + [q for q in py if q.startswith(SKILL + os.sep)])
    T("static: no host-specific plugin variables or personal paths in the skill", not re.search(r"\$\{[A-Z]+_PLUGIN_ROOT\}|[A-Za-z]:[\\/]Users[\\/]|/home/[a-z]|/Users/[a-z]", allt))
    # --- reference validator (optional)
    ref = opt.get("--skills-ref") or shutil.which("agentskills")
    if ref:
        p = subprocess.run([ref, "validate", SKILL], capture_output=True, text=True)
        T("skills-ref: `agentskills validate` accepts the folder", p.returncode == 0 and "Valid skill" in p.stdout, p.stdout + p.stderr)
        p = subprocess.run([ref, "to-prompt", SKILL], capture_output=True, text=True)
        T("skills-ref: `agentskills to-prompt` catalog entry names spindoctor-qwerty", "spindoctor-qwerty" in p.stdout and "<available_skills>" in p.stdout)
    else:
        T("skills-ref: reference validator not installed (pip install skills-ref)", None)
    # --- stand-in loader: discover / catalog / activate
    skills, problems = L.load([ROOT])
    T("loader: discovers exactly one valid skill in the repo (spindoctor-qwerty)", [fm2["name"] for _, fm2 in skills] == ["spindoctor-qwerty"] and not problems, (skills, problems))
    cat = L.catalog(skills)
    T("loader: <available_skills> catalog has name, description and SKILL.md location", "<name>spindoctor-qwerty</name>" in cat and "SKILL.md</location>" in cat)
    refs = L.references(SKILL, body)
    T("loader: every bundled file the body mentions exists (%d)" % len(refs), refs and all(ok for _, ok in refs), [r for r, ok in refs if not ok])
    cmds = L.commands(body)
    T("loader: documented commands found (%d)" % len(cmds), len(cmds) >= 7, cmds)
    # --- run every documented command from the skill folder
    outs = {}
    for c in cmds:
        p = L.run(SKILL, c, env); outs[c] = p
        T("run (skill folder): " + c[len("python3 scripts/spindoctor_cli.py "):][:70], p.returncode == 0, p.stderr.decode("utf-8", "replace")[-300:])
    o = {c.split()[2]: p.stdout.decode("utf-8", "replace") for c, p in outs.items()}
    T("output: function table is Markdown (Function | What it does | Command to type)", "| Function | What it does | Command to type |" in o.get("functions", ""))
    try:
        th = json.loads(o["theory"]); runj = json.loads(o["run"])
        T("output: Bell theory verdict supported; TXT+PDF theory reports valid", th["verdict"] == "supported" and all(map(is_pdf, pdfs(th, []))) and any(x.endswith(".txt") and os.path.isfile(x) for x in th["reports"]), th.get("verdict"))
        rp = pdfs(runj, [])
        T("output: Bell run ok; reports under ~/spindoctor-workspace; PDF valid", runj["ok"] and rp and all(map(is_pdf, rp)) and all(x.startswith(os.path.join(env["HOME"], "spindoctor-workspace")) for x in rp), rp[:2])
    except (ValueError, KeyError) as e:
        T("output: theory and run JSON parse", False, e)
    # --- agent-sandbox style: other cwd, full path, explicit workspace
    ws = os.path.join(tmp, "ws"); cli = os.path.join(SKILL, "scripts", "spindoctor_cli.py")
    p = subprocess.run([sys.executable, cli, "--workspace", ws, "preset", "qc-001"], cwd=tmp, env=env, capture_output=True)
    T("run (other folder, full path, --workspace): preset qc-001 ok, reports in that workspace", p.returncode == 0 and os.path.isdir(os.path.join(ws, "reports")), p.stderr[-200:])
    # --- theory from the chat via the JSON tool bridge
    args = {"action": "run", "source": "chat", "text": "Claim from our chat: H then measuring gives 0 and 1 about equally often.",
            "excerpts": ["User: if I put a qubit through H and measure, is it 50/50?", "Assistant: yes, about half 0 and half 1."],
            "hypothesis": "H on |0> gives P(0) = P(1) = 0.5", "prediction": "P(1) = 0.5 +/- 0.05 over 2000 shots",
            "script": "q.circuit new hth 1\nq.circuit add h 0\nq.circuit run shots 2000 basis z",
            "checks": [{"kind": "probability", "outcome": "1", "expected": 0.5, "tolerance": 0.05}], "workspace": ws}
    p = subprocess.run([sys.executable, cli, "tool", "spindoctor_test_theory"], input=json.dumps(args).encode(), cwd=tmp, env=env, capture_output=True)
    try:
        j = json.loads(p.stdout); txt = [x for x in j.get("reports", []) if x.endswith(".txt")]
        body_txt = open(txt[0], encoding="utf-8").read() if txt else ""
        T("tool bridge: chat theory supported, excerpts recorded under 'Source: chat history', PDF valid",
          j.get("verdict") == "supported" and j.get("excerptsRecorded") == 2 and "chat history" in body_txt.lower() and all(map(is_pdf, pdfs(j, []))), {k: j.get(k) for k in ("verdict", "excerptsRecorded", "source")})
    except (ValueError, OSError) as e:
        T("tool bridge: chat theory", False, e)
    p = subprocess.run([sys.executable, cli, "tool", "spindoctor_run_script"], input=b'{"script": "q.circuit new w 300"}', cwd=tmp, env=env, capture_output=True)
    T("tool bridge: 300-qubit register refused (1..298, SpinDoctor's own range error)", p.returncode != 0 and b'"ok": false' in p.stdout and b"outside the supported range" in p.stdout, p.stdout[:200])
    # --- upload zip: reproducible, clean, loads read-only
    zb = os.path.join(ROOT, "tools", "build_skill_zip.py"); z1, z2 = os.path.join(tmp, "a.zip"), os.path.join(tmp, "b.zip")
    h = [subprocess.run([sys.executable, zb, z], capture_output=True, text=True).stdout.split()[0] for z in (z1, z2)]
    names = zipfile.ZipFile(z1).namelist()
    T("zip: build is reproducible (same SHA-256 twice): " + h[0][:16], h[0] == h[1] == hashlib.sha256(open(z1, "rb").read()).hexdigest())
    T("zip: one top folder spindoctor-qwerty/ with SKILL.md; no caches or generated PDFs (%d files)" % len(names),
      "spindoctor-qwerty/SKILL.md" in names and all(n.startswith("spindoctor-qwerty/") for n in names) and not any("__pycache__" in n or n.endswith(".pyc") for n in names))
    up = os.path.join(tmp, "uploaded-skills"); zipfile.ZipFile(z1).extractall(up)
    for d, ds, fs in os.walk(up):
        for x in fs + ds: os.chmod(os.path.join(d, x), stat.S_IMODE(os.stat(os.path.join(d, x)).st_mode) & ~0o222)
    os.chmod(up, 0o555)
    sk2, pr2 = L.load([up]); d2 = sk2[0][0] if sk2 else up
    p = L.run(d2, "python3 scripts/spindoctor_cli.py --workspace %s theory examples/bell_theory_args.json" % os.path.join(tmp, "ws2"), env)
    T("zip: extracted read-only copy loads and runs the theory example (no writes into the skill)", sk2 and not pr2 and p.returncode == 0 and b'"supported"' in p.stdout, p.stderr[-200:])
    for d, ds, fs in os.walk(up):
        os.chmod(d, 0o755)
    # --- optional MCP route
    p = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", sys.executable, os.path.join(SKILL, "scripts", "spindoctor_mcp.py"),
                        "--examples", os.path.join(SKILL, "examples", "theory"), "--out", os.path.join(HERE, "e2e_results.json")], env=env, capture_output=True, text=True)
    last = [ln for ln in p.stdout.splitlines() if ln.strip()][-1:] or [""]
    T("mcp: tests/e2e_mcp.py against the bundled MCP server: " + last[0][:80], p.returncode == 0, p.stdout[-400:])
    shutil.rmtree(tmp, ignore_errors=True)
    n = sum(1 for r in res if r["pass"]); f = sum(1 for r in res if r["pass"] is False); s = sum(1 for r in res if r["pass"] is None)
    json.dump({"python": sys.version.split()[0], "checks": res, "passed": n, "failed": f, "skipped": s}, open(outp, "w"), indent=1)
    print("%d passed, %d failed, %d skipped" % (n, f, s))
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
