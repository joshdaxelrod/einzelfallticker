# How I fact-checked the AfD's "Einzelfallticker"

The Einzelfallticker ("individual case ticker") was a map the far-right
Alternative for Germany (AfD) promoted as a record of crimes committed by
migrants. Most of its pins cite a police press release as their source,
usually one published on presseportal.de, where many German police
departments post their bulletins. I checked the pins against those
releases. In 450 of the 1,025 cases backed by a police release (44%), the
release says nothing about the suspect's nationality, migration status or
appearance.

This repo has the data and code behind the analysis.

- Story: [The far-right lies to you about migrant crime, again](https://europeancorrespondent.com/en/r/the-farright-lies-to-you-about-migrant-crime-again), *The European Correspondent*, 7 May 2026
- The data: [every case and how it was coded](docs/the-data.md)
- Keyword list: [`keywords.txt`](keywords.txt)
- To rerun the analysis: [step-by-step instructions](docs/run-it-yourself.md), no coding experience needed

## Two examples

A pin in Berlin-Spandau reads *Berlin: "Männer" stoßen 81-Jährigen in
S-Bahn-Gleisbett* ("'Men' push 81-year-old into S-Bahn track bed"). The
quotation marks around "men" are the AfD's. The blog post behind the pin
cites a [federal police press release](https://www.presseportal.de/blaulicht/pm/70238/5684595)
about two unknown men who argued with an 81-year-old at Spandau station,
pushed him onto the tracks and ran. The only nationality mentioned is the
victim's: German. There's nothing about the attackers. The Berlin
prosecutor's office later confirmed they were German citizens, born in
Germany. This case is one of the 450.

A pin in Mettmann, near Düsseldorf, reads *Mettmann: Südländer überfällt
Lebensmittelgeschäft* ("Southerner robs grocery store"). The
[police release](https://www.presseportal.de/blaulicht/pm/43777/5792261)
describes the robber as male, 20 to 25, about 1.70 metres tall, wearing a
black hoodie and cap, with a "southern appearance." That phrase is common in
German police descriptions, and it's the only hint about where he might be
from. It says nothing about his nationality, but I counted the case as a
match because it gives the AfD some basis for the pin.

## The numbers

| | cases |
|---|---:|
| Pins on the map | 1,526 |
| Pins citing a police press release on presseportal.de | 1,025 |
| Releases with no migration-related keywords | 450 |

## Method

### 0. Finding the map

I found the map through an AfD Facebook ad from June 2024 that was viewed
nearly a million times
([Meta Ad Library](https://www.facebook.com/ads/library/?id=459185823423059)).
The idea to look through the party's ads came from Bellingcat's
[guide to tracking election ad spending on Facebook and Instagram](https://www.bellingcat.com/resources/2024/11/04/us-presidential-election-trump-harris-meta-ads/).
Hat tip to Bellingcat for that, and for its commitment to open-sourcing its
methods.

### 1. Getting the pins

The map was an OpenStreetMap widget on afd.de. Its data isn't loaded from
anywhere hidden: every pin is written into the page's HTML as a single list
called `oum_all_locations`, with the title, date, coordinates and a link to
the pin's blog post. I saved the page source and extracted that list.
Archived copies of the map are on the
[Wayback Machine](https://web.archive.org/web/2025*/afd.de/einzelfallticker*).
([`scripts/1_get_pins.py`](scripts/1_get_pins.py))

### 2. Finding each pin's source

Nearly every blog post links to one outside source. A script visited each
post and saved that link. Most were police press releases; the rest were
mainly news articles, many from Bild.

I limited the analysis to police releases on
[presseportal.de](https://www.presseportal.de/blaulicht/). They all share
one format and come directly from the police. News articles differ from
outlet to outlet and are often behind paywalls.
([`scripts/2_find_sources.py`](scripts/2_find_sources.py),
[`scripts/3_download_releases.py`](scripts/3_download_releases.py))

### 3. Translating and searching

I translated the releases into English in Google Sheets using the
`GOOGLETRANSLATE` formula
([instructions](docs/run-it-yourself.md#step-4-translate-in-google-sheets)), then searched them for 184 words and phrases
that could indicate a suspect wasn't German:

| Category | Terms | Examples |
|---|---:|---|
| Nationalities, countries and regions | 128 | Syrian, Afghan, Balkan, Eastern European |
| Migration and residence status, and language | 37 | asylum, deport, initial reception center, broken German |
| Appearance and other descriptors | 19 | southern appearance, dark complexion, black beard |

Each term also matches longer words that start with it, so "Syria" matches
"Syrian" and "Syrians."

The search is meant to be generous. A match doesn't mean the suspect was a
migrant, only that the release contains something the AfD could point to,
even if it's just "southern appearance." The 450 cases without a match are
the ones where the release contains nothing of the kind.
([`scripts/5_search_keywords.py`](scripts/5_search_keywords.py))

### 4. Checking the results by hand

I manually validated most of the releases that didn't match. When one
mentioned migration in a way the list didn't cover, I added the missing
term and ran the search again. Most of the additions were nationalities I
had left out the first time. In the final rounds, adding terms such as
"French," "Italian," "Lithuanian" and "does not speak German" moved 20
cases from no match to match.

## Limitations

- The search errs toward finding matches. Words like "southern" or
  "national" occasionally match for unrelated reasons ("southern Germany"),
  and each of those moves a case out of the 450, not into it.
- A release that doesn't mention migration doesn't prove the suspect was
  German. It means the AfD's own source gives no reason to call it a
  migrant crime. Establishing who a suspect was requires asking the
  authorities, as in the Berlin case above.
- The analysis covers police releases only, not the cases sourced to news
  articles.
- The data in this repo was collected in early 2025. Rerunning the scripts
  will pull the ticker and translations as they are now, so results will be
  close to mine but not identical. The files in [`data`](data) are the ones
  behind this analysis.

## How I used AI

- AI (Claude Opus 5.5) helped write the scripts in this repo.
- It didn't make any editorial decisions. I chose which cases to analyse,
  built the keyword list and checked the unmatched cases by hand.
- No case was classified by AI. The search is a plain keyword match and
  gives the same result every time.
- The releases were translated with Google Translate.
- Running the search script on my translated releases gives the same
  result for every case as the published data.

## Using this elsewhere

- Meta's [Ad Library](https://www.facebook.com/ads/library/) is a good way
  to find what a party is promoting. Search a page's ads and follow the
  links.
- Many web maps embed their full dataset in the page the way this one did.
  Searching the page source for `lat` or `lng` is a quick way to check.
- The keyword search will work on any collection of police releases. Edit
  [`keywords.txt`](keywords.txt) and point the scripts at different data.
- If you build on this, I'd love to hear about it:
  [joshdaxelrod@gmail.com](mailto:joshdaxelrod@gmail.com).

---

By [Josh Axelrod](https://josh-axelrod.com). Code is under the [MIT License](LICENSE). The data is public domain ([CC0](https://creativecommons.org/publicdomain/zero/1.0/)).
