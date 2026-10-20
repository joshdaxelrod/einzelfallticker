"""
Step 3: Download the police press releases.

About two-thirds of the pins cite a police press release on presseportal.de,
the platform German police use to publish their bulletins. Those pages all
share one layout, which makes them easy to read in bulk, so they're the set
I analysed. This script downloads the text of each one, plus its publication
date and the police agency that wrote it.

Like step 2, it can be stopped and restarted.

Usage:
    python3 scripts/3_download_releases.py
    python3 scripts/3_download_releases.py --limit 20
"""

import argparse
import re

from bs4 import BeautifulSoup

from common import RELEASES_CSV, SOURCES_CSV, append_csv, fetch, read_csv, require

COLUMNS = ["afd_url", "release_url", "release_title", "published", "police_agency", "german_text"]


def read_release(html):
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article", class_="story") or soup.find("article")
    if article is None:
        return "", ""
    title = article.find("h1").get_text(strip=True) if article.find("h1") else ""
    lines = []
    for tag in article.find_all(["p", "pre"]):
        if tag.name == "pre":  # lists of suspect descriptions are often in <pre> blocks
            lines += [f"- {l.strip(' •-')}" for l in tag.get_text().splitlines() if l.strip()]
        elif tag.get_text(strip=True):
            lines.append(tag.get_text(strip=True))
    return title, "\n".join(lines)


def published(text):
    """presseportal stamps each release like '10.01.2025 – 14:25'."""
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})\s*[–-]\s*(\d{2}):(\d{2})", text)
    return f"{m[3]}-{m[2]}-{m[1]} {m[4]}:{m[5]}" if m else ""


def agency(text):
    """Each release ends with 'Original-Content von: <agency>, übermittelt durch news aktuell'."""
    m = re.search(r"Original-Content von:\s*([^,]+),\s+übermittelt durch", text)
    return m.group(1).strip() if m else ""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, help="only do this many releases (for testing)")
    args = parser.parse_args()

    require(SOURCES_CSV, 2)
    cases = [r for r in read_csv(SOURCES_CSV) if "presseportal.de" in r["source_domain"]]
    done = {r["afd_url"] for r in read_csv(RELEASES_CSV)}
    todo = [c for c in cases if c["afd_url"] not in done][: args.limit]
    print(f"{len(cases)} pins cite a presseportal release, {len(done)} already done, {len(todo)} to go.")

    for i, case in enumerate(todo, 1):
        html = fetch(case["source_url"])
        title, text = read_release(html) if html else ("", "")
        append_csv(RELEASES_CSV, {
            "afd_url": case["afd_url"],
            "release_url": case["source_url"],
            "release_title": title,
            "published": published(text),
            "police_agency": agency(text),
            "german_text": text,
        }, COLUMNS)
        print(f"[{i}/{len(todo)}] {title or 'could not read ' + case['source_url']}")

    print(f"\nSaved to output/{RELEASES_CSV.name}")


if __name__ == "__main__":
    main()
