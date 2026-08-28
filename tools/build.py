"""
Static site generator for xidenlz.github.io.

Content lives in `pages.py`. Running this script writes every HTML file,
plus sitemap.xml, feed.xml, robots.txt, and .nojekyll.

    py tools/build.py

Layouts are composed here; page-specific text is in pages.py.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, date
from pathlib import Path

from pages import (
    SITE_URL, AUTHOR, NAV, HOME, ABOUT, RESEARCH_INDEX, PROJECTS_INDEX,
    BLOG_INDEX, CONTACT, NOT_FOUND, ARTICLES, PROJECTS,
)

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# partials
# ---------------------------------------------------------------------------

def head(page):
    title = page["title"]
    tab_title = title if page.get("root") else f"{title} · Musaed"
    desc = page["description"]
    slug = page["slug"]
    canonical = SITE_URL + (slug if slug != "index" else "")
    og_image = f"{SITE_URL}assets/og/{page.get('og', slug)}.png"
    og_type = "article" if page.get("type") == "article" else "website"

    tags = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'<title>{html.escape(tab_title)}</title>',
        f'<meta name="description" content="{html.escape(desc)}">',
        f'<meta name="author" content="{AUTHOR}">',
        '<meta name="theme-color" content="#0a0b0d">',
        f'<link rel="canonical" href="{canonical}">',
        f'<meta property="og:site_name" content="Musaed">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:title" content="{html.escape(title)}">',
        f'<meta property="og:description" content="{html.escape(desc)}">',
        f'<meta property="og:image" content="{og_image}">',
        f'<meta property="og:image:width" content="1200">',
        f'<meta property="og:image:height" content="630">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(title)}">',
        f'<meta name="twitter:description" content="{html.escape(desc)}">',
        f'<meta name="twitter:image" content="{og_image}">',
    ]

    if page.get("type") == "article":
        tags.append(
            f'<meta property="article:published_time" '
            f'content="{page["date"].isoformat()}">'
        )
        tags.append(f'<meta property="article:author" content="{AUTHOR}">')

    prefix = page.get("asset_prefix", "")
    tags += [
        f'<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">',
        f'<link rel="alternate" type="application/rss+xml" title="Musaed research feed" href="{SITE_URL}feed.xml">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="preload" as="style" '
        'href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap">',
        '<link rel="stylesheet" '
        'href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap">',
        f'<link rel="stylesheet" href="{prefix}css/style.css">',
    ]

    ld = page.get("schema")
    if ld:
        tags.append(f'<script type="application/ld+json">{ld}</script>')

    return "\n  ".join(tags)


def masthead(page):
    prefix = page.get("asset_prefix", "")
    items = []
    for label, href in NAV:
        target = prefix + href
        active = ""
        current_slug = page["slug"]
        if href == "index.html" and current_slug == "index":
            active = ' aria-current="page"'
        elif href != "index.html" and current_slug.split("/")[0] == href.replace(".html", ""):
            active = ' aria-current="page"'
        items.append(f'<li><a href="{target}"{active}>{label}</a></li>')
    nav_items = "\n            ".join(items)

    return f'''<a class="skip-link" href="#main">Skip to content</a>

  <header class="masthead">
    <div class="wrap masthead-inner">
      <a class="wordmark" href="{prefix}index.html" aria-label="Musaed home">
        Musaed <span>&lt;/&gt;</span>
      </a>
      <button class="nav-toggle" type="button"
              aria-label="Toggle navigation" aria-expanded="false"
              aria-controls="nav-list">
        <svg class="icon-open" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <svg class="icon-close" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
      <nav aria-label="Primary">
        <ul id="nav-list" class="nav-list">
            {nav_items}
        </ul>
      </nav>
    </div>
  </header>'''


def footer(page):
    prefix = page.get("asset_prefix", "")
    year = date.today().year
    return f'''<footer class="site-footer">
    <div class="wrap footer-inner">
      <div>&copy; {year} Musaed &middot; xidenlz</div>
      <ul class="footer-nav">
        <li><a href="https://github.com/xidenlz" rel="me noopener">GitHub</a></li>
        <li><a href="{prefix}feed.xml">RSS</a></li>
        <li><a href="{prefix}contact.html">Contact</a></li>
      </ul>
    </div>
  </footer>'''


def page_template(page, body_html):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head(page)}
</head>
<body>
  {masthead(page)}

  <main id="main">
    <div class="wrap">
      {body_html}
    </div>
  </main>

  {footer(page)}

  <script src="{page.get("asset_prefix", "")}js/main.js" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------------------
# helpers used inside page content
# ---------------------------------------------------------------------------

def crumbs(page):
    trail = page.get("crumbs")
    if not trail:
        return ""
    parts = []
    for label, href in trail[:-1]:
        parts.append(f'<a href="{href}">{html.escape(label)}</a>')
    parts.append(f'<span aria-current="page">{html.escape(trail[-1][0])}</span>')
    return f'<div class="crumbs">{" / ".join(parts)}</div>'


def render_page_head(page):
    return f'''<div class="page-head">
      {crumbs(page)}
      <h1>{html.escape(page["title"])}</h1>
      <p class="page-sub">{html.escape(page["subtitle"])}</p>
    </div>'''


def render_tags(tags):
    if not tags:
        return ""
    items = "".join(f'<li>{html.escape(t)}</li>' for t in tags)
    return f'<ul class="tags" aria-label="Tags">{items}</ul>'


def render_entry(entry):
    aside_bits = []
    if entry.get("kicker"):
        aside_bits.append(f'<span class="kicker">{html.escape(entry["kicker"])}</span>')
    if entry.get("when"):
        aside_bits.append(f'<span>{html.escape(entry["when"])}</span>')
    if entry.get("note"):
        aside_bits.append(f'<span>{html.escape(entry["note"])}</span>')
    aside = "".join(aside_bits)

    title_html = html.escape(entry["title"])
    if entry.get("href"):
        title_html = f'<a href="{entry["href"]}">{title_html}</a>'

    body = [f'<h3 class="entry-title">{title_html}</h3>',
            f'<p class="entry-dek">{entry["dek"]}</p>']

    if entry.get("spec"):
        rows = "".join(
            f'<dt>{html.escape(k)}</dt><dd>{v}</dd>'
            for k, v in entry["spec"]
        )
        body.append(f'<dl class="spec">{rows}</dl>')

    if entry.get("tags"):
        body.append(render_tags(entry["tags"]))

    if entry.get("actions"):
        buttons = "".join(entry["actions"])
        body.append(f'<div class="hero-actions">{buttons}</div>')

    return f'''<li class="entry">
        <div class="entry-aside">{aside}</div>
        <div class="entry-body">{"".join(body)}</div>
      </li>'''


def render_index(entries):
    return f'<ol class="index">\n      {"".join(render_entry(e) for e in entries)}\n    </ol>'


def render_section(title, section_link, body_html):
    link_html = ""
    if section_link:
        label, href = section_link
        link_html = f'<a href="{href}">{html.escape(label)} &rarr;</a>'
    return f'''<section>
      <div class="section-head">
        <h2>{html.escape(title)}</h2>
        {link_html}
      </div>
      {body_html}
    </section>'''

# ---------------------------------------------------------------------------
# home
# ---------------------------------------------------------------------------

def render_home():
    hero_actions = "".join([
        '<a class="btn btn-primary" href="research.html">Read the research</a>',
        '<a class="btn" href="https://github.com/xidenlz" rel="noopener">GitHub</a>',
        '<a class="btn" href="contact.html">Contact</a>',
    ])

    featured = ARTICLES["battleye-internals"]
    featured_card = f'''<div class="entry-body">
      <p class="entry-note">Featured research &middot; {featured["date_display"]}</p>
      <h3 class="entry-title" style="font-size: var(--fs-2xl); margin-top: var(--sp-2)">
        <a href="research/{featured["slug"]}.html">{html.escape(featured["title"])}</a>
      </h3>
      <p class="entry-dek">{featured["dek"]}</p>
      {render_tags(featured["tags"][:5])}
    </div>'''

    project_ids = ["nt-injector", "screenshot-bypass", "pe-analyzer"]
    project_entries = [PROJECTS[p] for p in project_ids]
    projects_html = render_index([
        {
            "kicker": p["category"],
            "when": p["stack"],
            "title": p["title"],
            "dek": p["dek"],
            "tags": p["tags"][:4],
            "href": f'projects.html#{p["slug"]}',
        }
        for p in project_entries
    ])

    recent = sorted(
        [a for a in ARTICLES.values() if a["kind"] == "post"],
        key=lambda a: a["date"], reverse=True,
    )[:2]
    posts_html = render_index([
        {
            "kicker": p["category"],
            "when": p["date_display"],
            "title": p["title"],
            "dek": p["short_dek"],
            "tags": p["tags"][:4],
            "href": f'blog/{p["slug"]}.html',
        }
        for p in recent
    ])

    body = f'''<section class="hero">
        <p class="hero-role">Reverse engineering &middot; Windows internals &middot; anti-cheat research</p>
        <h1>Musaed</h1>
        <p class="hero-lede">
          Computer Science student at King Faisal University, graduating February 2027.
          I read binaries for a living. Kernel drivers, PE internals, and the seams
          where user mode meets the loader.
        </p>
        <div class="hero-actions">{hero_actions}</div>
      </section>

      {render_section("Featured research", ("All research", "research.html"), featured_card)}

      {render_section("Selected projects", ("All projects", "projects.html"), projects_html)}

      {render_section("Recent notes", ("All notes", "blog.html"), posts_html)}'''

    return page_template(HOME, body)

# ---------------------------------------------------------------------------
# about
# ---------------------------------------------------------------------------

def render_about():
    prose_html = f'''<div class="prose">
        <h2>Background</h2>
        <p>{ABOUT["background"]}</p>

        <h2>Focus</h2>
        <p>{ABOUT["focus"]}</p>
      </div>'''

    skills_html = "".join(
        f'''<div class="col">
          <h3>{html.escape(col["title"])}</h3>
          <ul>{"".join(f"<li>{html.escape(item)}</li>" for item in col["items"])}</ul>
        </div>'''
        for col in ABOUT["skills"]
    )

    record_html = "".join(
        f'''<div class="record-item">
          <div class="record-when">{html.escape(item["when"])}</div>
          <div class="record-what">
            <h3>{html.escape(item["role"])}</h3>
            <p class="record-where">{html.escape(item["where"])}</p>
            <p>{item["note"]}</p>
          </div>
        </div>'''
        for item in ABOUT["record"]
    )

    body = f'''{render_page_head(ABOUT)}
      {prose_html}
      <section>
        <div class="section-head"><h2>Skills</h2></div>
        <div class="cols">{skills_html}</div>
      </section>
      <section>
        <div class="section-head"><h2>Record</h2></div>
        <div class="record">{record_html}</div>
      </section>'''
    return page_template(ABOUT, body)

# ---------------------------------------------------------------------------
# research index
# ---------------------------------------------------------------------------

def render_research_index():
    research = sorted(
        [a for a in ARTICLES.values() if a["kind"] == "research"],
        key=lambda a: a["date"], reverse=True,
    )
    entries = [
        {
            "kicker": r["category"],
            "when": r["date_display"],
            "title": r["title"],
            "dek": r["dek"],
            "tags": r["tags"],
            "href": f'research/{r["slug"]}.html',
        }
        for r in research
    ]

    pending = RESEARCH_INDEX.get("pending", [])
    for p in pending:
        entries.append({
            "kicker": p["category"],
            "when": p["when"],
            "title": p["title"],
            "dek": p["dek"],
            "tags": p["tags"],
        })

    body = f'''{render_page_head(RESEARCH_INDEX)}
      {render_index(entries)}'''
    return page_template(RESEARCH_INDEX, body)

# ---------------------------------------------------------------------------
# projects
# ---------------------------------------------------------------------------

def render_projects():
    entries = []
    for p in PROJECTS.values():
        actions = []
        if p.get("link_url"):
            label = p.get("link_label", "Open link")
            actions.append(
                f'<a class="btn" href="{p["link_url"]}" rel="noopener">'
                f'{html.escape(label)}</a>'
            )
        entries.append({
            "kicker": p["category"],
            "when": p["stack"],
            "note": p.get("status"),
            "title": p["title"],
            "dek": p["long_dek"],
            "spec": p.get("primitives"),
            "tags": p["tags"],
            "actions": actions,
        })

    # entries are placed as <li>, but on projects page we want the slug id
    listing = []
    for entry, project in zip(entries, PROJECTS.values()):
        node = render_entry(entry)
        # attach id to the li so # anchors from the home page still work
        node = node.replace('<li class="entry">', f'<li class="entry" id="{project["slug"]}">', 1)
        listing.append(node)

    body = f'''{render_page_head(PROJECTS_INDEX)}
      <ol class="index">{"".join(listing)}</ol>'''
    return page_template(PROJECTS_INDEX, body)

# ---------------------------------------------------------------------------
# blog index
# ---------------------------------------------------------------------------

def render_blog_index():
    posts = sorted(
        [a for a in ARTICLES.values() if a["kind"] == "post"],
        key=lambda a: a["date"], reverse=True,
    )
    entries = [
        {
            "kicker": p["category"],
            "when": p["date_display"],
            "title": p["title"],
            "dek": p["short_dek"],
            "tags": p["tags"],
            "href": f'blog/{p["slug"]}.html',
        }
        for p in posts
    ]
    body = f'''{render_page_head(BLOG_INDEX)}
      {render_index(entries)}'''
    return page_template(BLOG_INDEX, body)

# ---------------------------------------------------------------------------
# contact
# ---------------------------------------------------------------------------

def render_contact():
    channels_html = "".join(
        f'''<li class="channel">
          {c["icon"]}
          <div class="channel-label">{html.escape(c["label"])}</div>
          <div class="channel-value">{c["value"]}</div>
          <p>{html.escape(c["note"])}</p>
        </li>'''
        for c in CONTACT["channels"]
    )

    body = f'''{render_page_head(CONTACT)}
      <div class="prose">
        <p>{CONTACT["intro"]}</p>
      </div>
      <ul class="channels">{channels_html}</ul>'''
    return page_template(CONTACT, body)

# ---------------------------------------------------------------------------
# 404
# ---------------------------------------------------------------------------

def render_404():
    body = f'''<div class="notfound">
      <p class="notfound-code">HTTP 404 &middot; page not mapped</p>
      <h1>Nothing at that offset.</h1>
      <p class="page-sub">
        The URL doesn’t resolve to a page on this site. It may have been renamed,
        or the link that got you here was stale.
      </p>
      <div class="hero-actions" style="margin-top: var(--sp-6)">
        <a class="btn btn-primary" href="index.html">Home</a>
        <a class="btn" href="research.html">Research</a>
        <a class="btn" href="blog.html">Blog</a>
      </div>
    </div>'''
    return page_template(NOT_FOUND, body)

# ---------------------------------------------------------------------------
# article
# ---------------------------------------------------------------------------

def render_article(article):
    byline_parts = [
        f'<span>Musaed</span>',
        f'<span><b>Published</b> {html.escape(article["date_display"])}</span>',
        f'<span><b>Category</b> {html.escape(article["category"])}</span>',
    ]
    if article.get("word_count"):
        byline_parts.append(
            f'<span><b>Read</b> ~{article["word_count"] // 220} min</span>'
        )
    byline = "".join(byline_parts)

    tag_html = render_tags(article["tags"])

    head_html = f'''<div class="article-head">
        <div class="crumbs">
          <a href="../index.html">home</a> /
          <a href="../{article["parent"]}.html">{article["parent"]}</a> /
          <span aria-current="page">{article["slug"]}</span>
        </div>
        <h1>{html.escape(article["title"])}</h1>
        <div class="byline">{byline}</div>
      </div>'''

    prose_html = f'''<article class="prose">
        {article["body"]}
        {tag_html}
      </article>'''

    toc_html = '''<aside class="toc" aria-label="On this page">
        <details open>
          <summary>On this page</summary>
        </details>
      </aside>'''

    body = f'''<div class="article">
        {prose_html}
        {toc_html}
      </div>
      {head_html.replace("article-head", "article-head-placeholder")}'''

    # Actually place article-head BEFORE the article grid.
    body = f'''{head_html}
      <div class="article">
        {prose_html}
        {toc_html}
      </div>'''

    slug = article["slug"]
    parent = article["parent"]
    parent_dir = "research" if article["kind"] == "research" else "blog"
    page = {
        "title": article["title"],
        "description": article["meta_description"],
        "slug": f"{parent_dir}/{slug}.html",
        "og": f"{parent_dir}-{slug}",
        "asset_prefix": "../",
        "type": "article",
        "date": article["date"],
        "crumbs": None,
        "schema": build_article_schema(article),
    }
    return page_template(page, body)


def build_article_schema(article):
    import json
    slug = article["slug"]
    parent_dir = "research" if article["kind"] == "research" else "blog"
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": article["title"],
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE_URL},
        "datePublished": article["date"].isoformat(),
        "url": f"{SITE_URL}{parent_dir}/{slug}.html",
        "description": article["meta_description"],
        "image": f"{SITE_URL}assets/og/{parent_dir}-{slug}.png",
        "publisher": {"@type": "Person", "name": AUTHOR, "url": SITE_URL},
    }, indent=None)

# ---------------------------------------------------------------------------
# feeds and site infra
# ---------------------------------------------------------------------------

def write_sitemap():
    entries = [
        ("", date.today()),
        ("about.html", date.today()),
        ("research.html", date.today()),
        ("projects.html", date.today()),
        ("blog.html", date.today()),
        ("contact.html", date.today()),
    ]
    for a in ARTICLES.values():
        parent = "research" if a["kind"] == "research" else "blog"
        entries.append((f'{parent}/{a["slug"]}.html', a["date"]))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, d in entries:
        lines.append(
            f'  <url><loc>{SITE_URL}{path}</loc>'
            f'<lastmod>{d.isoformat()}</lastmod></url>'
        )
    lines.append('</urlset>')
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def strip_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(re.sub(r"\s+", " ", text)).strip()


def write_feed():
    posts = sorted(ARTICLES.values(), key=lambda a: a["date"], reverse=True)
    now_rfc = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for a in posts:
        parent = "research" if a["kind"] == "research" else "blog"
        url = f'{SITE_URL}{parent}/{a["slug"]}.html'
        pub = datetime.combine(a["date"], datetime.min.time()).strftime(
            "%a, %d %b %Y 00:00:00 +0000"
        )
        summary = html.escape(a["meta_description"])
        items.append(f'''    <item>
      <title>{html.escape(a["title"])}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{pub}</pubDate>
      <category>{html.escape(a["category"])}</category>
      <description>{summary}</description>
    </item>''')

    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Musaed: research and notes</title>
    <link>{SITE_URL}</link>
    <atom:link href="{SITE_URL}feed.xml" rel="self" type="application/rss+xml" />
    <description>Reverse engineering, Windows internals, and anti-cheat research.</description>
    <language>en</language>
    <lastBuildDate>{now_rfc}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
'''
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")


def write_robots():
    txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}sitemap.xml
"""
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")

# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"wrote {path}")


def main():
    write("index.html",    render_home())
    write("about.html",    render_about())
    write("research.html", render_research_index())
    write("projects.html", render_projects())
    write("blog.html",     render_blog_index())
    write("contact.html",  render_contact())
    write("404.html",      render_404())

    for a in ARTICLES.values():
        parent = "research" if a["kind"] == "research" else "blog"
        write(f'{parent}/{a["slug"]}.html', render_article(a))

    write_sitemap()
    write_feed()
    write_robots()
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print("wrote sitemap.xml, feed.xml, robots.txt, .nojekyll")


if __name__ == "__main__":
    main()
