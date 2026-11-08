# 4AD Character Generator — project guide

A single-file web app (`index.html`) that builds parties of four heroes for **Four Against Darkness, Expanded Edition** (Andrea Sfiligoi, Ganesha Games). No build step, no backend, no dependencies beyond Google Fonts (with fallbacks).

## Source of truth for rules
- The rulebook PDF lives at `rules/Four Against Darkness_ Expanded Edition - Andrea Sfiligoi.pdf` and is **gitignored**: it's a purchased, watermarked copy. Never commit it.
- Extract text with `pdftotext -layout "rules/Four Against Darkness_ Expanded Edition - Andrea Sfiligoi.pdf" /tmp/4ad.txt`, then grep. Useful sections:
  - Characters / classes: pp. 19–66 (each class has a page ref in `CLASSES[].page`)
  - Equipment and prices: pp. 81–88
  - Animal companions: p. 115
  - XP systems and levelling: pp. 117–118
  - Spells: wizard basic list, druid list, illusionist list in the Magic chapter
- **Don't reproduce rules text verbatim.** Trait and feature descriptions are short paraphrases in our own words; each sheet points to the book page. Keep it that way.

## Code layout (all in `index.html`)
Inline `<style>`, then markup, then one `<script>`. Script sections, in order:

1. **Data**
   - `WIZ`, `ELF_SPELLS`, `DRUID_SPELLS`, `ILLU_SPELLS`, `SWORN` — name lists.
   - `W` — base attack modifier by weapon kind (`light −1, hand 0, two +1, bow 0, crossbow +1, sling −1, handgun +2, rifle +3, stars −1`). `RANGED`, `FIRE`.
   - `tierOf(L)` (1–4 Basic, 5–9 Expert, 10–14 Heroic, 15–19 Legendary, 20 Epic), `TIER_DIE`, `half(L)` = floor(L/2).
   - Starting-kit item helpers (`LA`, `HA`, `SH`, `HW`, `LW`, `TW`, `BOW`, …). Item fields: `n` name, `w` weapon kind, `a` armor value, `at` armor type, `s` shield.
   - `SHOP` — grouped shop items `{id,n,p,w?,a?,at?,s?,max?,tag?,needs?,food?,mush?,note?}`. `tag` ∈ `magic|potion|scroll|herbal`.
   - `ANIMALS`, `WARHORSE` — companion stat blocks.
   - `CLASSES` — one object per class (20 total, 8 flagged `core`). Key fields:
     - `life` base (max Life = life + L + trait mods), `gold` (number of d6), `saves`, `page`, `rare`
     - `atk(kind, L, T, itemName)` → class attack bonus for that weapon; `def(L,T)`; `stealth(L,T)` (number or display string)
     - `allow: {ar:[light|heavy|shield], w:[kinds]}` — shop restrictions
     - `gear: [{l:label, i:[items]}]` — starting-kit trade-in options
     - `gearPick: {n, from:[shop ids], def:[ids]}` — free choice of starting weapons (assassin: any two); stored on the hero as `picks[]`
     - `spells: {list, slots(L), single?}` — `single` = one spell in every slot (gnome)
     - `feat(h, L, T)` → array of feature strings with level-scaled numbers
     - `traits: [[name, summary] ×6]`, `traitCount` (halfling = 2)
     - `tmod: {traitIndex: (L,T) => ({life,def,stealth,atkR,atkHand,atkLight,atkSling,atkBow,slots,addItem,allowW})}` — numeric trait effects
     - `uses(h,L,T)` — per-adventure resources for the printed sheet (Rage, Luck, Tricks, prayers…)
     - flags: `food`, `sworn`, `druidPet`, `nomagic`, `artificial`, `nomush`
2. **Helpers** — dice, `sgn` (uses a real minus sign), `esc`, random names.
3. **Hero model**
   - Hero shape: `{cls,name,L,gear,traits[],gold[],food[]|null,spells[],sworn,notes,bought[],free[],goldAdj,pet,petFree,mount,mountFree,dogArmor,dogFree,xp,lastRoll,hp,madness,clues,picks?}`
   - Play tracking: `hp` is current Life, `null` = full (so it follows max Life on level-up); `maxLife`, `curLife`, `setLife`. `madLimit` = L (+1 for classes with `sane:1`, i.e. wizard). `aliveCount` counts heroes above 0 Life.
   - `newHero`, `upgrade` (fills defaults for old saves), `tmods`, `slotCount`, `fillSpells`, `kitItems`, `allItems`, `spent`, `goldLeft`, `foodCount`, `canUse` (returns a reason string or null), `computed` (all derived stats).
   - Gold: `goldLeft = sum(gold dice) + goldAdj − spent`. Borrowing between heroes moves `goldAdj`. Items in `free[]` and animals flagged `*Free` cost nothing.
