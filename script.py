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

CF_TOKEN = os.getenv("CF_TOKEN", "")


# ----------------------
# SLUGIFY
# ----------------------

def slugify(text):
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', ' ', text)
    text = text.title().replace(" ", "-")
    return text[:MAX_NAME].strip("-") or "Note"


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

        new_name = slugify(f.stem) + f.suffix.lower()
        new_path = Path(*[slugify(p) for p in rel.parts[:-1]]) / new_name

        mapping[str(rel)] = str(new_path)

    return mapping


# ----------------------
# FIX JOPLIN CONTENT
# ----------------------

def fix_content(content):
    lines = content.splitlines()

    fixed = []
    first_h1 = False

    for line in lines:
        # Fix headings
        if line.startswith("#"):
            if not first_h1:
                fixed.append(line)  # keep first H1
                first_h1 = True
            else:
                # downgrade all other H1 → H2
                fixed.append(re.sub(r'^# ', '## ', line))
            continue

        fixed.append(line)

    content = "\n".join(fixed)

    # Fix Joplin image links :/abc123 → resources/abc123.*
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

    # Copy resources folder directly
    resources_src = src / "resources"
    if resources_src.exists():
        shutil.copytree(resources_src, docs / "resources")

    # HOMEPAGE
    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

Use the sidebar to explore your notes.

## Example
- [Sample Page](sample-page/)
""")

    # SAMPLE PAGE
    (docs / "sample-page.md").write_text("""
# Sample Page

## Section One
Example content.

## Section Two
More content.
""")

    # COPY FILES WITH FIXES
    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# BUILD NAV
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):
            if p.is_dir():
                items.append({p.name: walk(p)})

            elif p.suffix == ".md" and p.name not in {"index.md", "sample-page.md"}:
                items.append({p.stem: p.relative_to(docs).as_posix()})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG
# ----------------------

def write_mkdocs():
    import yaml

    config = {
        "site_name": "Vault Wiki",

        "theme": {
            "name": "material",
            "features": [
                "navigation.sections",
                "navigation.top",
                "toc.follow"
            ]
        },

        "markdown_extensions": [
            {
                "toc": {
                    "permalink": True
                }
            },
            "tables",
            "fenced_code"
        ],

        "extra_css": ["stylesheets/extra.css"],

        "nav": [
            {"Home": "index.md"},
            {"Sample": "sample-page.md"}
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS (FORCE BOLD + CLEAN)
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
h1, .md-typeset h1 {
    font-weight: 800 !important;
}

h2, .md-typeset h2 {
    font-weight: 700 !important;
}

h3, .md-typeset h3 {
    font-weight: 600 !important;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: toc + images + headings"], check=False)
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
    write_css()
    write_mkdocs()
    deploy()

    print("✅ TOC, images, and headings fully fixed")


if __name__ == "__main__":
    main()