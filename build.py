"""
Static Site Generator for CBSE English Complete
=================================================
Builds ONE real, crawlable HTML file per chapter (content baked in server-side,
no JavaScript required to see it) at a clean slug URL like:

    /summer-of-the-beautiful-white-horse/index.html

This is the correct approach for GitHub Pages SEO: Google indexes actual HTML
files at actual URLs, not query-string variations of a single JS-rendered page.

USAGE (local):
    pip install markdown beautifulsoup4
    python3 build.py
    -> writes everything into ./dist

USAGE (automatic): the accompanying .github/workflows/deploy.yml runs this on
every push to main and publishes ./dist via GitHub Pages.
"""
import json
import re
import shutil
from pathlib import Path
import markdown
from bs4 import BeautifulSoup

SITE_URL = "https://cgcb-01.github.io/Englishopeadia/"
SITE_NAME = "CBSE English Complete"
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
CHAPTERS_DIR = ROOT / "chapters"


# ---------- slugify (MUST match slugify used anywhere links are built) ----------
def slugify(title: str) -> str:
    t = re.sub(r"\s*\(\s*\d+\s*pages?\s*\)", "", title, flags=re.I)
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    return t


# ---------- port of the custom [C]/[B]/[U]/[[split]]/blockquote formatting ----------
def convert_markdown_to_book_format(html: str) -> str:
    html = re.sub(r"\[C\](.*?)\[/C\]", r'<div class="qa-center">\1</div>', html, flags=re.S | re.I)
    html = re.sub(r"\[B\](.*?)\[/B\]", r'<span class="qa-standout-bold">\1</span>', html, flags=re.S | re.I)
    html = re.sub(r"\[U\](.*?)\[/U\]", r'<span class="qa-underline">\1</span>', html, flags=re.S | re.I)

    soup = BeautifulSoup(html, "html.parser")
    final_wrapper = soup.new_tag("div")
    current_block = soup.new_tag("div")
    current_block["class"] = "book-columns"
    final_wrapper.append(current_block)

    SECTION_HEADS = {
        "justification of title", "theme", "summary", "character", "characters",
        "important questions", "notice", "grammar", "exercise",
    }

    for node in list(soup.contents):
        if getattr(node, "name", None) is None:
            current_block.append(node.extract())
            continue

        raw_text = node.get_text().strip()
        raw_text_clean = re.sub(r"\s*\(\s*\d+\s*pages?\s*\)", "", raw_text, flags=re.I)
        tag = node.name.upper()

        if tag in ("H1", "H2", "H3") or raw_text_clean.lower() in SECTION_HEADS:
            head = soup.new_tag("div")
            head["class"] = "book-section-heading"
            head.string = raw_text_clean
            final_wrapper.append(head)
            current_block = soup.new_tag("div")
            current_block["class"] = "book-columns"
            final_wrapper.append(current_block)

        elif raw_text_clean.lower() == "[[split]]":
            grid = soup.new_tag("div"); grid["class"] = "col-split-wrap"
            col_left = soup.new_tag("div"); col_left["class"] = "col-left"
            col_right = soup.new_tag("div"); col_right["class"] = "col-right"
            for child in list(current_block.contents):
                col_left.append(child.extract())
            if current_block in final_wrapper.contents:
                current_block.extract()
            grid.append(col_left); grid.append(col_right)
            final_wrapper.append(grid)
            current_block = col_right

        elif tag == "BLOCKQUOTE":
            box = soup.new_tag("div"); box["class"] = "book-answer-box"
            inner = node.decode_contents()
            inner = re.sub(r"<strong>(.*?)</strong>", r'<div class="box-title-center">\1</div>', inner, flags=re.S)
            box.append(BeautifulSoup(inner, "html.parser"))
            current_block.append(box)

        elif re.match(r"^\[Q\]", raw_text, re.I) and re.search(r"\[/Q\]", raw_text, re.I):
            qdiv = soup.new_tag("div"); qdiv["class"] = "qa-q"
            inner = node.decode_contents()
            inner = re.sub(r"\[Q\]", "", inner, flags=re.I)
            inner = re.sub(r"\[/Q\]", "", inner, flags=re.I)
            qdiv.append(BeautifulSoup(inner, "html.parser"))
            current_block.append(qdiv)

        elif raw_text.upper().startswith("A:") or raw_text.upper().startswith("ANS:"):
            adiv = soup.new_tag("div"); adiv["class"] = "qa-a"
            adiv.append(BeautifulSoup(node.decode_contents(), "html.parser"))
            current_block.append(adiv)

        else:
            current_block.append(node.extract())

    out = str(final_wrapper).replace("[br]", "<br>")
    return out


