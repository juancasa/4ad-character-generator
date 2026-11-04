"""Smoke test for index.html. Run: python3 tests/smoke.py"""
import pathlib, sys
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(__file__).resolve().parent.parent / "index.html"
CLASSES = ['warrior','barbarian','dwarf','elf','cleric','rogue','wizard','halfling','acrobat','assassin',
           'bulwark','druid','gnome','illusionist','kukla','gladiator','monk','paladin','ranger','swashbuckler']

def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 1600})
        pg.on('pageerror', lambda e: errors.append(str(e)))
        pg.goto(PAGE.as_uri()); pg.wait_for_timeout(300)
        pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)

        for _ in range(10): pg.click('#rollParty')
        for cid in CLASSES:
            pg.select_option('select[data-act=cls][data-i="0"]', cid)
            for _ in range(5): pg.click('button[data-act=lvup][data-i="0"]')
            for _ in range(5): pg.click('button[data-act=lvdown][data-i="0"]')

        pg.select_option('select[data-act=cls][data-i="2"]', 'warrior')
        pg.check('#freeGear')
        pg.click('details.shop[data-i="2"] summary')
        pg.click('details.shop[data-i="2"] button[data-id="bow"]')
        pg.select_option('#pet2', 'warhound')
        pg.check('input[data-act=dogarmor][data-i="2"]')
        pg.select_option('#mount2', 'warhorse')
        pg.uncheck('#freeGear')
        pg.click('details.shop[data-i="2"] button[data-id="rope"]')

        for sysv in ['classical', 'slowsure', 'oldschool', 'slower']:
            pg.select_option('#xpSystem', sysv)
        pg.select_option('#xpSystem', 'classical')
        for _ in range(3):
            btn = pg.query_selector('button[data-act=xproll]:not([disabled])')
            if btn: btn.click()
        pg.click('#encPlus')

        # play tracking: Life, Madness, Clues
        for _ in range(3): pg.click('button[data-act=hpdown][data-i="1"]')
        pg.click('button[data-act=hpup][data-i="1"]')
        for _ in range(4): pg.click('button[data-act=madup][data-i="1"]')
        pg.click('button[data-act=maddown][data-i="1"]')
        for _ in range(3): pg.click('button[data-act=clueup][data-i="1"]')
        snap = "(()=>{const h=party[1];return {hp:curLife(h),max:maxLife(h),mad:h.madness,clues:h.clues}})()"
        st = pg.evaluate(snap)
        assert st['max'] - st['hp'] == 2 and st['mad'] == 3 and st['clues'] == 3, st
        pg.click('button[data-act=lvup][data-i="1"]')  # wounds stay; max Life rises
        st = pg.evaluate(snap)
        assert st['max'] - st['hp'] == 3, st
        pg.reload(); pg.wait_for_timeout(300)
        st2 = pg.evaluate(snap)
        assert st2 == st, (st, st2)
        md = pg.evaluate("toMarkdown()")
        assert f"**Life:** {st['hp']}/{st['max']}" in md and '**Madness:** 3' in md and '**Clues:** 3' in md, md[:400]
        pg.click('button[data-act=hpfull][data-i="1"]')
        while pg.is_enabled('button[data-act=hpdown][data-i="1"]'): pg.click('button[data-act=hpdown][data-i="1"]')
        assert pg.evaluate("curLife(party[1])") == 0
        pg.click('#copyMd')
        b.close()

    if errors:
        print("FAIL"); [print(" ", e) for e in errors]; sys.exit(1)
    print("OK")

if __name__ == "__main__":
    main()
