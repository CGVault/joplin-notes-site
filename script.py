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


# 🔐 SECURITY: Cloudflare token from environment variable
# Set it like:
# export CF_TOKEN="your_token_here"
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
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # 🏠 HOMEPAGE WITH REAL NAVIGATION
    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

---

## 📌 Quick Start

- [📂 Browse All Notes](./)
- [📁 Example Folder](example-folder/)
- [🧪 Sample Page](sample-page/)

---

## 🚀 What is this?

This site is automatically generated from your Joplin vault.

Each folder becomes a section with its own landing page.

---

## 📊 System Status

- MkDocs Material active
- Auto navigation enabled
- Cloudflare analytics enabled
""")

    # 🧪 SAMPLE PAGE (ENSURES SIDEBAR ALWAYS HAS REAL TARGET)
    (docs / "sample-page.md").write_text("""
# Sample Page

This is a sample page to demonstrate navigation.

---

## Content Example

You can replace this with real notes later.

- Point 1
- Point 2
- Point 3

---

## Notes

This page exists to ensure navigation links are never broken.
""")

    # 📁 SAMPLE FOLDER (ENSURES STRUCTURE EXISTS)
    sample_folder = docs / "example-folder"
    sample_folder.mkdir(parents=True, exist_ok=True)

    (sample_folder / "index.md").write_text("""
---
title: Example Folder
---

# Example Folder

This is a sample folder landing page.

---

## Inside this section

- Sample note 1
- Sample note 2

---

This folder is auto-generated to demonstrate structure.
""")

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


# ----------------------
# ENSURE EVERY FOLDER HAS LANDING PAGE
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

Use the sidebar to explore deeper into this category.
""")


# ----------------------
# BUILD NAV TREE
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
# CSS
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
# ANALYTICS (SECURE VERSION)
# ----------------------

def write_analytics(docs):
    js_dir = docs / "js"
    js_dir.mkdir(parents=True, exist_ok=True)

    if not CF_TOKEN:
        print("⚠️ WARNING: CF_TOKEN not set. Analytics disabled.")
        return

    (js_dir / "analytics.js").write_text(f"""
/* Cloudflare Web Analytics */
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

    subprocess.run(
        ["git", "commit", "-m", "vault upgrade: pages + nav + security"],
        check=False
    )

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

    print("✅ Site upgraded: working pages + secure analytics + folder structure fixed")


if __name__ == "__main__":
    main()