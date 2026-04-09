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


# ----------------------
# DISPLAY CLEANING
# ----------------------

def clean_display(name):
    _, title = parse_order(Path(name).stem)
    return title.replace("-", " ").strip()


def clean_folder(name):
    _, title = parse_order(name)
    return title.replace("-", " ").strip()


# ----------------------
# FILE SYSTEM SAFE SLUG (PROPER CASE PRESERVED)
# ----------------------

def slugify(text):
    """
    Creates filesystem-safe names BUT keeps Proper Case instead of forcing lowercase.
    Example: "hello world" -> "Hello-World"
    """
    text = text.strip()

    # remove invalid characters
    text = re.sub(r'[^\w\s-]', '', text)

    # replace separators with spaces
    text = re.sub(r'[\s_-]+', ' ', text)

    # Proper Case each word
    text = text.title()

    # convert spaces to hyphens
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
# NAV BUILDER
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
                    items.append({
                        clean_folder(p.name): walk(p)
                    })

            elif p.suffix == ".md" and p.name != "index.md":
                items.append({
                    clean_display(p.name): p.relative_to(docs).as_posix()
                })

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
                    "scheme": "default",
                    "primary": "blue",
                    "accent": "indigo"
                }
            ],
            "font": {
                "text": "Segoe UI",
                "code": "Consolas"
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
# CSS (MICROSOFT FLUENT STYLE)
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
/* ================================
   MICROSOFT FLUENT STYLE THEME
   ================================ */

:root {
    --ms-blue: #0078D4;
    --ms-blue-light: #2B88D8;
    --ms-red: #D83B01;
    --ms-green: #107C10;
    --ms-yellow: #FFB900;
}

/* Base */
body {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    font-family: "Segoe UI", system-ui, sans-serif;
}

/* Header */
.md-header {
    background: var(--ms-blue) !important;
    color: white !important;
    border-bottom: 3px solid var(--ms-blue-light);
}

/* Sidebar */
.md-nav {
    background: #f3f3f3;
    border-right: 1px solid #e1e1e1;
}

/* Links */
a {
    color: var(--ms-blue);
}

a:hover {
    color: var(--ms-blue-light);
}

/* Code blocks */
pre, code {
    background: #f4f4f4 !important;
    border-radius: 6px;
}

/* Content area */
.md-content {
    border-left: 4px solid var(--ms-blue);
    padding-left: 20px;
}

/* Buttons / accents */
.md-button {
    background: var(--ms-blue);
    color: white;
}
""")


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
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ Vault Wiki rebuilt (Microsoft Fluent theme + Proper Case filenames)")


if __name__ == "__main__":
    main()