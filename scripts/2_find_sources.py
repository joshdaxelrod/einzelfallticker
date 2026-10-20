"""
Step 2: Find the source behind every pin.

Each pin links to a short AfD blog post, and almost every post links out to
one source: a police press release or a news article. This script opens each
post, grabs that outside link, and sorts it into "police press release",
"news" or "no source found".

This takes a while (about 1,500 pages at one per second, so roughly half an
hour). If it stops, just run it again: it skips posts it has already done.

Usage:
    python3 scripts/2_find_sources.py
    python3 scripts/2_find_sources.py --limit 20     # try it on 20 posts first
"""

import argparse
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from common import PINS_CSV, SOURCES_CSV, append_csv, fetch, read_csv, require

COLUMNS = ["afd_url", "title", "source_url", "source_domain", "category"]

# Links in a post that are never the source (sharing buttons, the party's own sites).
IGNORE = ("afd.de", "facebook.", "twitter.", "x.com", "instagram.", "youtube.",
          "t.me", "telegram.", "tiktok.", "whatsapp.", "linkedin.", "mailto:")


def source_link(html):
    """Return the first outside link inside the post's main text."""
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("article .post-content") or soup.find("article")
    if body is None:
        return ""
    for link in body.find_all("a", href=True):
        href = link["href"].strip()
        if href.startswith("http") and not any(bad in href for bad in IGNORE):
            return href
    return ""


def category(url):
    """Police releases come from presseportal.de's "Blaulicht" section or a police website."""
    if not url:
        return "no source found"
    domain = urlparse(url).netloc.lower()
    if domain == "polizei.news":  # a news site, despite the name
        return "news"
    if "presseportal.de" in domain or "polizei" in domain or "/polizei" in url.lower() \
            or "feuerwehr" in domain or "sachsen-anhalt.de" in domain:
        return "police press release"
    return "news"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, help="only do this many posts (for testing)")
    args = parser.parse_args()

    require(PINS_CSV, 1)
    pins = [p for p in read_csv(PINS_CSV) if p["afd_url"]]
    done = {row["afd_url"] for row in read_csv(SOURCES_CSV)}
    todo = [p for p in pins if p["afd_url"] not in done][: args.limit]
    print(f"{len(pins)} posts, {len(done)} already done, {len(todo)} to go.")

    for i, pin in enumerate(todo, 1):
        url = pin["afd_url"]
        html = fetch(url) or fetch(url + "/")  # some posts only load with a trailing slash
        link = source_link(html) if html else ""
        append_csv(SOURCES_CSV, {
            "afd_url": url,
            "title": pin["title"],
            "source_url": link,
            "source_domain": urlparse(link).netloc if link else "",
            "category": category(link),
        }, COLUMNS)
        print(f"[{i}/{len(todo)}] {link or 'no source found'}")

    rows = read_csv(SOURCES_CSV)
    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    print(f"\nSaved to output/{SOURCES_CSV.name}:")
    for name, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {n:5}  {name}")


if __name__ == "__main__":
    main()
