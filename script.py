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
# FIX CONTENT (FORCE H2 TITLES)
# ----------------------

def fix_content(content):

    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    content = re.sub(
        r'!\[([^\]]*)\]\(:/([a-zA-Z0-9]+)\)',
        r'![\1](resources/\2)',
        content
    )

    content = content.replace("_resources/", "resources/")
    content = content.replace("\xa0", " ")
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

    lines = content.splitlines()
    new_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if re.match(r'^#{1,6}\S', stripped):
            stripped = re.sub(r'^(#{1,6})(\S)', r'\1 \2', stripped)

        if stripped.startswith("#"):
            text = re.sub(r'^#{1,6}\s*', '', stripped).strip()
            clean = f"## {text}"

            if new_lines and new_lines[-1].strip() != "":
                new_lines.append("")

            new_lines.append(clean)

            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                new_lines.append("")

            continue

        new_lines.append(line)

    return "\n".join(new_lines)


# ----------------------
# COPY RESOURCES
# ----------------------

def copy_all_resources(src, docs):
    for res in src.rglob("_resources"):
        if not res.is_dir():
            continue

        rel_parent = res.parent.relative_to(src)
        dst = docs / rel_parent / "resources"

        dst.mkdir(parents=True, exist_ok=True)

        for file in res.iterdir():
            if file.is_file():
                shutil.copy2(file, dst / file.name)


# ----------------------
# SAMPLE PAGE
# ----------------------

def create_sample_page(docs):
    sample = docs / "sample-page.md"

    sample.write_text("""# Sample Page

## Headings (TOC Example)

### Level 3 Heading

## Content Example

- notes
- images
- code
- links

## Purpose

Use this page as a template.
""", encoding="utf-8")


# ----------------------
# HOME PAGE
# ----------------------

def create_home_page(docs):
    home = docs / "index.md"

    home.write_text("""# Vault Wiki

## Welcome

- 📘 Sample Page

## Navigation

Use sidebar to browse notes.

## Features

- Fast search
- Clean TOC
- Joplin support
- Microsoft-style UI
""", encoding="utf-8")


# ----------------------
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):

    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    copy_all_resources(src, docs)

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# FOLDER INDEXES
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

        (root / "index.md").write_text(content, encoding="utf-8")


# ----------------------
# NAV BUILD
# ----------------------

def build_nav(docs):
    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):
            if any(part in IGNORE_DIRS for part in p.parts):
                continue

            if p.name == "sample-page.md":
                continue

            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({clean_folder(p.name): walk(p)})

            elif p.suffix == ".md" and p.name != "index.md":
                items.append({clean_display(p.name): p.relative_to(docs).as_posix()})

        return items

    return walk(docs)


# ----------------------
# MKDOCS CONFIG (SAFE + CLEAN)
# ----------------------

def write_mkdocs(docs):

    import yaml

    nav = [
        {"🏠 Home": "index.md"},
        {"🧪 Sample Page": "sample-page.md"},
        *build_nav(docs)
    ]

    config = {
        "site_name": "Vault Wiki",

        "plugins": [
            {
                "search": {
                    "separator": "[\\s\\-\\.]+",
                    "lang": "en"
                }
            }
        ],

        "theme": {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.tracking",
                "navigation.sections",
                "navigation.path",
                "navigation.top",
                "navigation.indexes",
                "toc.follow",
                "search.suggest",
                "search.highlight",
                "content.code.copy"
            ]
        },

        "markdown_extensions": [
            {"toc": {"permalink": True}},
            "tables",
            "fenced_code"
        ],

        "extra_css": ["stylesheets/extra.css"],
        "nav": nav
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# CSS (MICROSOFT STYLE — CLEAN VERSION)
# ----------------------

def write_css():

    css_dir = Path("docs/stylesheets")
    css_dir.mkdir(parents=True, exist_ok=True)

    (css_dir / "extra.css").write_text("""
body {
    font-size: 15.5px;
    line-height: 1.7;
}

/* Headings */
.md-typeset h1 {
    font-weight: 800;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 6px;
}

.md-typeset h2 {
    font-weight: 700;
    border-bottom: 2px solid #93c5fd;
    padding-bottom: 4px;
}

/* Active nav item */
.md-nav__link--active {
    color: #2563eb !important;
    font-weight: 600;
}

/* Hover nav */
.md-nav__link:hover {
    color: #1d4ed8;
}

/* Code blocks */
.md-typeset code {
    border-radius: 6px;
}

/* Spacing */
p {
    margin-bottom: 14px;
}

.md-typeset h2,
.md-typeset h3 {
    scroll-margin-top: 80px;
}
""", encoding="utf-8")


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "clean microsoft UI"], check=False)
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
    create_sample_page(docs)
    create_home_page(docs)
    write_css()
    write_mkdocs(docs)
    deploy()

    print("✅ CLEAN MICROSOFT UI VERSION COMPLETE")


if __name__ == "__main__":
    main()