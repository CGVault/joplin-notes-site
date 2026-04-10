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
# SLUGIFY (PROPER CASE SAFE)
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
# FOLDER LANDING PAGES
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

        content = f"""---
title: {folder_name}
---

# {folder_name}

"""

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

        "nav": [
            {"Home": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS (UPDATED HEADINGS ONLY)
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

a {
    color: #0078D4;
}

.md-content {
    padding: 24px 32px;
    max-width: 900px;
    margin: auto;
}

/* =========================
   UPGRADED HEADINGS
   ========================= */

/* H1 = Page title (very strong) */
h1 {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    border-bottom: 4px solid #0078D4;
    padding-bottom: 12px;
    margin-bottom: 20px;
}

/* H2 = Section headers */
h2 {
    font-size: 1.9rem;
    font-weight: 800;
    margin-top: 28px;
    margin-bottom: 12px;
    color: #1a1a1a;
}

/* H3 = Subsections */
h3 {
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 20px;
}

/* Ensure MkDocs doesn't override */
.md-content h1,
.md-content h2,
.md-content h3 {
    font-weight: 900 !important;
}

/* Slight visual hierarchy boost */
h2::before {
    content: "";
    display: block;
    width: 40px;
    height: 3px;
    background: #0078D4;
    margin-bottom: 8px;
}
""")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)

    subprocess.run(
        ["git", "commit", "-m", "sync full vault + docs"],
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
    generate_folder_indexes(docs)
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ Headings upgraded (H1/H2/H3 Microsoft-style hierarchy improved)")


if __name__ == "__main__":
    main()