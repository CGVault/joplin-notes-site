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
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # HOMEPAGE
    (docs / "index.md").write_text("""
# Vault Wiki

Welcome to your knowledge base.

---

## 📌 Start Here

Use the sidebar to explore your notes.

---

## 🧪 Example

- [Sample Page](sample-page/)

---

## 🚀 About

This site is automatically generated from your Joplin vault.

- Folders become sections
- Notes are organized automatically
- Navigation is fully dynamic
""")

    # SAMPLE PAGE
    (docs / "sample-page.md").write_text("""
# Sample Page

## Section One
Some example content.

## Section Two
More example content.

### Subsection
Even deeper content.
""")

    # COPY + ENSURE HEADINGS (important for TOC)
    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")

        # Ensure file has at least one H1 for TOC to work nicely
        if not re.search(r'^# ', content, re.MULTILINE):
            title = clean_display(Path(new).name)
            content = f"# {title}\n\n" + content

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# ENSURE FOLDER INDEXES
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

## 📂 Contents

Browse notes in this section using the sidebar.
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

            elif p.suffix == ".md" and p.name not in {"index.md", "sample-page.md"}:
                items.append({clean_display(p.name): p.relative_to(docs).as_posix()})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG (TOC ENABLED)
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
                "navigation.sections",
                "navigation.top",
                "navigation.indexes",
                "toc.follow",          # 👈 sticky TOC
                "toc.integrate"        # 👈 better integration
            ]
        },

        "markdown_extensions": [
            "toc",
            "tables",
            "fenced_code",
            "admonition"
        ],

        "extra": {
            "toc": {
                "depth": 3  # 👈 controls heading depth
            }
        },

        "extra_css": ["stylesheets/extra.css"],
        "extra_javascript": ["js/analytics.js"],

        "nav": [
            {"🏠 Home Dashboard": "index.md"},
            {"🧪 Sample Page": "sample-page.md"},
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
.md-content {
    max-width: 900px;
    margin: auto;
}
""")


# ----------------------
# ANALYTICS
# ----------------------

def write_analytics(docs):
    js_dir = docs / "js"
    js_dir.mkdir(parents=True, exist_ok=True)

    if not CF_TOKEN:
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
    subprocess.run(["git", "commit", "-m", "feat: enable TOC on all pages"], check=False)
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

    print("✅ TOC enabled across all pages")


if __name__ == "__main__":
    main()