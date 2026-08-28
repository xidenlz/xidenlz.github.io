"""
Generate OG social cards under assets/og/.

Each card is 1200x630 PNG, dark background, cyan accent, matching the site
style. Runs with the Windows-shipped Consolas + Segoe UI so it doesn't need
any downloaded fonts.

    py tools/og.py
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from pages import ARTICLES, PROJECTS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og"

W, H = 1200, 630
BG = (10, 11, 13)
BG_RAISED = (16, 18, 22)
LINE = (28, 31, 38)
LINE_STRONG = (42, 47, 57)
INK = (230, 232, 236)
INK_DIM = (154, 161, 173)
INK_FAINT = (106, 114, 128)
ACCENT = (56, 189, 248)

FONTS = [
    r"C:\Windows\Fonts\segoeuib.ttf",   # Segoe UI Bold — title
    r"C:\Windows\Fonts\segoeui.ttf",    # Segoe UI — body
    r"C:\Windows\Fonts\consola.ttf",    # Consolas — kicker/mono
    r"C:\Windows\Fonts\consolab.ttf",   # Consolas Bold — wordmark
]


def font(idx, size):
    try:
        return ImageFont.truetype(FONTS[idx], size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, ft, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = f"{current} {w}".strip()
        wpx = draw.textlength(trial, font=ft)
        if wpx <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def make_card(path, kicker, title, subtitle, footer=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # subtle inset background band
    d.rectangle([(0, H - 90), (W, H)], fill=BG_RAISED)
    d.line([(0, H - 90), (W, H - 90)], fill=LINE, width=1)

    # accent bar top-left
    d.rectangle([(80, 80), (84, 260)], fill=ACCENT)

    padding = 110

    # wordmark
    wm_font = font(3, 30)
    d.text((padding, 80), "Musaed", fill=INK, font=wm_font)
    slash_w = d.textlength("Musaed ", font=wm_font)
    d.text((padding + slash_w, 80), "</>", fill=ACCENT, font=wm_font)

    # kicker
    kicker_font = font(2, 24)
    d.text((padding, 160), kicker.upper(), fill=ACCENT, font=kicker_font)

    # title
    max_title_w = W - padding * 2
    for size in (78, 68, 60, 52, 46):
        title_font = font(0, size)
        lines = wrap(d, title, title_font, max_title_w)
        if len(lines) <= 3:
            break

    y = 210
    for line in lines:
        d.text((padding, y), line, fill=INK, font=title_font)
        y += int(size * 1.1)

    # subtitle
    if subtitle:
        sub_font = font(1, 26)
        sub_lines = wrap(d, subtitle, sub_font, max_title_w)[:2]
        y = min(y + 12, H - 200)
        for line in sub_lines:
            d.text((padding, y), line, fill=INK_DIM, font=sub_font)
            y += 34

    # footer
    footer_font = font(2, 20)
    d.text((padding, H - 60), (footer or "xidenlz.github.io/xidenlz").upper(),
           fill=INK_FAINT, font=footer_font)

    img.save(path, "PNG", optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    make_card(OUT / "home.png",
              "Security · Low-level",
              "Musaed",
              "Reverse engineering, Windows internals, and anti-cheat research.")

    make_card(OUT / "about.png",
              "About",
              "CS student. I read binaries.",
              "KFU · Graduating February 2027")

    make_card(OUT / "research.png",
              "Research",
              "Long-form write-ups.",
              "Kernel-level, anti-cheat, and Windows internals.")

    make_card(OUT / "projects.png",
              "Projects",
              "Injection, hooking, triage.",
              "Framework code and reverse-engineering tools.")

    make_card(OUT / "blog.png",
              "Blog",
              "Short notes and findings.",
              "Reverse engineering, kernel work, malware triage.")

    make_card(OUT / "contact.png",
              "Contact",
              "Email, GitHub, Discord.",
              "Open for internships and research collaboration.")

    make_card(OUT / "404.png",
              "404",
              "Nothing at that offset.",
              "This URL doesn't resolve to a page on the site.")

    for a in ARTICLES.values():
        parent = "research" if a["kind"] == "research" else "blog"
        path = OUT / f'{parent}-{a["slug"]}.png'
        make_card(path, a["category"], a["title"], None,
                  footer=f'{parent}  ·  {a["date_display"]}')

    print(f"wrote {len(list(OUT.glob('*.png')))} cards to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
