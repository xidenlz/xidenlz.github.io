# Build

Static site. HTML is generated from Python content modules in this directory.

```
py tools/build.py       # rewrite all HTML + sitemap.xml + feed.xml + robots.txt
py tools/og.py          # regenerate 1200x630 OG social cards
```

`build.py` is idempotent — run it after editing anything under `tools/` and
commit the resulting HTML.

## What lives where

```
tools/build.py      layouts, partials, sitemap + feed generation
tools/pages.py      per-page metadata (titles, subtitles, projects)
tools/articles.py   article body HTML
tools/og.py         social card generator (needs Pillow)
```

## Adding a post

1. Add the body to `articles.py` (`ARTICLE_BODIES`).
2. Add the metadata entry to `pages.py` (`ARTICLES`).
3. `py tools/build.py && py tools/og.py`.

## Local preview

```
py -m http.server 8000
```

Open <http://127.0.0.1:8000>.

## Requirements

Python 3.9+. Pillow for the OG card step:

```
pip install pillow
```
