#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path
import yaml

# ----------------------
# CONFIG
# ----------------------

IGNORE_DIRS = {"resources", "_resources", ".obsidian", ".trash"}
MAX_NAME = 120


# ----------------------
# TITLE CLEANING
# ----------------------

def parse_order(name):
    match = re.match(r'^(\d+)[\.\-\s]+(.+)$', name)
    if match:
        return int(match.group(1)), match.group(2)
    return 9999, name


def clean_title(name):
    _, title = parse_order(Path(name).stem if "." in name else name)
    return title.replace("-", " ").strip()


# ----------------------
# SLUGIFY
# ----------------------

def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', ' ', text)
    text = text.title()
    text = text.replace(" ", "-")
    return text[:MAX_NAME].strip("-") or "Note"


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
# FIX CONTENT (IMAGES ONLY)
# ----------------------

def fix_content(content):
    content = re.sub(
        r'!\[([^\]]*)\]\(:/([a-zA-Z0-9]+)\)',
        r'![\1](resources/\2)',
        content
    )
    return content


# ----------------------
# RESOURCES COPY
# ----------------------

def copy_resources(src, docs):
    for res in src.rglob("_resources"):
        if not res.is_dir():
            continue

        rel_parent = res.parent.relative_to(src)
        dst = docs / rel_parent / "resources"

        dst.mkdir(parents=True, exist_ok=True)

        for file in res.iterdir():
            if file.is_file():
                shutil.copy2(file, dst / file.name)


# ----------------------
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):

    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    copy_resources(src, docs)

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# SAMPLE PAGE (ONLY ONE SOURCE)
# ----------------------

def create_sample_page(docs):
    (docs / "sample-page.md").write_text("""# Sample Page

## What this is
This page demonstrates correct structure.

## Headings (TOC TEST)
### Level 3 Heading
#### Level 4 Heading

MkDocs TOC is automatically generated from headings.

## Example Content
- notes
- images
- code
""", encoding="utf-8")


# ----------------------
# HOME PAGE
# ----------------------

def create_home_page(docs):
    (docs / "index.md").write_text("""# Vault Wiki

Welcome.

## Start Here
- [Sample Page](sample-page.md)

## Navigation
Use sidebar.
""", encoding="utf-8")


# ----------------------
# NAV BUILDER (FIXED, NO DUPLICATES)
# ----------------------

def build_nav(docs):

    nav = [
        {"Home": "index.md"},
        {"Sample Page": "sample-page.md"},
    ]

    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):

            if any(part in IGNORE_DIRS for part in p.parts):
                continue

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({clean_title(p.name): walk(p)})

            elif p.suffix == ".md":
                if p.name in {"index.md", "sample-page.md"}:
                    continue
                items.append({clean_title(p.name): p.relative_to(docs).as_posix()})

        return items

    nav.extend(walk(docs))
    return nav


# ----------------------
# MKDOCS CONFIG
# ----------------------

def write_mkdocs(docs):

    config = {
        "site_name": "Vault Wiki",
        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.sections",
                "navigation.path",
                "navigation.top",
                "navigation.indexes",
                "toc.follow"
            ]
        },
        "markdown_extensions": [
            "tables",
            "fenced_code",
            {"toc": {"permalink": True}}
        ],
        "extra_css": ["stylesheets/extra.css"],
        "nav": build_nav(docs)
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
.md-typeset h1 { font-weight: 800; }
.md-typeset h2 { font-weight: 700; }
""", encoding="utf-8")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix nav duplication + restore TOC stability"], check=False)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["mkdocs", "gh-deploy", "--force"], check=True)


# ----------------------
# MAIN
# ----------------------

def main():

    import sys

    src = Path(sys.argv[1]).resolve()
    docs = Path("docs")

    mapping = build_map(src)

    write_docs(src, docs, mapping)
    create_sample_page(docs)
    create_home_page(docs)
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ FULL FIX COMPLETE (no duplicates, TOC stable, nav fixed)")


if __name__ == "__main__":
    main()