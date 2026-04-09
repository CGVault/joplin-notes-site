#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
from pathlib import Path

# ========= CONFIG =========
MAX_NAME = 80
# ==========================

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:MAX_NAME].strip("-") or "note"

def extract_title(md_text, fallback):
    # First heading
    m = re.search(r'^\s*#\s+(.+)', md_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return fallback

def build_file_map(src_root):
    file_map = {}
    used = set()

    for file in src_root.rglob("*"):
        if not file.is_file():
            continue

        rel = file.relative_to(src_root)

        # Handle markdown
        if file.suffix.lower() == ".md":
            content = file.read_text(errors="ignore")
            title = extract_title(content, file.stem)
            name = slugify(title) + ".md"
        else:
            name = slugify(file.stem) + file.suffix.lower()

        # Keep folder structure (slugified)
        new_parts = [slugify(p) for p in rel.parts[:-1]]
        new_path = Path(*new_parts) / name

        # Avoid collisions
        counter = 1
        base = new_path
        while str(new_path) in used:
            new_path = base.with_name(f"{base.stem}-{counter}{base.suffix}")
            counter += 1

        used.add(str(new_path))
        file_map[str(rel)] = str(new_path)

    return file_map

def rewrite_links(text, src_file, src_root, file_map, dst_file):
    def repl(match):
        prefix, url, suffix = match.groups()

        if url.startswith("http") or url.startswith("#"):
            return match.group(0)

        target = (src_file.parent / url).resolve()

        try:
            rel = target.relative_to(src_root)
        except:
            return match.group(0)

        new_rel = file_map.get(str(rel))
        if not new_rel:
            return match.group(0)

        # Compute relative path
        new_target = Path(new_rel)
        rel_path = os.path.relpath(dst_file.parent / new_target, dst_file.parent)
        rel_path = rel_path.replace("\\", "/")

        return f"{prefix}{rel_path}{suffix}"

    return re.sub(r'(!?\[.*?\]\()([^\)]+)(\))', repl, text)

def generate_nav(docs_dir):
    def walk(folder):
        items = []
        for p in sorted(folder.iterdir()):
            if p.is_dir():
                items.append({p.name: walk(p)})
            elif p.suffix == ".md":
                title = p.stem.replace("-", " ").title()
                rel = p.relative_to(docs_dir).as_posix()
                items.append({title: rel})
        return items

    return walk(docs_dir)

def write_mkdocs_yml(docs_dir):
    nav = generate_nav(docs_dir)

    yml = f"""site_name: Joplin Notes
theme:
  name: material
docs_dir: docs

nav:
"""

    def write_nav(items, indent=2):
        lines = []
        for item in items:
            for k, v in item.items():
                if isinstance(v, list):
                    lines.append(" " * indent + f"- {k}:")
                    lines += write_nav(v, indent + 2)
                else:
                    lines.append(" " * indent + f"- {k}: {v}")
        return lines

    yml += "\n".join(write_nav(nav))

    Path("mkdocs.yml").write_text(yml)

def run_git():
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Sync notes"], check=False)
    subprocess.run(["git", "push"], check=True)

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

    print("✅ Done. Now run: mkdocs gh-deploy")

if __name__ == "__main__":
    main()