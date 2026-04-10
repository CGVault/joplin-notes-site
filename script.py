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

CF_TOKEN = os.getenv("CF_TOKEN", "")


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
# WRITE DOCS (CLEANED)
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # 🏠 REAL HOMEPAGE (NO DUMMY FOLDER LINKS)
    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

---

## 📌 Start Here

These are example entry points into your system:

- [🧠 Notes Overview](notes-overview/)
- [📁 Folder Structure Guide](folder-guide/)
- [⚙️ System Information](system-info/)

---

## 🚀 What this is

This site is automatically generated from your Joplin vault.

Each folder becomes a section with its own landing page.

---

## 📊 Status

- Auto navigation enabled
- MkDocs Material theme
- Cloudflare analytics ready
""")

    # 🧪 REAL SAMPLE PAGES (USED BY HOMEPAGE LINKS)

    (docs / "notes-overview.md").write_text("""
# Notes Overview

This page shows how your notes are structured.

---

## What you'll find here

- Automatically imported notes from Joplin
- Organized by folders
- Clean navigation hierarchy

---

## Tip

Use the sidebar to browse all notes.
""")

    (docs / "folder-guide.md").write_text("""
# Folder Structure Guide

Your vault is organized into folders.

---

## How it works

- Each folder becomes a section
- Each section has a landing page
- Subfolders are nested automatically

---

## Navigation

Use breadcrumbs and sidebar to move around easily.
""")

    (docs / "system-info.md").write_text("""
# System Information

This wiki system is automatically generated.

---

## Stack

- MkDocs Material
- Python generator script
- GitHub Pages deployment

---

## Features

- Auto navigation
- Folder indexing
- Cloudflare analytics integration
""")

    # COPY REAL VAULT FILES
    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


# ----------------------
# ENSURE FOLDER LANDING PAGES
# ----------------------

def ensure_folder_indexes(docs):
    for root, _, _ in os.walk(docs):
        root = Path(root)

        if root == docs:
            continue

        if any(part in IGNORE_DIRS for part in root.parts):
            continue

        index = root / "index.md"

        if not index.exists():
            name = clean_folder(root.name)

            index.write_text(f"""
---
title: {name}
---

# {name}

This is the landing page for **{name}**.

---

## 📂 Contents

This section contains notes and sub-sections.

---

## 🧭 Navigation

Use the sidebar to explore this area.
""")


# ----------------------
# BUILD NAV
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
                "navigation.path",
                "navigation.top",
                "navigation.indexes",
                "search.suggest",
                "search.highlight",
                "content.code.copy"
            ],
            "palette": [
                {"scheme": "default", "primary": "blue", "accent": "indigo"}
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
        "extra_javascript": ["js/analytics.js"],

        "nav": [
            {"🏠 Home Dashboard": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS (UNCHANGED)
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
body {
    background: #ffffff;
    font-family: "Segoe UI", system-ui, sans-serif;
    color: #1a1a1a;
}

.md-header {
    background: #0078D4 !important;
}

.md-nav {
    background: #f5f5f5;
    border-right: 1px solid #e1e1e1;
}

.md-nav__item--active > .md-nav__link {
    font-weight: 700;
    color: #0078D4;
}

a {
    color: #0078D4;
}

.md-content {
    padding: 24px 32px;
    max-width: 900px;
    margin: auto;
}

h1 {
    font-size: 2.6rem;
    font-weight: 900;
    border-bottom: 4px solid #0078D4;
}

h2 {
    font-size: 1.9rem;
    font-weight: 800;
}

h3 {
    font-size: 1.4rem;
    font-weight: 800;
}
""")


# ----------------------
# ANALYTICS
# ----------------------

def write_analytics(docs):
    js_dir = docs / "js"
    js_dir.mkdir(parents=True, exist_ok=True)

    if not CF_TOKEN:
        print("⚠️ CF_TOKEN not set — analytics disabled")
        return

    (js_dir / "analytics.js").write_text(f"""
(function() {{
    var script = document.createElement('script');
    script.defer = true;
    script.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    script.setAttribute('data-cf-beacon', '{{"token": "{CF_TOKEN}"}}');
    document.head.appendChild(script);
}})();
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "vault cleanup: real homepage + structure"], check=False)
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
    write_analytics(docs)
    write_mkdocs(docs)
    deploy()

    print("✅ Clean homepage + real sample pages + no dummy folders")


if __name__ == "__main__":
    main()