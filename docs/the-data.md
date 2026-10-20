# The data

[← Back to the walkthrough](../README.md)

The [`data`](../data) folder holds the exact files behind the story,
collected in early 2025. All three are CSVs, which open in Excel, Google
Sheets or Numbers.

## [`pins.csv`](../data/pins.csv): every pin on the map

All 1,526 pins on the ticker.

| column | what it is |
|---|---|
| `post_id` | the AfD website's ID for the blog post |
| `date` | the date shown on the pin |
| `title` | the pin's headline, in German, as the AfD wrote it |
| `lat`, `lng` | where the pin sits on the map |
| `afd_url` | the AfD blog post the pin opens |

## [`sources.csv`](../data/sources.csv): where each post got its story

One row per AfD post where I found a source link.

| column | what it is |
|---|---|
| `afd_url` | the AfD blog post |
| `source_url` | the outside link in that post |
| `source_domain` | the website it points to |
| `category` | `police press release` or `news` |

## [`cases_published.csv`](../data/cases_published.csv): the 1,025 cases I analysed

Every case whose source is a police press release on presseportal.de, with
the result of the keyword search. **This is the file behind the story's
numbers:** filter `keyword_found` to `no` and you get the 450.

Each row is a pin. A few press releases are cited by more than one pin, so
they appear more than once.

| column | what it is |
|---|---|
| `afd_url` | the AfD blog post |
| `release_url` | the police press release it cites |
| `release_title` | the release's headline, in German |
| `published` | when police published it |
| `police_agency` | the police agency that wrote it |
| `keyword_found` | `yes` if the release contains any word in [`keywords.txt`](../keywords.txt), `no` if not. A `no` means the release says nothing about migration; it doesn't prove the suspect was German |
| `matched_words` | which words matched |
| `matched_sentence` | the first sentence with a match, in English (Google Translate) |

A few releases have no `published` date or `police_agency`, because the
page didn't follow the usual layout.

## What's not here

- **The full text of the press releases**, in German or English. Those
  belong to the police departments that wrote them, and
  [step 3](run-it-yourself.md#step-3-download-the-police-press-releases)
  downloads them fresh from the links above.
- **The news articles** behind the other third of the pins. I didn't
  analyse them.
- **Interviews and correspondence with police and prosecutors.**

## Using this data

You're welcome to use and build on it, for instance to check a claim about
a specific pin, or to compare against a newer version of the ticker. No
credit needed, but if you do something with it, I'd love to hear about it:
[joshdaxelrod@gmail.com](mailto:joshdaxelrod@gmail.com).
