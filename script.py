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
# SLUGIFY
# ----------------------

def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', ' ', text)
    return text.title().replace(" ", "-")[:MAX_NAME]


# ----------------------
# BUILD FILE MAP
# ----------------------

def build_map(src):
    mapping = {}

    for f in src.rglob("*"):
        if not f.is_file():
            continue

        rel = f.relative_to(src)

        if any(part in IGNORE_DIRS for part in rel.parts):
            continue

        new_path = Path(*[slugify(p) for p in rel.parts])

        mapping[str(rel)] = str(new_path)

    return mapping


# ----------------------
# FIX CONTENT
# ----------------------

def fix_content(content):
    lines = content.splitlines()

    fixed = []
    first_h1 = False

    for line in lines:
        if line.startswith("#"):
            if not first_h1:
                fixed.append(line)
                first_h1 = True
            else:
                fixed.append(re.sub(r'^# ', '## ', line))
        else:
            fixed.append(line)

    content = "\n".join(fixed)

    # Fix images
    content = re.sub(
        r'!\[.*?\]\(:/([a-zA-Z0-9]+)\)',
        r'![image](resources/\1.png)',
        content
    )

    return content


# ----------------------
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # Copy resources
    if (src / "resources").exists():
        shutil.copytree(src / "resources", docs / "resources")

    # Homepage
    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

Use the sidebar to explore your notes.
""")

    # Sample page
    (docs / "sample-page.md").write_text("""
# Sample Page

## Section One
Example content.
""")

    # Copy notes
    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# ENSURE FOLDER INDEXES
# ----------------------

def ensure_folder_indexes(docs):
    for root, _, _ in os.walk(docs):
        root = Path(root)

        if root == docs:
            continue

        index = root / "index.md"

        if not index.exists():
            index.write_text(f"# {root.name}\n")


# ----------------------
# BUILD NAV (THIS FIXES YOUR ISSUE)
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):
            if p.name in IGNORE_DIRS:
                continue

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({p.name: walk(p)})

            elif p.suffix == ".md" and p.name not in {"index.md", "sample-page.md"}:
                items.append({p.stem: p.relative_to(docs).as_posix()})

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
                "navigation.sections",
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
            {"🧪 Sample": "sample-page.md"},
            *nav   # ✅ THIS RESTORES YOUR SIDEBAR
        ]
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
.md-typeset h1 {
    font-weight: 800 !important;
}

.md-typeset h2 {
    font-weight: 700 !important;
}

.md-typeset h3 {
    font-weight: 600 !important;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: restore nav + toc + images"], check=False)
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
    ensure_folder_indexes(docs)
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ Navigation restored + TOC working + images fixed")


if __name__ == "__main__":
    main()