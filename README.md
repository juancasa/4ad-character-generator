# 4AD Character Generator

A single-page party builder for **Four Against Darkness** (Expanded Edition) by Andrea Sfiligoi / Ganesha Games.

**Use it online: https://4ad.macondo.info/**

Open `index.html` in a browser — no build step, no server, no dependencies (Google Fonts load if online, with system font fallbacks).

## Features

- **Party of four** — roll a random party or pick any of the 20 classes (core-only toggle). Rare classes (Bulwark, Kukla, Mushroom Monk) are limited to one per party.
- **Character sheets** — Life, Attack per weapon, Defense, Stealth and Saves, calculated from class, level, gear and traits.
- **Starting gear and gold** — gear trade-in options, rolled starting gold and rations, d6 traits (two for halflings), spell slots, Ranger Sworn Enemy.
- **Equipment shop** — the Equipment chapter at book prices, with class restrictions and carry limits. Short heroes borrow from allies. Optional *free equipment* mode.
- **Animal companions** — hawk, owl, peacock, warhound (plus dog armor), wildcat, crow, and a warhorse mount; druids get theirs for 1gp of food.
- **Levelling** — manual level controls plus all four XP systems: Classical, Slow and Sure, Old School tally, and Slower Advancement. Stats, slots and resources scale with level; Tier dice change at L5/10/15/20.
- **Party check** — roles covered, HCL, gold left, rule warnings.
- **Play tracking** — current Life, Madness and Clues on each sheet.
- **Save, export, print** — parties are saved in browser `localStorage`; export/import a party as JSON to back it up or move it to another browser; copy a party as Markdown; print-friendly sheets.

## Notes

- Trait and class-feature text is condensed. Each sheet shows the book page for the full rule.
- The Expanded Edition covers the Basic Tier (L1–4). Expert Tier skills (L5+) are in *Four Against the Abyss*.
- You need a copy of the book to play.

## Hosting

Served by GitHub Pages from the `main` branch (root folder) at **https://4ad.macondo.info/**. The `CNAME` file holds the custom domain; DNS has a CNAME record `4ad.macondo.info → juancasa.github.io`. Every push to `main` redeploys.

Saved parties live in each browser’s `localStorage` for one web address, so use Export/Import JSON to move parties between addresses or browsers.
