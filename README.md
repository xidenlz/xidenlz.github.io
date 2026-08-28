# xidenlz.github.io

Source for [xidenlz.github.io/xidenlz](https://xidenlz.github.io/xidenlz/) —
my personal site and research archive. Reverse engineering, Windows
internals, and anti-cheat notes.

## Layout

```
index.html      about.html      research.html      projects.html
blog.html       contact.html    404.html

research/       long-form write-ups
blog/           shorter notes

css/style.css   design system
js/main.js      nav, TOC, code copy, reading progress
assets/         favicon, diagrams, OG cards
tools/          the static-site generator
```

## Build

Static site. HTML is generated from Python content modules under `tools/`.

```
py tools/build.py       # rewrite all HTML + sitemap + feed
py tools/og.py          # regenerate OG social cards
```

`build.py` is idempotent — run it after editing anything in `tools/` and
commit the resulting HTML.

Requires Pillow for the OG card step:

```
pip install pillow
```

Serve locally:

```
py -m http.server 8000
```

## Adding a post

1. Add the body to `tools/articles.py` (`ARTICLE_BODIES`).
2. Add the metadata entry to `tools/pages.py` (`ARTICLES`).
3. `py tools/build.py && py tools/og.py`.

## Contact

Email: uint64_t@hotmail.com &nbsp;·&nbsp; Discord: `xdenlz`
