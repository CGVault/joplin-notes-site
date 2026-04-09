#!/usr/bin/env python3
"""
sync_joplin_to_mkdocs.py
Usage: python sync_joplin_to_mkdocs.py /path/to/joplin-export

Behavior:
- Walks the export folder and sanitizes filenames based on titles inside .md files.
- Rewrites image links to the new names.
- Copies sanitized tree to ./docs/<export_root_name> inside current git repo.
- Generates mkdocs.yml (basic) and a sidebar nav based on folder structure and titles.
- Commits & pushes changes to the repo (git must be configured).
- Writes docs/_mapping.json mapping original relative paths -> new relative paths.

Dependencies: Python 3.8+, standard library only.
"""
import sys, os, re, shutil, json, subprocess, datetime
from pathlib import Path
from urllib.parse import unquote

if len(sys.argv) < 2:
    print("Usage: python sync_joplin_to_mkdocs.py /path/to/joplin-export")
    sys.exit(1)

SRC = Path(sys.argv[1]).expanduser().resolve()
REPO = Path.cwd().resolve()
DOCS_DIR = REPO / "docs"
if not SRC.exists():
    print("Source export folder does not exist:", SRC)
    sys.exit(1)

# Settings
MAX_SLUG_LEN = 64
SAFE_RE = re.compile(r"[^a-z0-9._-]")
TITLE_RE = re.compile(r'^\s{0,3}#{1,6}\s+(.*\S)', flags=re.MULTILINE)
MD_LINK_RE = re.compile(r'(!?\[.*?\]\()([^\)\s]+)(\))')  # captures ![](url) and [](...)
IMG_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}

def slugify(name, max_len=MAX_SLUG_LEN):
    name = unquote(name)
    name = name.lower().strip()
    name = name.replace(" ", "-")
    name = re.sub(r'[-_]+', '-', name)
    name = SAFE_RE.sub('-', name)
    if len(name) > max_len:
        base, dot, ext = name.rpartition(".")
        if dot:
            ext = ext[:10]
            base = base[:max_len - 1 - len(ext)]
            name = f"{base}.{ext}"
        else:
            name = name[:max_len]
    name = name.strip("-")
    return name or "file"

# Build list of files
all_files = [p for p in SRC.rglob("*") if p.is_file()]

# mapping original -> new relative path under docs/<root>
root_name = SRC.name
OUT_ROOT = DOCS_DIR / root_name

original_to_new = {}
collision_counters = {}

def unique_path_for(desired_path):
    """Ensure no collision: append -n if exists."""
    p = Path(desired_path)
    key = str(p.parent / p.name)
    if key not in collision_counters:
        collision_counters[key] = 0
    candidate = p
    while candidate.exists() or str(candidate) in original_to_new.values():
        collision_counters[key] += 1
        stem = p.stem
        ext = p.suffix
        candidate = p.parent / f"{stem}-{collision_counters[key]}{ext}"
    return candidate

# First pass: determine new filenames
for src_file in all_files:
    rel = src_file.relative_to(SRC)
    rel_parts = rel.parts
    # If markdown, try to extract title
    if src_file.suffix.lower() == ".md":
        text = src_file.read_text(encoding="utf-8", errors="ignore")
        m = TITLE_RE.search(text)
        if m:
            title = m.group(1).strip()
        else:
            title = src_file.stem
        # create slug filename from title
        slug_base = slugify(title)
        slug_name = f"{slug_base}.md" if not slug_base.endswith(".md") else slug_base
    else:
        # resource: slugify original filename
        slug_name = slugify(src_file.name)
        # preserve extension if lost
        if not Path(slug_name).suffix and src_file.suffix:
            slug_name = slug_name + src_file.suffix.lower()
    # Build new relative path preserving intermediate directories (slugify dirs)
    new_parts = []
    for i, part in enumerate(rel_parts[:-1]):
        new_parts.append(slugify(part))
    new_parts.append(slug_name)
    new_rel = Path(*new_parts)
    out_path = OUT_ROOT / new_rel
    # ensure unique on disk
    unique_out = unique_path_for(out_path)
    # store mapping as relative to OUT_ROOT
    original_to_new[str(rel)] = str(unique_out.relative_to(OUT_ROOT))

# Prepare output folder: remove existing OUT_ROOT then recreate
if OUT_ROOT.exists():
    print("Removing existing output folder:", OUT_ROOT)
    shutil.rmtree(OUT_ROOT)
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# Second pass: copy files and rewrite markdown links
def find_new_for(original_rel_str):
    return original_to_new.get(original_rel_str)

