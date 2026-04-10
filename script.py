#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

IGNORE_DIRS = {".obsidian", ".trash", "_resources"}
MAX_NAME = 120


# ----------------------
# ORDER + CLEANING
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


def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text.strip())
    text = re.sub(r'[\s_-]+', ' ', text)
    text = text.title().replace(" ", "-")
    return text[:MAX_NAME].strip("-") or "Note"


# ----------------------
# BUILD MAP
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
        new_rel = rel.with_name(new_name)

        mapping[rel] = new_rel

    return mapping


# ----------------------
# IMAGE FIX (NEW SYSTEM)
# ----------------------

def fix_images(content):
    """
    Convert Joplin _resources references into local folder resources
    """

    # normalize all Joplin variants
    content = re.sub(r'!\[([^\]]*)\]\([^)]*_resources/', r'![\1](resources/', content)

    # fallback replacements
    content = content.replace("_resources/", "resources/")

    return content


# ----------------------
# CONTENT FIX
# ----------------------

def fix_content(content):
    lines = content.splitlines()
    fixed = []

    for line in lines:

        # TOC FIX (include first heading now)
        if line.startswith("#"):
            line = "#" + line  # shift everything down one level

        fixed.append(line)

    return fix_images("\n".join(fixed))


# ----------------------
# WRITE DOCS
# ----------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # ----------------------
    # HOME PAGE
    # ----------------------

    (docs / "index.md").write_text("""
# Vault Wiki

## Start Here
- [Sample Page](sample-page.md)
""")

    (docs / "sample-page.md").write_text("""
# Sample Page

## Section 1
Example

## Section 2
More content
""")

    # ----------------------
    # FILES
    # ----------------------

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        content = src_file.read_text(encoding="utf-8", errors="ignore")
        content = fix_content(content)

        # ----------------------
        # COPY LOCAL RESOURCES
        # ----------------------

        src_folder = src_file.parent
        dst_folder = dst_file.parent

        src_res = src_folder / "_resources"
        dst_res = dst_folder / "resources"

        if src_res.exists():
            if dst_res.exists():
                shutil.rmtree(dst_res)
            shutil.copytree(src_res, dst_res)

        dst_file.write_text(content, encoding="utf-8")


# ----------------------
# NAV BUILD (IGNORES _resources)
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
# MKDOCS
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
                "navigation.sections",
                "navigation.path",
                "navigation.top",
                "toc.follow"
            ]
        },
        "markdown_extensions": [
            {"toc": {"permalink": True}},
            "tables",
            "fenced_code"
        ],
        "nav": [
            {"Home": "index.md"},
            {"Sample": "sample-page.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------
# DEPLOY
# ----------------------

def deploy():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: images + nav cleanup"], check=False)
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
    write_mkdocs(docs)
    deploy()

    print("✅ FIXED: images + navigation + resources handling")


if __name__ == "__main__":
    main()