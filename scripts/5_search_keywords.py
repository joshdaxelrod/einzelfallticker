"""
Step 5: Search every release for signs of migration.

Reads the word list in keywords.txt and checks each release for any of those
words. Every word also matches longer words that start with it, so "Syria"
also catches "Syrian" and "Syrians".

A match means the release gives the AfD *some* ostensible reason to call it a
migrant crime. No match means the release says nothing at all about the
suspect's nationality, migration status, skin colour or the like.

The search was a loop, not a single run: I read the releases with no match,
and whenever one did mention migration in a way the list missed, I added that
word to keywords.txt and ran the search again. Do the same.

It reads the translated spreadsheet from step 4 (output/4_releases_english.csv),
looking for the English in a column called english_text.

Usage:
    python3 scripts/5_search_keywords.py
    python3 scripts/5_search_keywords.py --file path/to/your_translated_sheet.csv
"""

import argparse
import re

from common import KEYWORDS_TXT, RESULTS_CSV, TRANSLATED_CSV, read_csv, require, write_csv

COLUMNS = ["afd_url", "release_url", "release_title", "published", "police_agency",
           "keyword_found", "matched_words", "matched_sentence"]


def load_keywords(path):
    """One keyword per line. Lines starting with # are notes and get skipped."""
    words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                words.append(line)
    return list(dict.fromkeys(words))  # drop repeats, keep order


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", default=TRANSLATED_CSV, help="the translated spreadsheet, saved as CSV")
    parser.add_argument("--keywords", default=KEYWORDS_TXT, help="a different keyword file")
    args = parser.parse_args()

    require(args.file, 4)
    rows, column = read_csv(args.file), "english_text"
    if rows and column not in rows[0]:
        raise SystemExit(f"No column called {column} in {args.file}. Rename your English column to {column}.")

    words = load_keywords(args.keywords)
    # \b = start of a word; \w* = any ending. So "Afghan" matches "Afghan", "Afghans", "Afghanistan".
    pattern = re.compile("|".join(rf"\b{re.escape(w)}\w*\b" for w in words), re.IGNORECASE)

    for row in rows:
        text = row.get(column, "")
        found = sorted({m.lower() for m in pattern.findall(text)})
        sentence = next((s for s in re.split(r"(?<=[.!?])\s+", text) if pattern.search(s)), "")
        row["keyword_found"] = "yes" if found else "no"
        row["matched_words"] = "; ".join(found)
        row["matched_sentence"] = sentence.strip()

    write_csv(RESULTS_CSV, rows, COLUMNS)
    hits = sum(r["keyword_found"] == "yes" for r in rows)
    misses = len(rows) - hits
    print(f"Searched {len(rows)} releases for {len(words)} keywords.")
    print(f"  {hits:5}  mention migration, nationality or appearance")
    print(f"  {misses:5}  don't ({misses / max(len(rows), 1):.0%})")
    print(f"\nSaved to output/{RESULTS_CSV.name}. Filter keyword_found = no and start reading.")


if __name__ == "__main__":
    main()
