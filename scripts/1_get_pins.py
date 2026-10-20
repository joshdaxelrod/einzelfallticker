"""
Step 1: Get every pin on the Einzelfallticker map.

The map is an OpenStreetMap widget (a WordPress plugin called Open User Map).
The widget doesn't load its pins from anywhere fancy: they're all written into
the page's HTML as one big list called `oum_all_locations`. This script finds
that list and saves each pin as a row in a spreadsheet.

Usage:
    python3 scripts/1_get_pins.py
    python3 scripts/1_get_pins.py --from-file saved_page.html   # use a page you saved yourself
"""

import argparse
import json
import re
from html import unescape

from common import PINS_CSV, fetch, write_csv

TICKER_URL = "https://www.afd.de/einzelfallticker/"
COLUMNS = ["post_id", "date", "title", "lat", "lng", "afd_url"]


def find_pin_list(html):
    match = re.search(r"var oum_all_locations\s*=\s*(\[[\s\S]*?\]);", html)
    if not match:
        raise SystemExit(
            "Couldn't find the map data (oum_all_locations) in the page. "
            "The AfD may have changed or taken down the page. "
            "Try an archived copy and pass it with --from-file."
        )
    return json.loads(match.group(1))


def date_and_slug(content):
    """Each pin carries its date and the last part of its blog post's address.

    In early 2025 these sat in little bits of HTML; later versions of the map
    plugin store them as plain text: "28. Januar 2025 <title> <address>".
    """
    date = re.search(r'oum_location_date">([^<]+)<', content)
    slug = re.search(r'<div style="display: none">([^<]+)</div>', content)
    if date or slug:
        return (date.group(1).strip() if date else ""), (slug.group(1).strip() if slug else "")
    text = unescape(content).strip()
    date = re.match(r"\d{1,2}\. \w+ \d{4}", text)
    last_word = text.split()[-1] if text else ""
    slug = last_word if re.fullmatch(r"[a-z0-9-]+", last_word) and "-" in last_word else ""
    return (date.group(0) if date else ""), slug


def tidy(pin):
    date, slug = date_and_slug(pin.get("content", ""))
    if slug:
        afd_url = f"https://www.afd.de/{slug}"
    elif pin.get("post_id"):
        afd_url = f"https://www.afd.de/?p={pin['post_id']}"  # WordPress forwards this to the post
    else:
        afd_url = ""
    return {
        "post_id": pin.get("post_id", ""),
        "date": date,
        "title": unescape(pin.get("title", "")),
        "lat": pin.get("lat", ""),
        "lng": pin.get("lng", ""),
        "afd_url": afd_url,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-file", help="a saved copy of the ticker page's HTML")
    args = parser.parse_args()

    if args.from_file:
        with open(args.from_file, encoding="utf-8") as f:
            html = f.read()
    else:
        print(f"Downloading {TICKER_URL} ...")
        html = fetch(TICKER_URL)
        if html is None:
            raise SystemExit("Couldn't download the ticker page.")

    pins = [tidy(pin) for pin in find_pin_list(html)]
    write_csv(PINS_CSV, pins, COLUMNS)

    missing = sum(1 for p in pins if not p["afd_url"])
    print(f"Saved {len(pins)} pins to output/{PINS_CSV.name}")
    if missing:
        print(f"({missing} pins had no blog post address)")


if __name__ == "__main__":
    main()
