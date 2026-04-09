#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

# ----------------------
# CONFIG
# ----------------------

IGNORE_DIRS = {"resources", "_resources", ".obsidian", ".trash"}
MAX_NAME = 120

# ----------------------
# NAME CLEANING
# ----------------------

def clean_display_name(filename):
    name = Path(filename).stem

    # remove numbering ONLY for display
    name = re.sub(r'^\d+[\.\-\)\s]+', '', name)

    name = name.replace("-", " ").strip()
    return name.title()


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:MAX_NAME].strip("-") or "note"

# ----------------------
# FILE MAPPING
# ----------------------

def build_map(src):
    mapping = {}
    used = set()

    for f in src.rglob("*"):
        if not f.is_file():
            continue

        rel = f.relative_to(src)

        # IGNORE unwanted folders
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue

        new_name = slugify(f.stem) + f.suffix.lower()

        new_path = Path(*[slugify(p) for p in rel.parts[:-1]]) / new_name

        base = new_path
        i = 1
        while str(new_path) in used:
            new_path = base.with_name(f"{base.stem}-{i}{base.suffix}")
            i += 1

        used.add(str(new_path))
        mapping[str(rel)] = str(new_path)

    return mapping


# ----------------------
# WRITE FILES
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir()

    (docs / "index.md").write_text("# Home\n\nNotes Wiki")

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


# ----------------------
# CREATE CLEAN FOLDER INDEXES
# ----------------------

def create_indexes(docs):
    for root, dirs, files in os.walk(docs):

        root = Path(root)

        # skip root
        if root == docs:
            continue

        # skip ignored folders
        if any(part in IGNORE_DIRS for part in root.parts):
            continue

        index = root / "index.md"

        if not index.exists():
            name = root.name.replace("-", " ").title()

            index.write_text(f"""---
title: {name}
---

# {name}

Section: {name}
""")


# ----------------------
# BUILD CONTROLLED NAV (FIXED ORDER)
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        # SORT BY FILENAME (THIS FIXES ORDERING)
        for p in sorted(folder.iterdir(), key=lambda x: x.name):

            if any(part in IGNORE_DIRS for part in p.parts):
                continue

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({p.name.replace("-", " ").title(): walk(p)})

            elif p.suffix == ".md" and p.name != "index.md":
                title = clean_display_name(p.name)
                rel = p.relative_to(docs).as_posix()
                items.append({title: rel})

        return items

    return walk(docs)


def write_mkdocs(docs):
    import yaml

    nav = build_nav(docs)

    config = {
        "site_name": "Joplin Notes Wiki",
        "theme": {
            "name": "material"
        },
        "docs_dir": "docs",
        "nav": [
            {"Home": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# GIT
# ----------------------

def git_push():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "sync wiki"], check=False)
    subprocess.run(["git", "push"], check=True)


# ----------------------
# MAIN
# ----------------------

def main():
    import sys

    src = Path(sys.argv[1]).resolve()
    docs = Path("docs")

    mapping = build_map(src)
    write_docs(src, docs, mapping)
    create_indexes(docs)
    write_mkdocs(docs)
    git_push()

    print("✅ Done → mkdocs serve")


if __name__ == "__main__":
    main()