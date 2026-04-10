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
# ORDER PARSING
# ----------------------

def parse_order(name):
    match = re.match(r'^(\d+)[\.\-\s]+(.+)$', name)
    if match:
        return int(match.group(1)), match.group(2)
    return 9999, name


def clean_display(name):
    _, title = parse_order(Path(name).stem)
    return title.replace("-", " ").strip()


def clean_folder(name):
    _, title = parse_order(name)
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
# BUILD MAP
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
# FIX CONTENT (IMAGES + TOC SAFE HEADINGS)
# ----------------------

def fix_content(content):

    # Fix Joplin image links
    content = re.sub(
        r'!\[([^\]]*)\]\(:/([a-zA-Z0-9]+)\)',
        r'![\1](resources/\2)',
        content
    )

    content = content.replace("_resources/", "resources/")

    # Ensure proper heading spacing for TOC stability
    content = re.sub(r'^(#{1,6})([^ #])', r'\1 \2', content, flags=re.MULTILINE)

    return content


# ----------------------
# RESOURCES COPY (HIDDEN FROM NAV)
# ----------------------

def copy_all_resources(src, docs):
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
# SAMPLE PAGE
# ----------------------

def create_sample_page(docs):
    sample = docs / "sample-page.md"

    sample.write_text("""---
title: Sample Page
---

# Sample Page

This page shows how notes will look in your vault.

## Structure Example

### Headings
Use headings to automatically build the table of contents.

### Example Block

- notes
- ideas
- code
- images

## Why this exists

This is your reference template for all future notes.
""", encoding="utf-8")


# ----------------------
# HOME PAGE
# ----------------------

def create_home_page(docs):

    home = docs / "index.md"

    home.write_text("""---
title: Home
---

# 🧠 Vault Wiki

Welcome to your personal knowledge system.

---

## 🚀 Start Here

- Open the **Sample Page** to learn structure

---

## 📘 Example Page

- 🧪 [Sample Page](sample-page.md)

---

## 📂 Explore

Use the sidebar to browse your notes and folders.

Everything is auto-generated.

---

## ✨ Tips

- Use headings for automatic TOC
- Prefix folders with numbers for ordering
- Images are supported automatically
""", encoding="utf-8")


# ----------------------
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):

    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    copy_all_resources(src, docs)

    for orig, new in mapping.items():

        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# FOLDER INDEXES (EXCLUDE RESOURCES)
# ----------------------

def generate_folder_indexes(docs):

    for root, _, _ in os.walk(docs):
        root = Path(root)

        if root == docs:
            continue

        if any(part in IGNORE_DIRS for part in root.parts):
            continue

        subfolders = []
        notes = []

        for item in sorted(root.iterdir()):

            if item.is_dir():
                if (item / "index.md").exists():
                    subfolders.append(item)

            elif item.suffix == ".md" and item.name != "index.md":
                notes.append(item)

        if not subfolders and not notes:
            continue

        folder_name = clean_folder(root.name)

        content = f"# {folder_name}\n\n"

        if subfolders:
            content += "## Sections\n\n"
            for sf in subfolders:
                name = clean_folder(sf.name)
                rel = sf.relative_to(docs).as_posix()
                content += f"- [{name}]({rel}/)\n"
            content += "\n"

        if notes:
            content += "## Notes\n\n"
            for nf in notes:
                name = clean_display(nf.name)
                rel = nf.relative_to(docs).as_posix()
                content += f"- [{name}]({rel})\n"

        (root / "index.md").write_text(content, encoding="utf-8")


# ----------------------
# NAV TREE (DEDUP + NO RESOURCES + NO DUP SAMPLE)
# ----------------------

def build_nav(docs):

    seen = set()

    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):

            if any(part in IGNORE_DIRS for part in p.parts):
                continue

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({clean_folder(p.name): walk(p)})

            elif p.suffix == ".md" and p.name != "index.md":
                rel = p.relative_to(docs).as_posix()

                if rel in seen:
                    continue

                seen.add(rel)
                items.append({clean_display(p.name): rel})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG
# ----------------------

def write_mkdocs(docs):

    import yaml

    nav = [
        {"🏠 Home": "index.md"},
        {"🧪 Sample Page": "sample-page.md"},
        *build_nav(docs)
    ]

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
            "toc",
            "tables",
            "fenced_code"
        ],
        "extra_css": ["stylesheets/extra.css"],
        "nav": nav
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
.md-typeset h1 { font-weight: 900; }
.md-typeset h2 { font-weight: 900; font-size: 2rem; }
.md-typeset h3 { font-weight: 800; }
""", encoding="utf-8")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix nav duplication + hide resources + restore TOC"], check=False)
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
    generate_folder_indexes(docs)

    create_sample_page(docs)
    create_home_page(docs)

    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ FIX COMPLETE: TOC + NAV + RESOURCES + SAMPLE DUP REMOVED")


if __name__ == "__main__":
    main()