# ---------- shared page shell ----------
def page_shell(*, title, description, canonical, content_html, sidebar_html, ld_json, h1=None):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{canonical}"/>
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{SITE_NAME}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{canonical}" />
    <meta name="twitter:card" content="summary" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{rel_root(canonical)}style.css"/>
    <script type="application/ld+json">{ld_json}</script>
</head>
<body>
    <div class="sidebar-overlay" id="sidebarOverlay"></div>
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1><i class="fas fa-book-open"></i> <a href="{SITE_URL}" style="color:inherit;text-decoration:none;">CBSE English</a></h1>
            <button class="close-btn" id="closeSidebar"><i class="fas fa-times"></i></button>
        </div>
        <div class="sidebar-search">
            <div class="search-wrapper">
                <i class="fas fa-search search-icon"></i>
                <input type="text" id="sidebarSearch" placeholder="Search topics..." />
            </div>
        </div>
        <nav class="sidebar-nav" id="sidebarNav">{sidebar_html}</nav>
    </aside>
    <main class="main-content">
        <header class="topbar">
            <div class="topbar-left">
                <button class="hamburger" id="hamburgerBtn"><i class="fas fa-bars"></i></button>
                <div class="breadcrumb" style="font-weight:600;">{h1 or title}</div>
            </div>
            <div class="topbar-actions">
                <button onclick="window.print()"><i class="fas fa-print"></i></button>
            </div>
        </header>
        <div class="content-area" id="contentArea">
            {content_html}
        </div>
    </main>
    <script src="{rel_root(canonical)}script.js"></script>