4. **State** — `party` (4 heroes), `coreOnly`, `meta {xp, minor, last, banked, freeGear}`. Saved to `localStorage` key `4ad-party-v2` (reads `4ad-party-v1` too); roster under `4ad-roster-v1`.
5. **Levels and XP** — four systems: `classical`, `slowsure`, `oldschool`, `slower`. `meta.last` = index of the hero who just levelled up via XP (they can't take the next XP unless they're alone). `TRAINING` gold costs at new Tiers (slower system).
6. **Rendering** — string templates: `sheetHTML`, `xpBox`, `shopHTML`, `boughtHTML`, `petHTML`, `renderCheck` (party-role bar), `renderSettings`, `render(anim)` (keeps open shop `<details>` and scroll position).
7. **Markdown export**, **JSON export/import** (`toJSON`, `fromJSON`, `cleanHero`: imported files are untrusted, so every field is validated against the data and unknown values are dropped; the current party goes to the roster before an import replaces it), **events** (event delegation on `#sheets` via `data-act`), **boot**.

When adding a class rule, prefer extending the data (`atk`, `tmod`, `feat`, `allow`) over special-casing in `computed`.

## Rules decisions already made
- Level range 1–20; the book covers Basic Tier (L1–4). From L5 the sheet notes that Expert skills come from *Four Against the Abyss*. Tier die changes with Tier.
- Best armor counts (light and heavy don't stack); a shield adds +1. Shield and heavy armor each give −1 Stealth.
- Conditional bonuses (cleric vs undead, rogue vs outnumbered Minor Foes, dwarf vs goblins, …) are listed as features, not added to the main numbers.
- Bonuses tied to a specific weapon type the shop doesn’t model (rogue Knife Fighter: daggers; warrior Sword/Mace Training; dwarf Axe Mastery) stay in the trait text and aren’t added to Attack. Kukla’s +1 matches item names (dagger/knife/slashing).
- Weapon lists follow the book strictly: rangers get no crossbows, rogues get no throwing stars.
- Rare classes (Bulwark, Kukla, Mushroom Monk): one per party, enforced in random rolls and warned in the party bar. Two or more dwarves → warning that the party can't Bribe.
- Druid companion costs 1gp; companions above the hero's level can't be chosen.
- Unarmed: −2, except mushroom monk (hands count as light, then hand weapons from L5) and kukla (claws −1).

## Design
Graph-paper "printed form filled in pencil" look.
- Fonts: **Alegreya** for printed labels, **Kalam** for handwritten values.
- Color tokens on `:root` with a dark set under `@media (prefers-color-scheme: dark)` and `[data-theme]`: `--paper --grid --grid-strong --ink --pencil --soft --red --blue --card --line --ok --warn`. Red pencil is used for dice, gold and attack numbers.
- Everything the player chooses looks filled in by pencil: selects are underlined blanks with Kalam values (global `select` style), checkboxes and radios are printed boxes with a pencil tick. Number controls are joined `.step` boxes (− value +).
- Each hero card opens with a dark `.band` like the printed form's card headers: class select, page ref, Reroll, Level stepper. It uses `--ink` as background and `--card` as text, so it flips in dark mode.
- Above the cards, `#partyRoll` shows each hero's Life, Attack and Defense side by side (links to `#hero-i`), followed by the party-mix boxes. File actions (Save, Markdown, JSON, Print) are quiet `.link` buttons in the header; “Roll a new party” is the only primary button.
- Dice render as pip faces (`.die`) with a short tumble animation, disabled under `prefers-reduced-motion`.
- **Print** renders `#printSheet` instead of the app: a one-page US Letter copy of the 4AD party sheet form (`rules/4AD_Party_Sheet_Letter.pdf`, gitignored), filled in by `renderPrint()` on `beforeprint`. Labels in Helvetica/Arial, values in Kalam. Per-adventure resources come from each class’s `uses(h,L,T)` → `[name, uses]` (≤3 → boxes, else a number); “Once per …” traits are detected from their summary text. Overflow from fixed lines goes into Conditions/Notes. The smoke test fails if any class at L1/5/20 overflows a card or the print spills onto a second page.

## Hosting
- GitHub Pages from `main` at https://4ad.macondo.info/ (`CNAME` file; DNS CNAME `4ad` → `juancasa.github.io` at domain.com). Don’t delete `CNAME`. Pushing to `main` deploys.

## Testing
- **All Python runs through pipenv** (`pipenv run …`), never bare `python3`/`pip`. Dependencies live in `Pipfile` / `Pipfile.lock`; the virtualenv is `.venv/` in the project (gitignored). Add packages with `pipenv install [--dev] <pkg>`.
- `pipenv run python tests/smoke.py` runs a Playwright smoke test: it cycles every class through levels, buys gear, adds companions, uses each XP system and toggles free equipment, failing on any page error.
- Setup: `PIPENV_VENV_IN_PROJECT=1 pipenv install --dev && pipenv run playwright install chromium`.
- Run it after every change, and open `index.html` in a browser for a visual check.

## Conventions
- Keep it one self-contained `index.html` unless we decide otherwise.
- User-facing text uses typographic quotes and apostrophes (’ “ ”) and real minus signs (−) for modifiers.
- Commit messages: short imperative summary, e.g. `Add equipment shop`.

## Ideas not yet built
- Import a party from Markdown.
- More XP automation (Major Foes, Secrets, Final Boss counters).
