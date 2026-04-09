#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

MAX_NAME = 80

# ----------------------------
# Helpers
# ----------------------------

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:MAX_NAME].strip("-") or "note"


def extract_title(text, fallback):
    m = re.search(r'^\s*#\s+(.+)', text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


# ----------------------------
# Build file mapping
# ----------------------------

def build_file_map(src_root):
    file_map = {}
    used = set()

    for file in src_root.rglob("*"):
        if not file.is_file():
            continue

        rel = file.relative_to(src_root)

        if file.suffix.lower() == ".md":
            content = file.read_text(errors="ignore")
            title = extract_title(content, file.stem)
            new_name = slugify(title) + ".md"
        else:
            new_name = slugify(file.stem) + file.suffix.lower()

        new_parts = [slugify(p) for p in rel.parts[:-1]]
        new_rel = Path(*new_parts) / new_name

        # avoid collisions
        base = new_rel
        i = 1
        while str(new_rel) in used:
            new_rel = base.with_name(f"{base.stem}-{i}{base.suffix}")
            i += 1

        used.add(str(new_rel))
        file_map[str(rel)] = str(new_rel)

    return file_map


# ----------------------------
# Fix links inside markdown
# ----------------------------

def rewrite_links(text, src_file, src_root, file_map, dst_file):
    def repl(match):
        prefix, url, suffix = match.groups()

        if url.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)

        target = (src_file.parent / url).resolve()

        try:
            rel = target.relative_to(src_root)
        except:
            return match.group(0)

        mapped = file_map.get(str(rel))
        if not mapped:
            return match.group(0)

        new_target = Path(mapped)
        rel_path = os.path.relpath(dst_file.parent / new_target, dst_file.parent)
        return f"{prefix}{rel_path.replace(os.sep, '/')}{suffix}"

    return re.sub(r'(!?\[.*?\]\()([^\)]+)(\))', repl, text)


# ----------------------------
# NAV (FIXED: clean labels, no raw paths)
# ----------------------------

def build_nav(docs_dir):
    nav = []

    for root, _, files in os.walk(docs_dir):
        root_path = Path(root)
        rel_root = root_path.relative_to(docs_dir)

        items = []

        for file in sorted(files):
            if not file.endswith(".md"):
                continue

            path = root_path / file
            title = extract_title(path.read_text(errors="ignore"), path.stem)

            rel = path.relative_to(docs_dir).as_posix()

            # CLEAN LABEL (no paths shown)
            items.append({title: rel})

        if items:
            if rel_root == Path("."):
                nav.extend(items)
            else:
                nav.append({rel_root.as_posix().replace("-", " ").title(): items})

    return nav


# ----------------------------
# MkDocs config (FIXED + HOMEPAGE)
# ----------------------------

def write_mkdocs_yml(docs_dir):
    nav = build_nav(docs_dir)

    # ALWAYS add homepage to avoid 404
    nav.insert(0, {"Home": "index.md"})

    import yaml

    config = {
        "site_name": "Joplin Notes",
        "theme": {
            "name": "material"
        },
        "docs_dir": "docs",
        "nav": nav
    }

    with open("mkdocs.yml", "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)


# ----------------------------
# Git
# ----------------------------

def run_git():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Sync notes"], check=False)
    subprocess.run(["git", "push"], check=True)


# ----------------------------
# MAIN
# ----------------------------

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python sync_joplin_to_mkdocs.py <export_folder>")
        return

    src = Path(sys.argv[1]).resolve()
    docs = Path("docs")

    if docs.exists():
        shutil.rmtree(docs)

    docs.mkdir()

    file_map = build_file_map(src)

    # Ensure homepage exists (FIX FOR YOUR 404)
    (docs / "index.md").write_text("# Home\n\nWelcome to your Joplin notes.")

    for orig, new in file_map.items():
        src_file = src / orig
        dst_file = docs / new

        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

        if dst_file.suffix == ".md":
            text = dst_file.read_text(errors="ignore")

            title = extract_title(text, dst_file.stem)
            frontmatter = f"---\ntitle: \"{title}\"\n---\n\n"

            if not text.startswith("---"):
                text = frontmatter + text

            text = rewrite_links(text, src_file, src, file_map, dst_file)
            dst_file.write_text(text)

    write_mkdocs_yml(docs)
    run_git()

    print("✅ Done. Run: mkdocs serve")


if __name__ == "__main__":
    main()