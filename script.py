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
# WRITE DOCS (NO CONTENT MODIFICATION)
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

Use the sidebar to explore your notes.

---

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

### Subsection
Details.
""")

    # COPY FILES EXACTLY (NO MODIFICATION)
    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)


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
# {name}

This section contains related notes.
""")


# ----------------------
# BUILD NAV
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):
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
# MKDOCS CONFIG (REAL TOC FIX)
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
            "toc",  # IMPORTANT: this is what generates TOC from headings
            "tables",
            "fenced_code",
            "admonition"
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
# PROFESSIONAL CSS
# ----------------------

def write_css():
    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
:root {
    --md-text-font: "Segoe UI", system-ui, sans-serif;
}

/* Layout */
.md-content {
    max-width: 920px;
    margin: auto;
}

/* H1 - strong Microsoft style */
h1 {
    font-size: 2.5rem;
    font-weight: 800;  /* 🔥 strong bold */
    letter-spacing: -0.02em;
    border-bottom: 2px solid #e6e6e6;
    padding-bottom: 0.3em;
}

/* H2 */
h2 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 1.5em;
}

/* H3 */
h3 {
    font-size: 1.3rem;
    font-weight: 600;
}

/* Paragraph readability */
p {
    line-height: 1.7;
}

/* TOC sidebar */
.md-sidebar--secondary {
    border-left: 1px solid #eee;
    padding-left: 12px;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: proper TOC using real headings"], check=False)
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

    print("✅ TOC now reflects real Joplin headings")


if __name__ == "__main__":
    main()