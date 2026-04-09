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
# ORDER + DISPLAY CLEANING
# ----------------------

def parse_order(name):
    """
    Extracts numeric ordering prefix:
    1. Intro
    01 - Intro
    10.Intro
    """
    match = re.match(r'^(\d+)[\.\-\s]+(.+)$', name)
    if match:
        return int(match.group(1)), match.group(2)
    return 9999, name


def clean_display(name):
    """
    REMOVE ONLY ordering prefix, preserve ORIGINAL CASE
    """
    _, title = parse_order(Path(name).stem)
    return title.replace("-", " ").strip()


def clean_folder(name):
    """
    Folder display cleanup (same logic as files)
    """
    _, title = parse_order(name)
    return title.replace("-", " ").strip()


# ----------------------
# SLUGIFY (SAFE FILE SYSTEM NAMES ONLY)
# ----------------------

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:MAX_NAME].strip("-") or "note"


# ----------------------
# BUILD FILE MAP
# ----------------------

def build_map(src):
    mapping = {}
    used = set()

    for f in src.rglob("*"):
        if not f.is_file():
            continue

        rel = f.relative_to(src)

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
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir()

    (docs / "index.md").write_text("# Home\n\nVault Wiki")

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


# ----------------------
# CREATE FOLDER INDEXES
# ----------------------

def create_indexes(docs):
    for root, _, _ in os.walk(docs):
        root = Path(root)

        if root == docs:
            continue

        if any(part in IGNORE_DIRS for part in root.parts):
            continue

        index = root / "index.md"

        if not index.exists():
            name = clean_folder(root.name)

            index.write_text(f"""---
title: {name}
---

# {name}

Section: {name}
""")


# ----------------------
# NAV BUILDER (ORDERED + CLEAN UI)
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        def sort_key(p):
            order, _ = parse_order(p.stem)
            return order, p.name.lower()

        for p in sorted(folder.iterdir(), key=sort_key):

            if any(part in IGNORE_DIRS for part in p.parts):
                continue

            # folders
            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({
                        clean_folder(p.name): walk(p)
                    })

            # markdown files
            elif p.suffix == ".md" and p.name != "index.md":
                title = clean_display(p.name)
                rel = p.relative_to(docs).as_posix()
                items.append({title: rel})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG (MODERN DARK UI)
# ----------------------

def write_mkdocs(docs):
    import yaml

    nav = build_nav(docs)

    config = {
        "site_name": "Vault Wiki",
        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.expand",
                "navigation.sections",
                "navigation.indexes",
                "search.suggest",
                "search.highlight",
                "content.code.copy"
            ],
            "palette": [
                {
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "blue"
                }
            ],
            "font": {
                "text": "Inter",
                "code": "JetBrains Mono"
            }
        },
        "markdown_extensions": [
            "toc",
            "tables",
            "fenced_code",
            "admonition"
        ],
        "extra_css": ["stylesheets/extra.css"],
        "docs_dir": "docs",
        "nav": [
            {"Home": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "sync wiki"], check=False)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["mkdocs", "gh-deploy"], check=True)


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
    deploy()

    print("✅ Vault Wiki updated")


if __name__ == "__main__":
    main()