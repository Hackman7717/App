"""Tests für Version 1.13.0: Symbole statt Erklärtext in der ganzen App.
Aufruf: python3 pwa_113_test.py  (Testkopie der App unter http://127.0.0.1:8765/AppT/, siehe README)"""
import os
import re
import sys
from playwright.sync_api import sync_playwright
from h import T, open_app, S, shot, main_text

OK = []
BAD = []


def check(name, cond, info=''):
    (OK if cond else BAD).append(name + ('' if cond else '  →  ' + str(info)[:600]))


def ev(p, js):
    return p.evaluate('s=>window.__ev(s)', js)


def go(p, js, ms=250):
    ev(p, js)
    p.wait_for_timeout(ms)


def cnt(p, sel):
    return p.locator('#main ' + sel).count()


def fresh(b, when, **kw):
    p = open_app(b, when, **kw)
    ev(p, "act('clearDemo',document.body);act('clearDemo',document.body)")
    go(p, "dayOff=0;render()", 150)
    return p


# Zeichen, die iOS als Emoji zeigen kann oder die früher als Text-Symbol dienten
GLYPHS = re.compile('[★☆✎✓✔▶⏱⚠■●]')


def run():
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--lang=de-DE'], env={**os.environ, 'LANG': 'de_DE.UTF-8', 'LANGUAGE': 'de', 'LC_ALL': 'de_DE.UTF-8'})

        # ---------- A: Symbolsatz ----------
        p = open_app(b, T(2026, 11, 10, 8, 30))
        check('A1 Version 1.13.0', ev(p, 'APPV') == '1.13.0')
        check('A2 Gesichter und Akkus 1–5', ev(p, 'FACE.length') == 5 and ev(p, 'BATT.length') == 5)
        check('A3 Körperkarte für jede Kategorie', ev(p, "CATS.every(c=>CAT_IC[c]&&CAT_IC[c].includes('<svg'))"))
        check('A4 Tageszeit-Symbol je Mahlzeit', ev(p, "SLOTS.every(([k])=>SLOT_IC[k]&&SLOT_IC[k].includes('<svg'))"))
        check('A5 Messfigur je Maß', ev(p, "MEAS.every(([f])=>MEAS_IC[f]&&MEAS_IC[f].includes('<svg'))"))
        guess = ev(p, "['Wasser','Lesen','Kein Zucker','Dehnen','Vitamine','Spazieren','Kein Alkohol','Lernen','Meditieren','Zähne putzen','Früh ins Bett'].map(n=>habIcKey({name:n,kind:'check'}))")
        check('A6 Symbol passend zum Namen', guess == ['drop', 'book', 'candy', 'stretch', 'pill', 'walk', 'glass', 'cap', 'lotus', 'tooth', 'bed'], guess)
        kinds = ev(p, "['check','count','amount','quit'].map(k=>habIcKey({name:'Xyz',kind:k}))")
        check('A7 sonst Symbol nach Art', kinds == ['check', 'tally', 'gauge', 'quit'], kinds)
        check('A8 Abstinenz mit Schrägstrich', 'M3 3l18 18' in ev(p, "habIc({name:'Kein Zucker',kind:'quit'})")
              and 'M3 3l18 18' not in ev(p, "habIc({name:'Wasser',kind:'count'})"))
        check('A9 selbst gewähltes Symbol gewinnt', ev(p, "habIcKey({name:'Wasser',kind:'count',ic:'music'})") == 'music')
        p.context.close()

        # ---------- B: Heute mit Beispieldaten ----------
        p = open_app(b, T(2026, 11, 10, 8, 30), scale=2)
        go(p, "goRoot('heute');render()")
        hd = [x.inner_text() for x in p.locator('#main .pane-h .eyebrow').all()]
        withsvg = p.locator('#main .pane-h .eyebrow > svg:first-child').count()
        check('B1 Karten-Überschriften mit Symbol', withsvg >= 6, (withsvg, hd))
        cd = p.locator('#main .cidone')
        check('B2 Check-in erledigt: Werte statt Text', cd.count() == 1 and cd.locator('.cdv').count() >= 2 and ' h' in cd.inner_text()
              and 'ERLEDIGT' not in cd.inner_text(), cd.inner_text() if cd.count() else '')
        check('B3 Verlauf und Ändern als Symbol mit Beschriftung für Vorlesen',
              cd.locator('[data-act=goProg] svg').count() == 1 and cd.locator('[data-act=ciEdit] svg').count() == 1
              and 'Verlauf' in (cd.locator('[data-act=goProg]').get_attribute('aria-label') or ''))
        goal = ev(p, 'S.goal||3')
        wd = p.locator('#main .wkl .wdots i')
        on = p.locator('#main .wkl .wdots i.on').count()
        txt = p.locator('#main .wkl').inner_text()
        check('B4 Wochenziel als Kästchen', wd.count() == goal and txt.endswith(f'{on}/{goal}'), (wd.count(), on, txt))
        rows = p.locator('#main .hlist .hrow')
        check('B5 jede Gewohnheit mit Symbol', rows.count() >= 2 and p.locator('#main .hlist .hrow .hic svg').count() == rows.count(), rows.count())
        check('B6 Abhaken ohne „Offen/Erledigt“', 'Offen' not in main_text(p) and 'Erledigt\n' not in main_text(p))
        fc = p.locator('#main .card:has([data-act=goFood])').inner_text()
        check('B7 Ernährung: Balken mit „gegessen“ und „Ziel“, Makros', 'gegessen' in fc and 'Ziel' in fc and p.locator('#main .mrow.mini .mcell').count() == 3, fc)
        check('B8 Körper: Verlauf als Linie und Pfeil', cnt(p, '.wtrend .spark') == 1 and cnt(p, '.wtrend .wtr-d svg') == 1)
        check('B9 Ziele mit Symbol je Art', cnt(p, '.gname svg') >= 2)
        check('B10 Speicherzeile mit Symbolen', cnt(p, '#syncNote .sn svg') == 2)
        ev(p, "store.err=false;setStoreNote()")
        check('B11 Speicherzeile bleibt nach Aktualisierung mit Symbolen', cnt(p, '#syncNote svg') == 2)
        shot(p, 'u_B_heute', full=False)
        # Abends: Check-out mit Gesichtern
        p.clock.set_system_time(T(2026, 11, 10, 19, 5))
        go(p, "render()")
        sc = p.locator('#main .cicard .scale.sc-ic button')
        check('B12 Stimmung als Gesichter', sc.count() == 5 and p.locator('#main .cicard .scale.sc-ic button svg').count() == 5
              and 'Mies' in p.locator('#main .cicard .scale').inner_text())
        sc.nth(3).click()
        p.wait_for_timeout(200)
        check('B13 Stimmung gespeichert', S(p)['days']['2026-11-10'].get('mood') == 4)
        check('B14 Rückmeldung beim Antippen (kurzes Aufspringen)', p.locator('#main [data-act=mood][data-v="4"].tapfx').count() == 1,
              p.locator('#main [data-act=mood][data-v="4"]').get_attribute('class'))
        check('B ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- C: Check-in morgens, frisch ----------
        p = fresh(b, T(2026, 11, 10, 7, 40))
        card = p.locator('#main .cicard')
        check('C1 Aufgestanden und Eingeschlafen mit Sonne und Mond', card.locator('.ci-lt svg').count() == 2, card.inner_text())
        check('C2 kein Erklärtext „Vorschlag antippen“', 'Vorschlag antippen' not in card.inner_text() and 'kein Check-out' not in card.inner_text())
        check('C3 Schlafqualität als Akku', card.locator('.scale.sc-ic button svg').count() == 5)
        p.locator('#main [data-act=ciTSet][data-f=wake]').click()
        p.wait_for_timeout(120)
        p.locator('#main [data-act=ciTSet][data-f=bed]').click()
        p.wait_for_timeout(120)
        res = p.locator('#main .ci-res .slb')
        check('C4 Schlafdauer als Balken mit 7-Stunden-Strich', res.count() == 1 and res.locator('.slb-t i').count() == 1 and res.locator('.slb-t em').count() == 1,
              p.locator('#main .ci-res').inner_text())
        w = res.locator('.slb-t i').evaluate("e=>parseFloat(e.style.width)")
        h = S(p)['days']['2026-11-10']['sleep']['h']
        check('C5 Balkenbreite = Dauer / 10 h', abs(w - h * 10) < 0.11, (w, h))
        p.locator('#main [data-act=sleepQ][data-v="5"]').click()
        p.wait_for_timeout(200)
        row = p.locator('#main .cidone')
        check('C6 eingeklappt mit Dauer und vollem Akku', row.count() == 1 and row.locator('.cdv').count() == 2 and row.locator('.cdv svg path[fill]').count() == 1,
              row.inner_text() if row.count() else '')
        check('C ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- D: Gewohnheiten: Symbol wählen, Arten als Vorschau ----------
        p = fresh(b, T(2026, 11, 10, 12, 0))
        go(p, "S.habits=[];goRoot('heute');render()")
        sg = p.locator('#main .sugg button')
        check('D1 leere Gewohnheiten: Vorlagen mit Symbol, ohne Erklärsatz', sg.count() == 6 and p.locator('#main .sugg button svg').count() == 6
              and 'Alles Kleine' not in main_text(p))
        go(p, "goRoot('ich',['gewohnheiten']);render();act('newHab',document.body)")
        tiles = p.locator('#main .hkinds .ktile')
        check('D2 vier Arten als Kacheln mit Vorschau', tiles.count() == 4 and p.locator('#main .hkinds .pv').count() == 4)
        check('D3 Symbolwahl: Auto plus 22 Symbole', cnt(p, '.icpick button') == 23 and cnt(p, '.icpick button[aria-pressed="true"]') == 1)
        p.locator('#main #hfName').fill('Gitarre üben')
        tiles.nth(2).click()
        p.wait_for_timeout(150)
        p.locator('#main .icpick [data-v=music]').click()
        p.wait_for_timeout(150)
        check('D4 Symbol gewählt', p.locator('#main .icpick [data-v=music]').get_attribute('aria-pressed') == 'true')
        p.locator('#main #hfTarget').fill('20')
        p.locator('#main #hfUnit').fill('Min')
        p.locator('#main [data-act=saveHab]').click()
        p.wait_for_timeout(200)
        hb = [h for h in S(p)['habits'] if h['name'] == 'Gitarre üben']
        check('D5 gespeichert mit Symbol und Art Menge', len(hb) == 1 and hb[0].get('ic') == 'music' and hb[0]['kind'] == 'amount', hb)
        check('D6 im Backup enthalten', ev(p, "backupObj().habits.find(h=>h.name==='Gitarre üben').ic") == 'music')
        hid = hb[0]['id'] if hb else ''
        go(p, f"(()=>{{const b=document.createElement('button');b.dataset.id='{hid}';act('editHab',b)}})()")
        p.locator('#main .icpick [data-v=""]').click()
        p.wait_for_timeout(120)
        p.locator('#main [data-act=saveHab]').click()
        p.wait_for_timeout(200)
        hb = [h for h in S(p)['habits'] if h['name'] == 'Gitarre üben']
        check('D7 „Auto“ entfernt das eigene Symbol', hb and 'ic' not in hb[0], hb)
        check('D8 Gitarre automatisch Musik-Symbol', ev(p, f"habIcKey(S.habits.find(h=>h.id==='{hid}'))") == 'music')
        shot(p, 'u_D_gewohnheiten', full=False)
        check('D ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- E: Training ----------
        p = open_app(b, T(2026, 11, 10, 17, 0), scale=2)
        go(p, "goRoot('training');render()")
        p.locator('#main [data-act=startPlan]').first.click()
        p.wait_for_timeout(300)
        p.locator('#main [data-act=startSession]').click()
        p.wait_for_timeout(300)
        rs = p.locator('#main .restset')
        check('E1 Pausentimer ohne Erklärsatz', 'Startet, sobald' not in rs.inner_text() and rs.locator('.rs-l svg').count() == 1, rs.inner_text())
        check('E2 Übung mit Körperkarte der Kategorie und 1/3', p.locator('#main .exey svg').count() == 1 and '1/3' in p.locator('#main .exey').inner_text(),
              p.locator('#main .exey').inner_text())
        check('E3 1RM und letztes Mal mit Symbol', p.locator('#main .ex .last svg').count() >= 1)
        check('E4 Prognose mit Zielscheibe statt „Prognose:“', cnt(p, '.pred svg') >= 1 and 'Prognose:' not in main_text(p))
        p.locator('#main [data-act=toggleDone]').first.click()
        p.wait_for_timeout(250)
        check('E5 abgehakter Satz zeigt Häkchen-Symbol', p.locator('#main .chk.on svg').count() == 1 and not GLYPHS.search(p.locator('#main .chk.on').inner_text()))
        ev(p, "S.draft.entries[0].sets.forEach(s=>s.done=true);render()")
        p.wait_for_timeout(150)
        check('E6 erledigte Übung im Streifen mit Symbol', p.locator('#main .steps .step.done svg').count() >= 1)
        go(p, "S.draft.finishing=true;render()")
        check('E7 Abschluss: Gefühl als Gesichter', p.locator('#main .feel button svg').count() == 5 and 'Zäh' in main_text(p))
        check('E8 offener Satz mit Warnsymbol', p.locator('#main .banner .bn-t svg').count() == 1)
        p.locator('#main [data-act=feel][data-v="4"]').click()
        p.wait_for_timeout(150)
        check('E9 Gefühl gewählt', ev(p, 'S.draft.feel') == 4)
        shot(p, 'u_E_abschluss', full=False)
        go(p, "S.draft=null;goRoot('training',['verlauf']);render()")
        mt = main_text(p)
        check('E10 Verlauf ohne Gebrauchsanweisung', 'Tippe ein Training an' not in mt and 'Gefühl:' not in mt, mt[:200])
        check('E11 Verlauf mit Symbolen (Gefühl, Dauer, Gewicht)', cnt(p, '.sess .meta svg') >= 6)
        go(p, "exQ='';exCatF='';exSubF='';goRoot('training',['uebungen']);render()")
        cc = p.locator('#main #listCats .chip')
        check('E12 Kategorien mit Körperkarte', cc.count() >= 7 and p.locator('#main #listCats .chip svg').count() == cc.count() - 1)
        check('E13 Gruppen-Überschrift mit Körperkarte', cnt(p, '.exg-h svg') >= 6)
        go(p, "goRoot('training',['plaene']);render()")
        check('E14 Pläne zeigen Kategorien als Körperkarte', cnt(p, '.pmeta .catics svg') >= 2)
        check('E ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- F: Ernährung ----------
        p = open_app(b, T(2026, 11, 10, 12, 10), scale=2)
        go(p, "goRoot('ernaehrung');render()")
        check('F1 vier Mahlzeiten mit Tageszeit-Symbol', cnt(p, '.mslot .ms-ic svg') == 4)
        check('F2 Favoriten mit Stern-Symbol statt Zeichen', cnt(p, '.fchip svg') >= 1 and not GLYPHS.search(p.locator('#main .favq').inner_text()))
        go(p, "mealOpen={k:today(),s:new Set(['fr'])};render()")
        check('F3 Ziehen als kurzer Hinweis mit Symbol', cnt(p, '.mdhint svg') == 1 and 'Lange drücken' in main_text(p))
        go(p, "mealReset();meal=newMeal(today());goRoot('ernaehrung',['mahlzeit']);render()")
        check('F4 Mahlzeit-Wahl mit Symbol', cnt(p, '.chips.slots .chip svg') == 4)
        check('F5 Suchen | Rezepte | Manuell mit Symbol', cnt(p, '.seg [data-act=mealMode] svg') == 3)
        check('F6 Quelle kurz', 'Daten: Open Food Facts' in main_text(p) and 'eine freie Lebensmittel-Datenbank' not in main_text(p))
        go(p, "openProduct({code:'4000000000006',n:'Skyr Natur',b:'Test',q:'500 g',u:'g',k:63,p:11,c:4,f:0.2,sv:150,src:'off'});push('produkt');render()")
        fav = p.locator('#main .favtog')
        check('F7 Favorit als Stern', fav.count() == 1 and fav.locator('.fav-ic svg').count() == 2)
        fav.click()
        p.wait_for_timeout(150)
        check('F8 Stern setzt Favorit', ev(p, 'prod.fav') is True)
        check('F9 Quelle mit Barcode', '4000000000006' in main_text(p) and 'Weicht etwas von der Packung ab' not in main_text(p))
        go(p, "S.recipes=[];goRoot('ernaehrung',['rezepte']);render()")
        check('F10 leere Rezepte als Bildfolge', cnt(p, '.steps3 svg') >= 3 and 'Leg dein erstes Rezept an' not in main_text(p))
        check('F ohne Fehler', not [e for e in p.errs if 'ERR_' not in e and '404' not in e], p.errs)
        p.context.close()

        # ---------- G: Fortschritt ----------
        p = open_app(b, T(2026, 11, 10, 9, 0), scale=2)
        go(p, "S.mode='basic';goRoot('fortschritt');render()")
        mt = main_text(p)
        check('G1 keine „ggü. davor“-Texte, Pfeile statt Plus/Minus', 'ggü. davor' not in mt and cnt(p, '.dlt svg') >= 2, mt[:400])
        check('G2 Ø Stimmung mit Gesicht', cnt(p, '.farea .kic svg') >= 1 and '1 bis 5' not in mt)
        check('G3 Zusammenhänge: Erklärung hinter „i“', cnt(p, '[data-act=info][data-id=aiIns]') == 1 and 'keine Ursachen' not in mt)
        check('G4 Bestwerte mit Pokal', cnt(p, '.fa-n .fan.pr svg') == 1)
        mb = p.locator('#main .morebtn')
        if mb.count():
            mb.click()
            p.wait_for_timeout(200)
            check('G5 „weitere in Analyse“ schaltet um', ev(p, 'S.mode') == 'perf')
            go(p, "S.mode='basic';render()")
        else:
            check('G5 „weitere in Analyse“ vorhanden', False, 'kein Knopf')
        go(p, "goRoot('fortschritt',['fMind']);render()")
        check('G6 Stimmung: Gesichter an der Achse', cnt(p, '.chart .yic') == 5)
        check('G7 7-Stunden-Linie als Legende', cnt(p, '.legend .lg-ref') == 1 and 'gestrichelt' not in main_text(p))
        go(p, "S.mode='perf';render()")
        check('G8 Analyse: Schlafqualität mit Akku an der Achse', cnt(p, '.chart .yic') == 10)
        go(p, "goRoot('fortschritt',['fErn']);render()")
        check('G9 Ernährung: Ziellinie als Legende', 'Gestrichelt' not in main_text(p) and cnt(p, '.legend .lg-ref') >= 1)
        check('G10 Mahlzeiten mit Tageszeit-Symbol', cnt(p, '.hbar .mslbl svg') == 4)
        go(p, "S.mode='basic';goRoot('fortschritt',['fTraining']);render()")
        check('G11 Muskelgruppen mit Körperkarte', cnt(p, '.hbar.cmp .mslbl svg') >= 6)
        check('G12 Übungen ohne Gebrauchsanweisung', 'Antippen zeigt den Verlauf' not in main_text(p))
        go(p, "goRoot('fortschritt',['fGewohn']);render()")
        check('G13 Gewohnheiten mit Symbol', cnt(p, '.fhn svg') >= 3)
        check('G ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- H: Ich ----------
        p = open_app(b, T(2026, 11, 10, 9, 0), scale=2)
        go(p, "goRoot('ich');render()")
        mt = main_text(p)
        check('H1 Module mit Symbol, Erklärungen hinter „i“', cnt(p, '.swrow > svg') == 3 and 'Ausgeschaltete Module behalten' not in mt
              and 'Analyse zeigt mehr Werte' not in mt and cnt(p, '[data-act=info]') >= 2)
        p.locator('#main [data-act=info][data-id=aiMods]').click()
        p.wait_for_timeout(100)
        check('H2 „i“ zeigt die Erklärung', 'Ausgeschaltete Module behalten' in main_text(p))
        go(p, "goRoot('ich',['koerper']);render()")
        check('H3 Maße mit Messfigur', cnt(p, '.meas .mlbl svg') == 5 and 'Wird beim Tippen gespeichert' not in main_text(p))
        go(p, "goRoot('ich',['journal']);render()")
        check('H4 Journal: Stimmung als Gesicht', cnt(p, '.jmood svg') >= 3)
        go(p, "goRoot('ich',['atem']);render()")
        bars = [p.locator('#main .brp').nth(i).locator('.brbar i').count() for i in range(3)]
        check('H5 Atemrhythmus als Balken (4, 3, 2 Abschnitte)', bars == [4, 3, 2] and 'Folge dem Quadrat' not in main_text(p), bars)
        go(p, "goRoot('ich',['ziele']);render();act('newGoal',document.body);render()")
        check('H6 Zielart als Kacheln mit Symbol', cnt(p, '.gtypes button svg') == 4)
        go(p, "goalEdit=null;goRoot('ich',['daten']);render()")
        mt = main_text(p)
        check('H7 Daten & Backup kurz, mit Symbolen', 'Deine Daten liegen nur auf diesem Gerät. Sichere sie' not in mt and cnt(p, '.bkst .sn svg') >= 2, mt[:500])
        check('H8 Versionsnummer im Fuß', 'Trainingsbuch 1.13.0' in mt)
        check('H ohne Fehler', not [e for e in p.errs if 'ERR_' not in e and '404' not in e], p.errs)
        p.context.close()

        # ---------- I: alle Seiten hell und dunkel, ohne Fehler und ohne Emoji-Zeichen ----------
        for dark in (False, True):
            p = open_app(b, T(2026, 11, 10, 19, 15), dark=dark, scale=1)
            found = []
            pages = [("goRoot('heute');render()", 'heute'), ("goRoot('training');render()", 'training'), ("goRoot('ernaehrung');mealOpen={k:today(),s:new Set(['fr','mi','ab','sn'])};render()", 'ernaehrung'),
                     ("goRoot('fortschritt');render()", 'fortschritt'), ("goRoot('ich');render()", 'ich')]
            for sub in ['fTraining', 'fGewohn', 'fErn', 'fKoerper', 'fMind']:
                pages.append((f"goRoot('fortschritt',['{sub}']);render()", sub))
            for root, sub in [('training', 'plaene'), ('training', 'uebungen'), ('training', 'verlauf'), ('ich', 'gewohnheiten'), ('ich', 'ziele'),
                              ('ich', 'koerper'), ('ich', 'journal'), ('ich', 'atem'), ('ernaehrung', 'bedarf'), ('ernaehrung', 'rezepte')]:
                pages.append((f"goRoot('{root}',['{sub}']);render()", sub))
            pages.append(("mealReset();meal=newMeal(today());goRoot('ernaehrung',['mahlzeit']);render()", 'mahlzeit'))
            for js, name in pages:
                go(p, js, 120)
                if GLYPHS.search(main_text(p)):
                    found.append((name, GLYPHS.findall(main_text(p))))
            check('I1 keine Text-Symbole (★ ✓ ✎ …) auf den Seiten' + (' (dunkel)' if dark else ''), not found, found)
            check('I2 Seiten ohne Fehler' + (' (dunkel)' if dark else ''), not [e for e in p.errs if 'ERR_' not in e and '404' not in e], p.errs)
            p.context.close()

        # ---------- J: schmales iPhone (375 px) ----------
        c = b.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2, is_mobile=True, has_touch=True,
                          locale='de-DE', timezone_id='Europe/Berlin', service_workers='block')
        p = c.new_page()
        errs = []
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.clock.install(time=T(2026, 11, 10, 7, 30))
        from h import BASE
        p.goto(BASE)
        p.wait_for_selector('#main')
        p.wait_for_timeout(300)
        ev(p, "act('clearDemo',document.body);act('clearDemo',document.body);dayOff=0;render()")
        p.wait_for_timeout(200)
        lb = p.locator('#main .cicard .ci-lt')
        hs = [x.bounding_box()['height'] for x in lb.all()]
        check('J1 Uhrzeit-Zeilen einzeilig bei 375 px', len(hs) == 2 and max(hs) < 30, hs)
        sw = p.evaluate("document.getElementById('main').scrollWidth<=document.getElementById('main').clientWidth+1")
        check('J2 kein waagerechtes Scrollen', sw)
        ev(p, "mealReset();meal=newMeal(today());goRoot('ernaehrung',['mahlzeit']);render()")
        p.wait_for_timeout(200)
        sl = p.locator('#main .chips.slots .chip')
        cut = p.evaluate("[...document.querySelectorAll('#main .chips.slots .chip')].some(b=>b.scrollWidth>b.clientWidth+1)")
        check('J3 Mahlzeit-Chips nicht abgeschnitten', sl.count() == 4 and not cut)
        shot(p, 'u_J_375_mahlzeit', full=False)
        check('J ohne Fehler', not errs, errs)
        c.close()
        b.close()


run()
print(f'{len(OK)} bestanden, {len(BAD)} fehlgeschlagen')
for x in BAD:
    print('FEHLER', x)
sys.exit(1 if BAD else 0)
