#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path
import subprocess

# ---------------------------
# CONFIG
# ---------------------------

MAX_NAME = 80

# ---------------------------
# UTIL
# ---------------------------

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:MAX_NAME].strip("-") or "note"


def extract_title(md, fallback):
    m = re.search(r'^\s*#\s+(.+)', md, re.MULTILINE)
    return m.group(1).strip() if m else fallback


# ---------------------------
# STEP 1: FILE MAPPING
# ---------------------------

def build_map(src):
    mapping = {}
    used = set()

    for f in src.rglob("*"):
        if not f.is_file():
            continue

        rel = f.relative_to(src)

        if f.suffix == ".md":
            content = f.read_text(errors="ignore")
            title = extract_title(content, f.stem)
            new_name = slugify(title) + ".md"
        else:
            new_name = slugify(f.stem) + f.suffix

        new_path = Path(*[slugify(p) for p in rel.parts[:-1]]) / new_name

        base = new_path
        i = 1
        while str(new_path) in used:
            new_path = base.with_name(f"{base.stem}-{i}{base.suffix}")
            i += 1

        used.add(str(new_path))
        mapping[str(rel)] = str(new_path)

    return mapping


# ---------------------------
# STEP 2: WRITE FILES
# ---------------------------

def write_docs(src, docs, mapping):
    if docs.exists():
        shutil.rmtree(docs)
    docs.mkdir()

    # homepage
    (docs / "index.md").write_text("# Home\n\nWelcome to your notes.")

    for orig, new in mapping.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

        if dst_file.suffix == ".md":
            txt = dst_file.read_text(errors="ignore")
            title = extract_title(txt, dst_file.stem)

            if not txt.startswith("---"):
                txt = f"---\ntitle: {title}\n---\n\n" + txt

            dst_file.write_text(txt)


# ---------------------------
# STEP 3: CREATE FOLDER INDEXES (KEY FIX 🔥)
# ---------------------------

def create_folder_indexes(docs):
    for root, dirs, files in os.walk(docs):

        root = Path(root)

        # skip root
        if root == docs:
            continue

        has_md = any(f.endswith(".md") for f in os.listdir(root))

        # ALWAYS create index.md for folder
        index = root / "index.md"

        if not index.exists():
            title = root.name.replace("-", " ").title()

            index.write_text(f"""---
title: {title}
---

# {title}

This section contains notes for {title}.
""")

        # ensure folder is discoverable in nav
        if not has_md:
            continue


# ---------------------------
# STEP 4: CLEAN NAV (FIXED TREE)
# ---------------------------

def build_nav(docs):
    def walk(folder):
        items = []

        for p in sorted(folder.iterdir()):
            if p.is_dir():
                if (p / "index.md").exists():
                    items.append({p.name.replace("-", " ").title(): walk(p)})
            elif p.suffix == ".md":
                if p.name != "index.md":
                    title = p.stem.replace("-", " ").title()
                    rel = p.relative_to(docs).as_posix()
                    items.append({title: rel})

        return items

    return walk(docs)


def write_mkdocs(docs):
    nav = build_nav(docs)

    import yaml

    config = {
        "site_name": "Joplin Notes",
        "theme": {"name": "material"},
        "docs_dir": "docs",
        "nav": [
            {"Home": "index.md"},
            *nav
        ]
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ---------------------------
# STEP 5: RUN GIT
# ---------------------------

def git_push():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "sync"], check=False)
    subprocess.run(["git", "push"], check=True)


# ---------------------------
# MAIN
# ---------------------------

def main():
    import sys

    src = Path(sys.argv[1]).resolve()
    docs = Path("docs")

    mapping = build_map(src)
    write_docs(src, docs, mapping)
    create_folder_indexes(docs)
    write_mkdocs(docs)
    git_push()

    print("✅ Done → run: mkdocs serve")


if __name__ == "__main__":
    main()