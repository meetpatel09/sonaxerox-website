#!/usr/bin/env python3
"""Create a new Sona Xerox page the right way — one command, nothing forgotten.

    python3 tools/new_page.py SLUG "English title" "ગુજરાતી શીર્ષક" [--public] [--paper] [--rupee]

What it does (these are the project rules, so they are automated):
  1. creates  <SLUG>/index.html  from tools/templates/page.html
  2. adds its button to /our-tools/            (standing rule: EVERY new page gets a dashboard button)
  3. private by default: adds  <meta name="robots" content="noindex">;
     with --public it is added to sitemap.xml instead
  --paper  use the main-site palette (cream background); default is the tool palette (white)
  --rupee  embed the bundled ₹ glyph (needed on any page that shows prices)
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "tools" / "templates" / "page.html"
RUPEE = ROOT / "tools" / "templates" / "rupee-face.css"

TOKENS = {
    "paper": """    --paper:#FBFAF6; --ink:#161616; --cyan:#00A3C4; --magenta:#E0218A; --yellow:#FFC400; --gray:#6F6F68; --line:#E4E2D9;
    --display:"Bricolage Grotesque","Hind Vadodara",sans-serif;
    --body:"Archivo","Hind Vadodara",sans-serif;
    --gu:"Hind Vadodara","Archivo",sans-serif;""",
    "tool": """    --paper:#FFFFFF; --ink:#161513; --cyan:#00AEEF; --magenta:#EC008C; --yellow:#F5C400; --gray:#726F68; --line:#DEDCD5;
    --display:"Archivo Black","Hind Vadodara",sans-serif;
    --body:"Work Sans","Hind Vadodara",sans-serif;
    --gu:"Hind Vadodara","Work Sans",sans-serif;""",
}
DEFAULT_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="7" height="7" rx="1.5"/>'
                '<rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/>'
                '<rect x="13" y="13" width="7" height="7" rx="1.5"/></svg>')


def add_dashboard_button(slug, title_en, title_gu, icon=DEFAULT_ICON):
    path = ROOT / "our-tools" / "index.html"
    html = path.read_text(encoding="utf-8")
    href = f'href="/{slug}/"'
    if href in html:
        return False
    li = f"""    <li>
      <a class="tool" {href}>
        <span class="ico">{icon}</span>
        <span class="txt">
          <span class="name" data-gu="{title_gu}" data-en="{title_en}">{title_gu}</span>
          <span class="path">sonaxerox.in/{slug}/</span>
        </span>
        <span class="go" aria-hidden="true">→</span>
      </a>
    </li>
"""
    new, n = re.subn(r"(</li>\s*\n)(\s*</ul>)", lambda m: m.group(1) + li + m.group(2), html, count=1)
    if n != 1:
        sys.exit("Could not find the tools list (</ul>) in our-tools/index.html")
    path.write_text(new, encoding="utf-8")
    return True


def add_to_sitemap(slug):
    path = ROOT / "sitemap.xml"
    xml = path.read_text(encoding="utf-8")
    loc = f"https://sonaxerox.in/{slug}/"
    if loc in xml:
        return False
    entry = f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
    path.write_text(xml.replace("</urlset>", entry + "</urlset>"), encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug"); ap.add_argument("title_en"); ap.add_argument("title_gu")
    ap.add_argument("--public", action="store_true"); ap.add_argument("--paper", action="store_true"); ap.add_argument("--rupee", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.slug):
        sys.exit("slug must be lowercase letters, digits and hyphens, e.g. photo-resizer")
    target = ROOT / a.slug / "index.html"
    if target.exists():
        sys.exit(f"{a.slug}/index.html already exists — nothing changed")
    esc = lambda t: t.replace("&", "&amp;").replace('"', "&quot;")
    html = TEMPLATE.read_text(encoding="utf-8")
    html = (html.replace("{{TITLE_EN}}", esc(a.title_en)).replace("{{TITLE_GU}}", esc(a.title_gu))
                .replace("{{TOKENS}}", TOKENS["paper" if a.paper else "tool"])
                .replace("{{ROBOTS}}", "" if a.public else '<meta name="robots" content="noindex">\n')
                .replace("{{RUPEE_CSS}}", (RUPEE.read_text(encoding="utf-8") + "\n") if a.rupee else ""))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print(f"created  {a.slug}/index.html")
    print("added    dashboard button in our-tools/" if add_dashboard_button(a.slug, esc(a.title_en), esc(a.title_gu)) else "exists   dashboard button")
    if a.public:
        print("added    sitemap.xml entry" if add_to_sitemap(a.slug) else "exists   sitemap entry")
    else:
        print("private  noindex added (not in sitemap)")
    print("\nNext: build the page, run `python3 tests/run_all.py`, open a pull request.")


if __name__ == "__main__":
    main()
