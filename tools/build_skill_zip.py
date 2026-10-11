#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty skill for Grok Bot: build the upload zip
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Pack the skill folder into one zip for hosts that take a skill as an upload.

  python tools/build_skill_zip.py            # writes dist/spindoctor-qwerty-skill-1.1.0.zip and prints its SHA-256

The zip holds a single top-level folder, spindoctor-qwerty/, with SKILL.md at its root (the Agent Skills layout). The build
is reproducible: files are sorted, timestamps fixed and caches/generated PDFs left out, so the same sources always give the
same bytes and the same SHA-256. Standard library only.
"""
import hashlib, os, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "spindoctor-qwerty")
SKIP_DIRS = {"__pycache__"}
STAMP = (2026, 10, 10, 0, 0, 0)


def files():
    out = []
    for d, dirs, fs in os.walk(SKILL):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        rel = os.path.relpath(d, SKILL)
        for f in fs:
            if f.endswith(".pyc") or (f.endswith(".pdf") and rel.replace("\\", "/") == "examples/theory"):
                continue  # caches and PDFs the theory examples generate are not part of the skill
            out.append(os.path.join(d, f))
    return sorted(out, key=lambda p: os.path.relpath(p, SKILL).replace("\\", "/"))


def build(dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files():
            name = "spindoctor-qwerty/" + os.path.relpath(p, SKILL).replace("\\", "/")
            zi = zipfile.ZipInfo(name, STAMP); zi.compress_type = zipfile.ZIP_DEFLATED; zi.create_system = 3
            zi.external_attr = ((0o755 if name.endswith(".py") and "/scripts/" in name else 0o644) | 0o100000) << 16
            with open(p, "rb") as fh: z.writestr(zi, fh.read())
    return hashlib.sha256(open(dest, "rb").read()).hexdigest()


def main():
    if not os.path.isfile(os.path.join(SKILL, "SKILL.md")):
        print("SKILL.md not found in", SKILL); return 1
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "spindoctor-qwerty-skill-1.1.0.zip")
    h = build(dest)
    print("%s  %s  (%d files)" % (h, os.path.relpath(dest, ROOT) if dest.startswith(ROOT) else dest, len(files())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
