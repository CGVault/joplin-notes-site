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
# CLEAN DISPLAY
# ----------------------

def clean_display(name):
    _, title = parse_order(Path(name).stem)
    return title.replace("-", " ").strip()


def clean_folder(name):
    _, title = parse_order(name)
    return title.replace("-", " ").strip()


# ----------------------
# PROPER CASE SLUG (SAFE FILE NAMES)
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
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    (docs / "index.md").write_text("# Vault Wiki\n\nWelcome")

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


# ----------------------
# CREATE INDEXES
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
                    items.append({clean_folder(p.name): walk(p)})

            elif p.suffix == ".md" and p.name != "index.md":
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
        "site_url": "https://cgvault.github.io/joplin-notes-site/",

        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.sections",
                "navigation.prune",
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

        "nav": [
            {"Home": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# MICROSOFT FLUENT CSS (UPGRADED + FIXED HEADINGS)
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
/* =========================================
   MICROSOFT FLUENT UI (WHITE THEME)
   ========================================= */

:root {
    --ms-blue: #0078D4;
    --ms-bg: #ffffff;
    --ms-sidebar: #f5f5f5;
    --ms-text: #1a1a1a;
    --ms-border: #e1e1e1;
}

/* BASE */
body {
    background: var(--ms-bg) !important;
    color: var(--ms-text);
    font-family: "Segoe UI", system-ui, sans-serif;
    line-height: 1.6;
}

/* HEADER */
.md-header {
    background: var(--ms-blue) !important;
    color: white !important;
}

/* SIDEBAR */
.md-nav {
    background: var(--ms-sidebar);
    border-right: 1px solid var(--ms-border);
}

/* LINKS */
a {
    color: var(--ms-blue);
}

/* CONTENT AREA */
.md-content {
    padding: 24px 32px;
    max-width: 900px;
    margin: auto;
}

/* =========================================
   STRONG HEADING SYSTEM (FIXED VISIBILITY)
   ========================================= */

h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #1a1a1a;
    border-bottom: 3px solid var(--ms-blue);
    padding-bottom: 10px;
    margin-bottom: 16px;
}

h2 {
    font-size: 1.6rem;
    font-weight: 800;
    margin-top: 24px;
    margin-bottom: 10px;
}

h3 {
    font-size: 1.25rem;
    font-weight: 700;
}

/* Force MkDocs override issues */
.md-content h1,
.md-content h2,
.md-content h3 {
    font-weight: 800 !important;
}

/* SIDEBAR EMPHASIS */
.md-nav__link {
    font-weight: 500;
}

.md-nav__link--active {
    font-weight: 700;
    color: var(--ms-blue) !important;
}

/* CODE */
pre {
    background: #f6f6f6 !important;
    border: 1px solid var(--ms-border);
}

code {
    background: #f3f3f3;
    padding: 2px 5px;
    border-radius: 4px;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["mkdocs", "build"], check=True)
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
    create_indexes(docs)
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ Microsoft Fluent MkDocs site deployed successfully")


if __name__ == "__main__":
    main()