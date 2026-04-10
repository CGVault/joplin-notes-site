#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

IGNORE_DIRS = {".obsidian", ".trash", "_resources"}


# ----------------------
# CLEANING
# ----------------------

def parse_order(name):
    match = re.match(r'^(\d+)[\.\-\s]+(.+)$', name)
    if match:
        return int(match.group(1)), match.group(2)
    return 9999, name


def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text.strip())
    text = re.sub(r'[\s_-]+', ' ', text)
    return text.title().replace(" ", "-")


def clean_title(name):
    _, title = parse_order(Path(name).stem)
    return title


# ----------------------
# BUILD FILE MAP
# ----------------------

def build_map(src):
    mapping = []

    for f in src.rglob("*.md"):
        rel = f.relative_to(src)

        if any(part in IGNORE_DIRS for part in rel.parts):
            continue

        mapping.append(rel)

    return mapping


# ----------------------
# FIX CONTENT (IMPORTANT)
# ----------------------

def fix_content(content):

    # FIX IMAGE PATHS
    content = re.sub(
        r'!\[([^\]]*)\]\([^)]*?_resources/',
        r'![\1](resources/',
        content
    )

    content = content.replace("_resources/", "resources/")

    return content


# ----------------------
# WRITE FILES (LOCAL RESOURCES SYSTEM)
# ----------------------

def write_docs(src, docs, files):

    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir(parents=True, exist_ok=True)

    # ----------------------
    # HOME
    # ----------------------

    (docs / "index.md").write_text("# Vault Wiki\n")

    # ----------------------
    # PROCESS FILES
    # ----------------------

    for rel in files:
        src_file = src / rel

        dst_file = docs / rel

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
# BUILD NAV (FIXED - NO ORPHANS)
# ----------------------

def build_nav(docs):

    tree = {}

    for f in docs.rglob("*.md"):
        rel = f.relative_to(docs).as_posix()

        parts = Path(rel).parts

        cursor = tree

        for part in parts[:-1]:
            cursor = cursor.setdefault(part, {})

        cursor[parts[-1]] = rel

    return tree


def convert_nav(tree):
    nav = []

    for k, v in sorted(tree.items()):
        if isinstance(v, dict):
            nav.append({k: convert_nav(v)})
        else:
            name = Path(k).stem.replace("-", " ")
            nav.append({name: v})

    return nav


# ----------------------
# MKDOCS CONFIG
# ----------------------

def write_mkdocs(docs):
    import yaml

    nav_tree = build_nav(docs)
    nav = convert_nav(nav_tree)

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
    subprocess.run(["git", "commit", "-m", "fix: full nav + image system rewrite"], check=False)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["mkdocs", "gh-deploy", "--force"], check=True)


# ----------------------
# MAIN
# ----------------------

def main():
    import sys

    src = Path(sys.argv[1]).resolve()
    docs = Path("docs")

    files = build_map(src)

    write_docs(src, docs, files)
    write_mkdocs(docs)
    deploy()

    print("✅ FULL FIX: nav + images + orphan elimination complete")


if __name__ == "__main__":
    main()