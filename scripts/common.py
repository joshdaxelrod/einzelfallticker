"""Shared settings and helpers for every step. You shouldn't need to edit this."""

import csv
import time
from pathlib import Path

import requests

# Everything is saved relative to the repo folder, wherever you put it.
REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output"
OUTPUT.mkdir(exist_ok=True)

PINS_CSV = OUTPUT / "1_pins.csv"
SOURCES_CSV = OUTPUT / "2_sources.csv"
RELEASES_CSV = OUTPUT / "3_releases.csv"
TRANSLATED_CSV = OUTPUT / "4_releases_english.csv"
RESULTS_CSV = OUTPUT / "5_results.csv"
KEYWORDS_TXT = REPO / "keywords.txt"

# Wait this many seconds between requests, so we don't hammer anyone's server.
PAUSE_SECONDS = 1

HEADERS = {"User-Agent": "Mozilla/5.0 (research script; einzelfallticker walkthrough)"}


def fetch(url, timeout=20):
    """Download a web page and return its HTML, or None if it fails."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        print(f"   could not load {url}: {error}")
        return None
    finally:
        time.sleep(PAUSE_SECONDS)


def read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, columns):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path, row, columns):
    """Add one row to a CSV, so a long run can be stopped and picked up later."""
    new_file = not Path(path).exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def require(path, step):
    if not Path(path).exists():
        raise SystemExit(f"Can't find {Path(path).name}. Run step {step} first.")
