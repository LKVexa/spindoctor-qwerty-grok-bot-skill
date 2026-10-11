#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty skill for Grok Bot: stand-in Agent Skills loader (test harness)
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""A small stand-in for an agent host's skill loader, following the Agent Skills format (agentskills.io).

Skills cannot be installed into Grok Bot from outside, so this script does what a skills-capable host does, step by step:
  1. discover: every folder under the search roots that holds a SKILL.md;
  2. parse + validate the YAML frontmatter (name, description, license, compatibility, metadata, allowed-tools) against the
     spec's rules (name 1-64 chars of a-z 0-9 and single hyphens, equal to the folder name; description 1-1024 chars;
     compatibility <= 500 chars; metadata is a string-to-string map; no unknown keys);
  3. build the <available_skills> catalog an agent sees before it picks a skill (name, description, location);
  4. activate: load the SKILL.md body and check that every bundled file it mentions (scripts/..., examples/...) exists;
  5. run: execute the skill's documented shell commands from the skill folder, as an agent's shell tool would.

  python tests/skill_loader.py ROOT [ROOT...]            # discover, validate, print the catalog
  python tests/skill_loader.py ROOT --activate NAME      # print the body an agent would read
  python tests/skill_loader.py ROOT --run NAME           # run every command in the SKILL.md bash blocks

It is a test harness, not Grok Bot: it proves the folder follows the format and its instructions work as written; how a
particular host ranks or chooses skills is up to that host. Standard library only (Python 3.8+).
"""
import json, os, re, shlex, subprocess, sys
from xml.sax.saxutils import escape

ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1].replace('\\"', '"') if v[0] == '"' else v[1:-1].replace("''", "'")
    return v


def parse(path):
    """Return (frontmatter dict, body) for a SKILL.md. Supports the YAML subset skills use: scalars and one nested map."""
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with a '---' frontmatter line")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter is not closed by a '---' line")
    fm, cur = {}, None
    for ln in text[4:end].split("\n"):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if not m:
            raise ValueError("cannot parse frontmatter line: %r" % ln)
        ind, k, v = m.groups()
        if ind:
            if cur is None:
                raise ValueError("indented line outside a map: %r" % ln)
            fm[cur][k] = _scalar(v)
        elif v.strip() == "":
            fm[k] = {}; cur = k
        else:
            fm[k] = _scalar(v); cur = None
    return fm, text[end + 5:]


def validate(skill_dir):
    errs = []
    try:
        fm, body = parse(os.path.join(skill_dir, "SKILL.md"))
    except (OSError, ValueError) as e:
        return None, None, [str(e)]
    unknown = set(fm) - ALLOWED
    if unknown: errs.append("unknown frontmatter keys: %s" % ", ".join(sorted(unknown)))
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not (1 <= len(name) <= 64) or not NAME_RE.match(name):
        errs.append("name must be 1-64 chars of a-z, 0-9 and single hyphens: %r" % (name,))
    elif name != os.path.basename(os.path.normpath(skill_dir)):
        errs.append("name %r must equal the folder name %r" % (name, os.path.basename(os.path.normpath(skill_dir))))
    if not isinstance(desc, str) or not (1 <= len(desc) <= 1024):
        errs.append("description must be 1-1024 characters (got %s)" % (len(desc) if isinstance(desc, str) else type(desc).__name__))
    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or len(comp) > 500): errs.append("compatibility must be <= 500 characters")
    md = fm.get("metadata")
    if md is not None and (not isinstance(md, dict) or not all(isinstance(v, str) for v in md.values())):
        errs.append("metadata must map strings to strings")
    return fm, body, errs


def discover(roots):
    found = []
    for root in roots:
        for d, dirs, fs in os.walk(root):
            dirs[:] = sorted(x for x in dirs if not x.startswith(".") and x not in ("__pycache__", "node_modules"))
            if "SKILL.md" in fs:
                found.append(os.path.abspath(d)); dirs[:] = []  # a skill's own subfolders are resources, not skills
    return found


def catalog(skills):
    out = ["<available_skills>"]
    for d, fm in skills:
        out += ["<skill>", "<name>%s</name>" % escape(fm["name"]), "<description>%s</description>" % escape(fm["description"]),
                "<location>%s</location>" % escape(os.path.join(d, "SKILL.md")), "</skill>"]
    return "\n".join(out + ["</available_skills>"])


def references(skill_dir, body):
    """Relative paths the body mentions under the skill's own resource folders, and whether each exists."""
    refs = sorted(set(re.findall(r"(?<![\w/.$}-])((?:scripts|examples|references|assets)/[\w./-]*\w)", body)))
    return [(r, os.path.exists(os.path.join(skill_dir, r))) for r in refs]


def commands(body):
    cmds = []
    for block in re.findall(r"```(?:bash|sh|shell)\n(.*?)```", body, re.S):
        for ln in block.splitlines():
            ln = ln.split("  #")[0].strip()
            if ln and not ln.startswith("#"): cmds.append(ln)
    return cmds


def run(skill_dir, cmd, env=None, timeout=300):
    """Run one documented command from the skill folder; `python3`/`python` map to this interpreter."""
    argv = shlex.split(cmd)
    if argv and argv[0] in ("python3", "python"): argv[0] = sys.executable
    return subprocess.run(argv, cwd=skill_dir, env=env, capture_output=True, timeout=timeout)


def load(roots):
    skills, problems = [], {}
    for d in discover(roots):
        fm, body, errs = validate(d)
        if errs: problems[d] = errs
        else: skills.append((d, fm))
    return skills, problems


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); return 2
    act = a.index("--activate") if "--activate" in a else a.index("--run") if "--run" in a else None
    roots = a[:act] if act is not None else a
    skills, problems = load(roots)
    for d, errs in problems.items(): print("INVALID %s: %s" % (d, "; ".join(errs)))
    if act is None:
        print(catalog(skills)); return 1 if problems else 0
    want = a[act + 1]; hit = [(d, fm) for d, fm in skills if fm["name"] == want]
    if not hit: print("no valid skill named", want); return 1
    d = hit[0][0]; fm, body, _ = validate(d)
    if a[act] == "--activate":
        print(body)
        for r, ok in references(d, body): print(("ok      " if ok else "MISSING ") + r)
        return 0
    bad = 0
    for c in commands(body):
        p = run(d, c); bad += p.returncode != 0
        print(json.dumps({"command": c, "exit": p.returncode, "stdout_head": p.stdout.decode("utf-8", "replace")[:160]}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