</body>
</html>
"""


def rel_root(canonical_url: str) -> str:
    # chapter pages live one folder deep -> need ../ to reach shared assets; homepage needs none
    return "" if canonical_url.rstrip("/") == SITE_URL.rstrip("/") else "../"


def build_slug_map(metadata):
    """Compute one canonical slug per chapter id, resolving collisions consistently."""
    used = {}
    slug_map = {}
    for item_id, item in metadata.items():
        base = slugify(item["title"])
        slug = base
        if slug in used:
            slug = f"{base}-class-{item['class']}" if item['class'] != 'all' else f"{base}-{item_id}"
            if slug in used:
                slug = f"{base}-{item_id}"
        used[slug] = item_id
        slug_map[item_id] = slug
    return slug_map


def build_sidebar(metadata, slug_map, active_id=None):
    sections = {"11": [], "12": [], "all": []}
    for item in metadata.values():
        sections.setdefault(item["class"], []).append(item)
    html = ""
    labels = {"11": "Class 11", "12": "Class 12", "all": "All Rounder"}
    for cls in ("11", "12", "all"):
        items = sections.get(cls, [])
        if not items:
            continue
        html += f'<div class="nav-section"><div class="nav-section-title">{labels[cls]}</div>'
        for item in items:
            clean_title = re.sub(r"\s*\(\s*\d+\s*pages?\s*\)", "", item["title"], flags=re.I)
            slug = slug_map[item["id"]]
            active = " active" if item["id"] == active_id else ""
            html += (
                f'<a class="nav-item{active}" href="{SITE_URL}{slug}/">'
                f'<span class="nav-icon"><i class="fas fa-feather-alt"></i></span>'
                f'<span>{clean_title}</span></a>'
            )
        html += "</div>"
    return html


def main():
    metadata = json.loads((ROOT / "metadata.json").read_text())

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # copy static assets
    for fname in ("style.css", "script.js", "metadata.json", "robots.txt", "google7686b6265bd7f1dd.html"):
        src = ROOT / fname
        if src.exists():
            shutil.copy(src, DIST / fname)

    sitemap_urls = [f"  <url>\n    <loc>{SITE_URL}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>1.0</priority>\n  </url>"]

    slug_map = build_slug_map(metadata)

    for item_id, item in metadata.items():
        slug = slug_map[item_id]

        md_path = CHAPTERS_DIR / item["file"]
        if not md_path.exists():
            print(f"WARNING: missing {md_path}, skipping")
            continue

        md_text = md_path.read_text(encoding="utf-8")
        raw_html = markdown.markdown(md_text, extensions=["extra"])
        content_html = convert_markdown_to_book_format(raw_html)

        clean_title = re.sub(r"\s*\(\s*\d+\s*pages?\s*\)", "", item["title"], flags=re.I)
        cls_label = "11 & 12" if item["class"] == "all" else item["class"]
        page_title = f"{clean_title} - CBSE Class {cls_label} English | {SITE_NAME}"
        description = f"CBSE Class {cls_label} English: {clean_title} - summary, important questions with answers, themes and analysis. Free notes."
        canonical = f"{SITE_URL}{slug}/"

        ld_json = json.dumps({
            "@context": "https://schema.org",
            "@type": "LearningResource",
            "name": page_title,
            "description": description,
            "url": canonical,
            "educationalLevel": f"Class {cls_label}",
            "about": clean_title,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL},
        })

        page_html = page_shell(
            title=page_title,
            description=description,
            canonical=canonical,
            content_html=f'<div class="page-header"><h1>{clean_title}</h1></div><div class="page-body">{content_html}</div>',
            sidebar_html=build_sidebar(metadata, slug_map, active_id=item_id),
            ld_json=ld_json,
            h1=clean_title,
        )

        page_dir = DIST / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(page_html, encoding="utf-8")

        sitemap_urls.append(
            f"  <url>\n    <loc>{canonical}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>"
        )

    # homepage: real static directory listing (also fully crawlable, no JS needed)
    home_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": "Free CBSE Class 11 & 12 English chapter summaries, important questions with answers, grammar and writing skills notes.",
    })
    home_content = '<div class="page-header"><h1>CBSE English Complete — Class 11 &amp; 12</h1></div><div class="page-body">'
    home_content += "<p>Browse chapter summaries, important questions with answers, grammar notes and writing-skills guides for CBSE Class 11 &amp; 12 English. Pick a topic from the menu.</p>"
    home_content += "<ul style='margin-top:1.5rem;'>"
    for item in metadata.values():
        slug = slug_map[item["id"]]
        clean_title = re.sub(r"\s*\(\s*\d+\s*pages?\s*\)", "", item["title"], flags=re.I)
        home_content += f'<li><a href="{SITE_URL}{slug}/">{clean_title}</a></li>'
    home_content += "</ul></div>"

    home_html = page_shell(
        title=f"CBSE Class 11 & 12 English Notes, Summaries & Answers | {SITE_NAME}",
        description="Free CBSE Class 11 & 12 English study material: chapter summaries, important questions with answers, themes, characters, grammar and writing skills.",
        canonical=SITE_URL,
        content_html=home_content,
        sidebar_html=build_sidebar(metadata, slug_map),
        ld_json=home_ld,
        h1="Home",
    )
    (DIST / "index.html").write_text(home_html, encoding="utf-8")

    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap_urls)
        + "\n</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    if not (DIST / "robots.txt").exists():
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")

    print(f"Built {len(slug_map)} chapter pages + homepage into {DIST}")


if __name__ == "__main__":
    main()
