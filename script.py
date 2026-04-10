#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

# ----------------------
# CONFIG
# ----------------------

IGNORE_DIRS = {".obsidian", ".trash"}
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
# BUILD FILE MAP (FIXED - NO STRUCTURE BREAKING)
# ----------------------

def build_map(src):
    mapping = {}

    for f in src.rglob("*"):
        if not f.is_file():
            continue

        rel = f.relative_to(src)

        if any(part in IGNORE_DIRS for part in rel.parts):
            continue

        # ONLY rename file, preserve folder structure EXACTLY
        new_name = slugify(f.stem) + f.suffix.lower()
        new_rel = rel.with_name(new_name)

        mapping[rel] = new_rel

    return mapping


# ----------------------
# CONTENT FIX (IMAGES + HEADINGS)
# ----------------------

def fix_content(content):
    lines = content.splitlines()
    fixed = []

    for line in lines:

        # ----------------------
        # HEADINGS (TOC FIX)
        # ----------------------
        if line.startswith("#"):
            fixed.append(re.sub(r'^#', '##', line))
            continue

        # ----------------------
        # IMAGE FIX (JOPLIN _resources)
        # ----------------------

        line = line.replace("../../../_resources/", "resources/")
        line = line.replace("../../_resources/", "resources/")
        line = line.replace("../_resources/", "resources/")
        line = line.replace("_resources/", "resources/")

        fixed.append(line)

    return "\n".join(fixed)


# ----------------------
# WRITE DOCS (FIXED PATH HANDLING)
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # ----------------------
    # COPY RESOURCES
    # ----------------------

    resources_src = src / "resources"
    resources_dst = docs / "resources"

    if resources_src.exists():
        if resources_dst.exists():
            shutil.rmtree(resources_dst)
        shutil.copytree(resources_src, resources_dst)

    # ----------------------
    # HOME PAGE
    # ----------------------

    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

---

## 🚀 Start Here

- [🧪 Open Sample Page](sample-page.md)

---

## 📊 Overview

- Auto-generated from Joplin
- Structured wiki navigation
""")

    # ----------------------
    # SAMPLE PAGE
    # ----------------------

    (docs / "sample-page.md").write_text("""
# Sample Page

## Section One
Example content.

## Section Two
TOC works here.

## Section Three
Use this page for testing.
""")

    # ----------------------
    # PROCESS FILES (FIXED PATH LOGIC)
    # ----------------------

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new   # ✅ FIXED (NO STRING CONVERSION BUG)

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# FOLDER INDEX PAGES
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
            if any(part in IGNORE_DIRS for part in item.parts):
                continue

            if item.is_dir():
                if (item / "index.md").exists():
                    subfolders.append(item)

            elif item.suffix == ".md" and item.name != "index.md":
                notes.append(item)

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

        (root / "index.md").write_text(content)


# ----------------------
# NAV TREE
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

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({clean_folder(p.name): walk(p)})

            elif p.suffix == ".md" and p.name not in {"index.md", "sample-page.md"}:
                items.append({clean_display(p.name): p.relative_to(docs).as_posix()})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG
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
                "navigation.sections",
                "navigation.path",
                "navigation.top",
                "navigation.indexes",
                "toc.follow"
            ]
        },

        "markdown_extensions": [
            {"toc": {"permalink": True}},
            "tables",
            "fenced_code"
        ],

        "extra_css": ["stylesheets/extra.css"],

        "nav": [
            {"🏠 Home": "index.md"},
            {"🧪 Sample Page": "sample-page.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS (MICROSOFT STYLE)
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
.md-typeset h1 {
    font-weight: 900;
    font-size: 2.4rem;
}

.md-typeset h2 {
    font-weight: 800;
    font-size: 2rem;
}

.md-typeset h3 {
    font-weight: 700;
}

.md-typeset h1,
.md-typeset h2,
.md-typeset h3 {
    letter-spacing: -0.02em;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: stable Joplin pipeline (paths + images + nav)"], check=False)
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
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ Fully stable Joplin → MkDocs pipeline rebuilt")


if __name__ == "__main__":
    main()