for src_file in all_files:
    rel = src_file.relative_to(SRC)
    new_rel = find_new_for(str(rel))
    if not new_rel:
        continue
    dst = OUT_ROOT / new_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    # Copy file
    shutil.copy2(src_file, dst)
    # If markdown, ensure frontmatter title and rewrite image links
    if dst.suffix.lower() == ".md":
        txt = dst.read_text(encoding="utf-8", errors="ignore")
        m = TITLE_RE.search(txt)
        if m:
            title = m.group(1).strip()
        else:
            # infer from original filename (original rel may include directories)
            title = src_file.stem
            # prepend H1 if missing
            txt = f"# {title}\n\n" + txt
        # add YAML frontmatter with title if not present
        if txt.lstrip().startswith("---"):
            # basic check: if frontmatter present, try to inject title if missing
            # naive: skip; assume user didn't have frontmatter
            pass
        else:
            front = f"---\ntitle: \"{title.replace('\"','\\\"')}\"\n---\n\n"
            txt = front + txt if not txt.startswith(front) else txt
        # rewrite local links/images
        def repl(mobj):
            prefix, url, suffix = mobj.group(1), mobj.group(2), mobj.group(3)
            # ignore URLs that are absolute (http:// or https:// or mailto:)
            if re.match(r'^[a-z]+://', url) or url.startswith("mailto:") or url.startswith("#"):
                return mobj.group(0)
            # strip fragment/query for mapping lookup
            url_clean = url.split("#")[0].split("?")[0]
            # If url is relative, attempt to resolve against src_file parent
            candidate = (src_file.parent / url_clean).resolve() if not Path(url_clean).is_absolute() else Path(url_clean)
            try:
                rel_to_src = candidate.relative_to(SRC)
                rel_key = str(rel_to_src)
                mapped = find_new_for(rel_key)
                if mapped:
                    # compute new relative path from dst parent to OUT_ROOT/mapped
                    new_target = Path(mapped)
                    new_rel_path = os.path.relpath(OUT_ROOT / new_target, start=dst.parent)
                    new_rel_path = new_rel_path.replace(os.path.sep, "/")
                    # preserve fragment/query
                    frag = ""
                    if "#" in url:
                        frag = "#" + url.split("#",1)[1]
                    if "?" in url:
                        frag = "?" + url.split("?",1)[1]
                    return f"{prefix}{new_rel_path}{frag}{suffix}"
            except Exception:
                # can't map; leave as-is
                return mobj.group(0)
            return mobj.group(0)
        new_txt = MD_LINK_RE.sub(repl, txt)
        dst.write_text(new_txt, encoding="utf-8")

# Generate mkdocs.yml with nav
def build_nav_tree(mapping):
    """
    mapping: original_to_new values keyed by original rel (unused here)
    Build nested dict from OUT_ROOT structure to create nav entries.
    """
    nav = []
    # Walk OUT_ROOT
    for dirpath, dirnames, filenames in os.walk(OUT_ROOT):
        # sort to give stable order
        dirpath_p = Path(dirpath)
    # We'll build nav by walking OUT_ROOT and mapping to nested structure
    def build_node(path):
        items = []
        # list directories first
        children = sorted([p for p in path.iterdir() if p.is_dir()])
        files = sorted([p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".md"])
        for f in files:
            # read title from frontmatter or H1
            content = f.read_text(encoding="utf-8", errors="ignore")
            title = None
            fm = re.match(r'^\s*---\s*\n(.*?)\n---\s*\n', content, flags=re.S)
            if fm:
                # try to find title: title: "..."
                m = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', fm.group(1), flags=re.M)
                if m:
                    title = m.group(1).strip()
            if not title:
                m2 = TITLE_RE.search(content)
                if m2:
                    title = m2.group(1).strip()
            if not title:
                title = f.stem
            rel = f.relative_to(OUT_ROOT).as_posix()
            items.append({title: rel})
        for c in children:
            sub = build_node(c)
            if sub:
                items.append({c.name: sub})
        return items
    nav = [{root_name: build_node(OUT_ROOT)}]
    return nav

nav = build_nav_tree(original_to_new)

mk = {
    "site_name": f"{root_name} Notes",
    "docs_dir": "docs",
    "site_url": "",
    "theme": {"name": "material"},
    "nav": nav
}

# Write mkdocs.yml
import yaml  # attempt import, but we'll fallback if pyyaml not present
try:
    import yaml as _yaml
    with open(REPO / "mkdocs.yml", "w", encoding="utf-8") as f:
        _yaml.safe_dump(mk, f, sort_keys=False)
except Exception:
    # fallback: produce a simple yaml via json->yaml naive
    with open(REPO / "mkdocs.yml", "w", encoding="utf-8") as f:
        f.write("site_name: \"{}\"\n".format(mk["site_name"]))
        f.write("docs_dir: \"docs\"\n")
        f.write("theme:\n  name: material\n")
        f.write("nav:\n")
        def write_nav(items, indent=2):
            for it in items:
                if isinstance(it, dict):
                    for k,v in it.items():
                        f.write(" " * indent + "- {}:\n".format(k))
                        if isinstance(v, list):
                            write_nav(v, indent+2)
                        else:
                            f.write(" "*(indent+2) + "- {}\n".format(v))
                else:
                    f.write(" " * indent + "- {}\n".format(it))
        write_nav(mk["nav"], indent=2)

# Write mapping file into OUT_ROOT
with open(OUT_ROOT / "_mapping.json", "w", encoding="utf-8") as mf:
    json.dump(original_to_new, mf, indent=2, ensure_ascii=False)

# Git operations: replace files under docs/<root_name>
# The script already wrote to docs/<root_name>. Now commit & push.
def run(cmd, check=True):
    print(">", " ".join(cmd))
    r = subprocess.run(cmd, cwd=REPO)
    if check and r.returncode != 0:
        print("Command failed:", cmd)
        sys.exit(1)

# Stage changes
run(["git", "add", "--all", "docs", "mkdocs.yml"])
# Commit
ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
commit_msg = f"Sync Joplin export -> mkdocs: {root_name} @ {ts}"
run(["git", "commit", "-m", commit_msg])
# Push
run(["git", "push", "origin", "HEAD"])

print("Sync complete.")
print("Docs available under docs/{}".format(root_name))
print("mkdocs.yml written to repo root.")
print("Mapping file at:", OUT_ROOT / "_mapping.json")