# Run it yourself

[← Back to the walkthrough](../README.md)

This repeats my analysis from start to finish. Expect it to take an
afternoon, mostly spent waiting on downloads and reading cases. You don't
need to know how to code: you'll copy commands into a window, press Return,
and open spreadsheets.

Just want to look at my results? Skip all of this and open
[`data/cases_published.csv`](../data/cases_published.csv) in any spreadsheet
app. See [The data](the-data.md).

## Requirements

These instructions are written for macOS, since that's what I use. The
scripts are plain Python and run the same way on Windows or Linux. Each
macOS step has a matching Windows dropdown right after it.

- **Terminal**: the app where you'll type commands. Open it via
  Applications → Utilities → Terminal, or press `⌘ Space`, type
  "Terminal," and press Return.

  Gray boxes like the one below hold commands. Copy the text, paste it into
  Terminal, and press Return to run it:

  ```bash
  echo "like this"
  ```

  <details>
  <summary>Using Windows instead?</summary>

  Press the Windows key, type **Command Prompt**, and press Enter. That's
  your equivalent of Terminal for every step below.

  </details>

- **Python 3.10 or newer.** Check what you have:

  ```bash
  python3 --version
  ```

  If it says 3.10 or higher, you're set. If it's older or missing,
  download the installer from [python.org](https://www.python.org/downloads/)
  and run it like any other Mac app.

  <details>
  <summary>Using Windows instead?</summary>

  Check with `python --version` (no `3`). If it's older than 3.10 or
  missing, download the installer from
  [python.org](https://www.python.org/downloads/). **On the first install
  screen, check "Add python.exe to PATH,"** or the `python` command won't
  be found afterward.

  Anywhere below that says `python3`, type `python` instead.

  </details>

- **A Google account**, for translating in Google Sheets (step 4).

## Download

**Option 1: Download the ZIP (easiest)**

1. Click the green **Code** button on the
   [main page](https://github.com/joshdaxelrod/einzelfallticker), then
   **Download ZIP**.
2. Find the file in your **Downloads** folder and double-click it to unzip.
   This creates a folder called `einzelfallticker-main`.
3. In Terminal, move into that folder:

   ```bash
   cd ~/Downloads/einzelfallticker-main
   ```

   <details>
   <summary>Using Windows instead?</summary>

   Right-click the downloaded file, choose **Extract All**, then:

   ```bat
   cd %USERPROFILE%\Downloads\einzelfallticker-main
   ```

   </details>

**Option 2: Use git**

```bash
cd ~/Downloads
git clone https://github.com/joshdaxelrod/einzelfallticker.git einzelfallticker-main
cd einzelfallticker-main
```

## Setup (one time only)

Create a private copy of Python just for this project (a "virtual
environment"). It avoids the "externally managed environment" errors newer
Macs throw, and keeps these scripts from using the wrong Python.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

<details>
<summary>Using Windows instead?</summary>

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

</details>

You'll see `(venv)` at the start of the line once it's active. **Every time
you open a new Terminal window**, `cd` into the folder and run
`source venv/bin/activate` again (`venv\Scripts\activate` on Windows)
before running any step.

Everything the scripts make goes into a folder called `output`, which
appears inside the project folder the first time you run step 1.

## Step 1: Get the pins

```bash
python3 scripts/1_get_pins.py
```

This downloads the ticker page and saves every pin to `output/1_pins.csv`.
It takes a few seconds.

**If the AfD has taken the page down or changed it**, find an archived copy
on the [Wayback Machine](https://web.archive.org/web/*/afd.de/einzelfallticker/),
right-click → **View Page Source**, save that as a file (e.g. `ticker.html`
in the project folder), and run:

```bash
python3 scripts/1_get_pins.py --from-file ticker.html
```

## Step 2: Find each pin's source

Try it on 20 posts first, so you can see it working:

```bash
python3 scripts/2_find_sources.py --limit 20
```

Then run the rest:

```bash
python3 scripts/2_find_sources.py
```

This visits every AfD blog post, one per second so it doesn't overload
anyone's server: roughly half an hour. You can stop it at any time with
`Ctrl + C`. Run the same command again and it picks up where it left off.

Results go to `output/2_sources.csv`, one row per pin, with the source link
and whether it's a police press release, news or nothing.

## Step 3: Download the police press releases

```bash
python3 scripts/3_download_releases.py
```

Downloads every presseportal.de release cited by a pin (another 15–20
minutes, also safe to stop and restart). Saves each release's German text,
date and police agency to `output/3_releases.csv`.

## Step 4: Translate in Google Sheets

This is how I did it, with no code.

1. Go to [sheets.new](https://sheets.new) to open a blank Google Sheet.
2. **File → Import → Upload**, and choose `output/3_releases.csv`. Pick
   **Replace current sheet**.
3. The German text is in the column headed `german_text` (column F). In the
   first empty column to its right, type `english_text` in row 1.
4. In row 2 of that new column, paste:

   ```
   =GOOGLETRANSLATE(F2, "de", "en")
   ```

   (If `german_text` isn't in column F, change `F2` to match.)
5. Click that cell, then double-click the small square at its bottom-right
   corner. That copies the formula down every row. Give it a few minutes to
   fill in; Sheets translates a batch at a time.
6. Once every row has English (scroll to the bottom to check), turn the
   formulas into plain text so they don't re-run: select the whole column,
   **Copy**, then **Edit → Paste special → Values only**.
7. **File → Download → Comma-separated values (.csv)**.
8. Rename the downloaded file to `4_releases_english.csv` and move it into
   the `output` folder.

## Step 5: Search for keywords

```bash
python3 scripts/5_search_keywords.py
```

Takes a second. It prints how many releases matched and saves
`output/5_results.csv`, with these columns added:

- `keyword_found`: yes or no
- `matched_words`: which dictionary words it found
- `matched_sentence`: the first sentence containing one, so you can judge
  the match without opening the release

(If you saved the translated sheet somewhere else, point to it with
`--file path/to/file.csv`.)

## Step 6: Read, add words, repeat

1. Open `output/5_results.csv` and filter `keyword_found` to **no**.
2. Read those releases. You can click `release_url` to open each one.
3. Found one that hints at migration in a way the list missed? Open
   [`keywords.txt`](../keywords.txt) in any text editor, add the word on
   its own line, save, and run step 5 again.
4. Repeat until the unmatched cases really do say nothing about the
   suspect's origin.

Reading the matches is worth doing too. Check `matched_sentence` for words
that matched for the wrong reason ("southern Germany," say). Whether you
count those is your editorial call; I kept the search generous so that my
final number would be conservative.

## Troubleshooting

- **`command not found: python3`**: Python isn't installed, or (on
  Windows) wasn't added to PATH. See Requirements.
- **`No module named requests`** (or `bs4`): the virtual environment isn't
  active. Run `source venv/bin/activate` and try again.
- **`Can't find ... Run step N first`**: the steps build on each other.
  Run them in order.
- **Lots of "could not load" lines**: a few are normal (some posts have
  been deleted). If every line fails, the site may be blocking you or down.
  Wait a while and run the step again; it'll retry only what's missing.
