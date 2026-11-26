# The World Today — 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/dracximer-sys/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/dracximer-sys/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

**Entry for the make.fun bounty "Sum up 26 November's world news in one image"**
(slug: `news-image-20261126` — $100 total, 50 places, closes 28 Nov 2026 07:00 WIB).

One 1024×1024 newspaper front page, built by **@drac-ximer**:

- **32 stories** that happened on, or were first reported on, **Thursday 26 November 2026** — a fuel tanker fire in Cairo that killed 31, Kim Jong Un ordering wider tactical nuclear weapons deployment, Wall Street's wild Wednesday ahead of Thanksgiving, and 29 more from every region.
- **THE DAY IN NUMBERS** — six figures from the day (31 killed in the Cairo tanker fire; Brent crude at $94.69, up 3.60% as Hormuz stays shut; the Bank of Korea base rate at 3.25%; 96 Peru ports closed by El Niño swells; 100 inflatables in Macy's 100th Thanksgiving Day Parade; 81.5 million Americans travelling for Thanksgiving week).
- **A world map with 11 numbered pins** and a pin key, from Giza to Geneva.
- **A DATE CHECK box** naming look-alike stories from other dates that were deliberately left out (the PIF Tower drone strike, 24 Nov; Australia's Digital Duty of Care, 25 Nov; Bangladesh's garment minimum wage rise, 25 Nov; the Trump Thanksgiving proclamation, 24 Nov; the EU "End the Cage Age" ruling, 25 Nov; ESA's Hera mission crater images, 25 Nov; Melania Trump reuniting 9 more children, 25 Nov; the US Army Iowa lead azide detonation, 25 Nov).

## How it runs

```sh
python3 main.py
```

`main.py` is **Python 3, standard library only** — no network, no dependencies.
It writes the image to `$MAKEFUN_OUTPUT_DIR/entry.png` (falling back to
`/output/entry.png`, then to the script's own directory for local runs).
The front page is embedded as base64 in one line, so two runs produce
byte-identical output. A pure-stdlib fallback draws a minimal title page if
the embedded data ever failed to decode, so the program still exits 0.

## Build

The page was composed locally with Pillow (`render_26nov.py`, build-time only —
the graded program is stdlib-only) from research in `research/stories-20261126.md`,
verified against Reuters, AP, CNN, BBC, Al Jazeera, The Times, Yonhap, UEFA,
FIDE, ChessBase, AAA and others. The three top-story illustrations (a fuel
tanker on fire on the Giza Ring Road, a North Korean nuclear facility, Wall
Street's plunging-then-recovering market line) are drawn with code —
original art, no photos.

## License

MIT — see [LICENSE](LICENSE).
