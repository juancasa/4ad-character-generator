"""Smoke test for index.html. Run: python3 tests/smoke.py"""
import json, pathlib, sys
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

        # assassin picks any two starting weapons
        pg.select_option('select[data-act=cls][data-i="3"]', 'assassin')
        pg.select_option('select[data-act=gearpick][data-i="3"][data-p="0"]', 'two')
        pg.select_option('select[data-act=gearpick][data-i="3"][data-p="1"]', 'rifle')
        names = pg.evaluate("kitItems(party[3]).map(x=>x.n)")
        assert 'Two-handed weapon' in names and 'Black powder rifle' in names, names
        # old save with gear index 1 (hand weapon + bow) upgrades to picks
        assert pg.evaluate("upgrade({cls:'assassin',gear:1}).picks.join()") == 'hand,bow'
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

        # printed party sheet: every class at L1/L5/L20 renders, no card overflows, one Letter page
        over = pg.evaluate('''(()=>{ const bad=[]; const keep=party;
          for(const id of CLASSES.map(c=>c.id)) for(const L of [1,5,20]){
            party=[0,1,2,3].map(()=>{const h=newHero(id); h.L=L; fillSpells(h,true); return h;});
            renderPrint(); const ps=document.getElementById('printSheet'); ps.style.display='flex';
            ps.querySelectorAll('.ps-body').forEach(b=>{ if(b.scrollHeight>b.clientHeight+1) bad.push(id+' L'+L); });
            ps.style.display=''; }
          party=keep; return bad; })()''')
        assert not over, over
        pg.emulate_media(media='print')
        pdf = pg.pdf(prefer_css_page_size=True, print_background=True)
        assert pdf.count(b'/Type /Page') - pdf.count(b'/Type /Pages') == 1, 'print should be one page'
        pg.emulate_media(media='screen')

        # JSON export -> import round trip
        before = pg.evaluate("JSON.stringify(party.map(h=>[h.cls,h.name,h.L,h.gold,h.bought,h.hp,h.madness,h.clues,h.spells,h.picks||null]))")
        with pg.expect_download() as dl: pg.click('#exportJson')
        path = dl.value.path(); data = json.loads(pathlib.Path(path).read_text())
        assert data['app'] == '4ad-party-builder' and len(data['party']) == 4, data.keys()
        pg.click('#rollParty')
        pg.set_input_files('#importFile', path); pg.wait_for_timeout(300)
        after = pg.evaluate("JSON.stringify(party.map(h=>[h.cls,h.name,h.L,h.gold,h.bought,h.hp,h.madness,h.clues,h.spells,h.picks||null]))")
        assert before == after, (before, after)
        assert pg.evaluate("(load(ROSTER)||[]).length") >= 1
        # hostile / broken files are rejected or cleaned, never crash
        bad = pathlib.Path(path).with_name('bad.json')
        for txt in ['not json', '{"party":[1,2]}', json.dumps({'party':[{'cls':'warrior','name':'<img src=x onerror=alert(1)>','bought':['nope'],'pet':'dragon','L':99,'traits':[9]}]*4})]:
            bad.write_text(txt); pg.set_input_files('#importFile', str(bad)); pg.wait_for_timeout(200)
        assert pg.evaluate("party[0].L") == 20 and pg.evaluate("party[0].pet") is None
        assert pg.query_selector('#sheets img') is None
        b.close()

    if errors:
        print("FAIL"); [print(" ", e) for e in errors]; sys.exit(1)
    print("OK")

if __name__ == "__main__":
    main()
