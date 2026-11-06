"""Tests für Version 1.12.0: Check-in und Check-out mit Uhrzeiten, übrige Kalorien, g/ml überall.
Aufruf: python3 pwa_112_test.py  (App unter http://127.0.0.1:8765/App/, Lebensmittel-Datenbank unter /App-Daten/)"""
import os
import sys
from playwright.sync_api import sync_playwright
from h import T, open_app, S, shot, main_text, new_ctx, BASE

OK = []
BAD = []


def check(name, cond, info=''):
    (OK if cond else BAD).append(name + ('' if cond else '  →  ' + str(info)))


def ev(p, js):
    return p.evaluate('s=>window.__ev(s)', js)


def fresh(b, when, **kw):
    """App mit leerem Stand („Neu anfangen“)."""
    p = open_app(b, when, **kw)
    ev(p, "act('clearDemo',document.body);act('clearDemo',document.body)")
    ev(p, "dayOff=0;render()")
    p.wait_for_timeout(150)
    return p


def card(p):
    c = p.locator('#main .cicard, #main .cidone')
    return c.first.inner_text().replace('\n', ' | ') if c.count() else ''


def tap(p, sel, i=0):
    p.locator('#main ' + sel).nth(i).click()
    p.wait_for_timeout(120)


def at(p, when):
    p.clock.set_system_time(when)
    ev(p, "render()")
    p.wait_for_timeout(100)


def run():
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--lang=de-DE'], env={**os.environ, 'LANG': 'de_DE.UTF-8', 'LANGUAGE': 'de', 'LC_ALL': 'de_DE.UTF-8'})

        # ---------- A: erster Morgen ohne Daten ----------
        p = fresh(b, T(2026, 11, 6, 8, 5))
        t = card(p)
        check('A1 Check-in offen', 'CHECK-IN' in t and 'AUFGESTANDEN' in t and 'SCHLAFQUALITÄT' in t, t)
        check('A1 kein Check-out am Morgen', 'CHECK-OUT' not in t and 'STIMMUNG' not in t, t)
        check('A1 Einschlafzeit nachfragen ohne Check-out', 'EINGESCHLAFEN' in t and 'kein Check-out am Abend davor' in t, t)
        check('A1 Vorschläge 07:00 und 23:00', p.locator('#main [data-act=ciTSet][data-f=wake]').inner_text() == '07:00'
              and p.locator('#main [data-act=ciTSet][data-f=bed]').inner_text() == '23:00', t)
        shot(p, 't_A1_checkin_leer', full=False)
        tap(p, '[data-act=ciTSet][data-f=wake]')
        tap(p, '[data-act=ciT][data-f=bed][data-d="1"]')
        d = S(p)['days']['2026-11-06']['sleep']
        check('A2 Uhrzeiten gespeichert', d.get('wake') == '07:00' and d.get('bed') == '23:15', d)
        check('A2 Dauer 7:45', abs(d.get('h', 0) - 7.75) < 1e-9, d)
        check('A2 Ergebnis angezeigt', 'Schlaf 7:45 h · eingeschlafen 23:15' in card(p), card(p))
        check('A2 noch nicht eingeklappt', 'ERLEDIGT' not in card(p), card(p))
        tap(p, '[data-act=sleepQ][data-v="4"]')
        t = card(p)
        check('A3 eingeklappt', 'CHECK-IN ERLEDIGT' in t and 'VERLAUF' in t and 'ÄNDERN' in t and 'SCHLAFQUALITÄT' not in t, t)
        check('A3 keine 7-Tage-Balken', p.locator('#main .cis-bars').count() == 0)
        h_card = p.locator('#main .cidone').bounding_box()['height']
        check('A3 eine Zeile hoch', h_card < 70, h_card)
        shot(p, 't_A3_eingeklappt', full=False)

        at(p, T(2026, 11, 6, 16, 59))
        check('A4 vor 17 Uhr kein Check-out', 'CHECK-OUT' not in card(p), card(p))
        # Uhr läuft über 17 Uhr: Karte wechselt von selbst
        p.clock.set_system_time(T(2026, 11, 6, 17, 0, ))
        p.clock.fast_forward(31000)
        p.wait_for_timeout(150)
        t = card(p)
        check('A5 ab 17 Uhr Check-out (ohne Antippen)', 'CHECK-OUT' in t and 'STIMMUNG' in t and 'EINSCHLAFEN' in t and 'CHECK-IN ERLEDIGT' in t, t)
        check('A5 Vorschlag Einschlafen = üblich 23:15', p.locator('#main [data-act=ciTSet][data-f=bed]').inner_text() == '23:15')
        shot(p, 't_A5_checkout', full=False)
        tap(p, '[data-act=mood][data-v="4"]')
        check('A6 nur Stimmung: noch offen', 'CHECK-OUT' in card(p), card(p))
        tap(p, '[data-act=ciTSet][data-f=bed]')
        st = S(p)
        check('A6 Stimmung am Tag', st['days']['2026-11-06'].get('mood') == 4, st['days']['2026-11-06'])
        check('A6 Einschlafzeit beim Folgetag', st['days'].get('2026-11-07', {}).get('sleep', {}).get('bed') == '23:15', st['days'].get('2026-11-07'))
        t = card(p)
        check('A6 beides erledigt, eine Zeile', 'CHECK-IN UND -OUT ERLEDIGT' in t and 'STIMMUNG' not in t, t)
        shot(p, 't_A6_beides', full=False)
        tap(p, '[data-act=ciEdit]')
        t = card(p)
        check('A7 Ändern zeigt beides', 'AUFGESTANDEN' in t and 'EINGESCHLAFEN' in t and 'in der Nacht davor' in t and 'CHECK-OUT' in t
              and 'EINSCHLAFEN' in t and 'FERTIG' in t, t)
        shot(p, 't_A7_aendern', full=False)
        # Uhrzeit direkt eintippen (iOS-Zeitrad): Einschlafen 23:40 → Folgetag
        p.locator('#main input.tval[data-ct=bed][data-k="2026-11-07"]').fill('23:40')
        p.wait_for_timeout(100)
        check('A7 Uhrzeit tippen speichert', S(p)['days']['2026-11-07']['sleep']['bed'] == '23:40', S(p)['days']['2026-11-07'])
        # Aufgestanden heute 6:58 → 7:43 Schlaf → auf 5 Minuten: 7:45
        p.locator('#main input.tval[data-ct=wake][data-k="2026-11-06"]').fill('06:58')
        p.wait_for_timeout(100)
        d = S(p)['days']['2026-11-06']['sleep']
        check('A7 Dauer auf 5 Minuten gerundet (7:43 → 7:45)', abs(d['h'] - 7.75) < 1e-9, d)
        check('A7 Ergebnis ohne Neuzeichnen aktualisiert', '7:45 h' in p.locator('#main #cires-2026-11-06').inner_text(), card(p))
        p.locator('#main input.tval[data-ct=wake][data-k="2026-11-06"]').fill('07:02')
        p.wait_for_timeout(100)
        d = S(p)['days']['2026-11-06']['sleep']
        check('A7 Dauer 7:47 → 7:45', abs(d['h'] - 7.75) < 1e-9, d)
        tap(p, '[data-act=ciClose]')
        check('A8 Fertig klappt ein', 'CHECK-IN UND -OUT ERLEDIGT' in card(p), card(p))

        # ---------- B: nächster Morgen ----------
        at(p, T(2026, 11, 7, 6, 40))
        t = card(p)
        check('B1 Check-in mit Einschlafzeit vom Vorabend', 'AUFGESTANDEN' in t and 'EINGESCHLAFEN' not in t, t)
        check('B1 Vorschlag aufgestanden = jetzt (früher als üblich)', p.locator('#main [data-act=ciTSet][data-f=wake]').inner_text() == '06:40', t)
        tap(p, '[data-act=ciTSet][data-f=wake]')
        d = S(p)['days']['2026-11-07']['sleep']
        check('B2 Dauer über Mitternacht (23:40 → 6:40 = 7:00)', abs(d.get('h', 0) - 7.0) < 1e-9, d)
        check('B2 Ergebnis', 'Schlaf 7:00 h · eingeschlafen 23:40' in card(p), card(p))
        # − und + springen auf Viertelstunden
        tap(p, '[data-act=ciT][data-f=wake][data-d="1"]')
        check('B3 + → 06:45', S(p)['days']['2026-11-07']['sleep']['wake'] == '06:45')
        tap(p, '[data-act=ciT][data-f=wake][data-d="-1"]')
        tap(p, '[data-act=ciT][data-f=wake][data-d="-1"]')
        check('B3 −− → 06:15', S(p)['days']['2026-11-07']['sleep']['wake'] == '06:15')
        tap(p, '[data-act=sleepQ][data-v="3"]')
        check('B4 erledigt', 'CHECK-IN ERLEDIGT' in card(p), card(p))
        # Verlauf → Fortschritt · Schlaf & Stimmung
        tap(p, '[data-act=goProg][data-v=mind]')
        p.wait_for_timeout(400)
        check('B5 Verlauf öffnet Schlaf & Stimmung', ev(p, 'curView()') == 'fMind' and 'Ø Schlaf' in main_text(p), ev(p, 'curView()'))
        ev(p, "goRoot('heute');render()")
        p.wait_for_timeout(300)

        # ---------- C: nach Mitternacht gilt der Check-out für den Vortag ----------
        at(p, T(2026, 11, 8, 1, 30))
        t = card(p)
        check('C1 nachts nur Check-out für gestern', 'CHECK-OUT · GESTERN' in t and 'CHECK-IN' not in t, t)
        check('C1 Vorschlag Einschlafen = jetzt 01:30', p.locator('#main [data-act=ciTSet][data-f=bed]').inner_text() == '01:30', t)
        shot(p, 't_C1_nachts', full=False)
        tap(p, '[data-act=mood][data-v="2"]')
        tap(p, '[data-act=ciTSet][data-f=bed]')
        st = S(p)
        check('C2 Stimmung beim Vortag', st['days']['2026-11-07'].get('mood') == 2 and not st['days'].get('2026-11-08', {}).get('mood'), st['days'].get('2026-11-08'))
        check('C2 Einschlafzeit 01:30 in der Nacht zum 8.', st['days']['2026-11-08']['sleep']['bed'] == '01:30', st['days']['2026-11-08'])
        check('C2 erledigt: Karte weg bis 3 Uhr, Hinweis', card(p) == '' and 'gestern gespeichert' in p.locator('#toastHost').inner_text(), (card(p), p.locator('#toastHost').inner_text()))
        at(p, T(2026, 11, 8, 2, 59))
        check('C3 vor 3 Uhr noch kein neuer Check-in', 'AUFGESTANDEN' not in card(p), card(p))
        at(p, T(2026, 11, 8, 3, 0))
        check('C3 ab 3 Uhr Check-in', 'AUFGESTANDEN' in card(p) and 'EINGESCHLAFEN' not in card(p), card(p))
        tap(p, '[data-act=ciTSet][data-f=wake]')
        d = S(p)['days']['2026-11-08']['sleep']
        check('C4 Vorschlag um 3 Uhr = 03:00, Dauer 1:30', d['wake'] == '03:00' and abs(d['h'] - 1.5) < 1e-9, d)
        at(p, T(2026, 11, 8, 9, 0))
        p.locator('#main input.tval[data-ct=wake]').fill('08:30')
        p.wait_for_timeout(100)
        check('C4 korrigiert 7:00', abs(S(p)['days']['2026-11-08']['sleep']['h'] - 7.0) < 1e-9)
        # unplausible Dauer
        p.locator('#main input.tval[data-ct=wake]').fill('01:50')
        p.wait_for_timeout(100)
        d = S(p)['days']['2026-11-08']['sleep']
        check('C5 unter 1 Stunde: keine Dauer, Hinweis', 'h' not in d and 'Prüf die Uhrzeiten' in card(p), (d, card(p)))
        p.locator('#main input.tval[data-ct=wake]').fill('08:30')
        p.wait_for_timeout(100)

        # ---------- D: frühere Tage ----------
        ev(p, "dayOff=-3;render()")  # 5.11.: nichts eingetragen
        p.wait_for_timeout(150)
        t = card(p)
        check('D1 früherer Tag: Check-in und Check-out offen', 'CHECK-IN' in t and 'CHECK-OUT' in t and 'AUFGESTANDEN' in t and 'STIMMUNG' in t, t)
        check('D1 Vorschläge ohne „jetzt“', p.locator('#main [data-act=ciTSet][data-f=wake]').inner_text() != '09:00', t)
        tap(p, '[data-act=mood][data-v="5"]')
        check('D2 Stimmung beim 5.11.', S(p)['days']['2026-11-05'].get('mood') == 5)
        ev(p, "dayOff=-2;render()")  # 6.11.: alles erledigt
        p.wait_for_timeout(150)
        check('D3 erledigter Tag eingeklappt', 'CHECK-IN UND -OUT ERLEDIGT' in card(p), card(p))
        ev(p, "dayOff=0;render()")
        errs = list(p.errs)
        check('A–D ohne Fehler', not errs, errs)
        p.context.close()

        # ---------- E: alte Einträge (nur Dauer) ----------
        p = open_app(b, T(2026, 11, 6, 18, 0))
        ev(p, """(()=>{for(const k in S.days){const s=S.days[k].sleep;if(s){delete s.bed;delete s.wake}}
            const d=S.days['2026-11-06'];d.mood=3;render()})()""")
        p.wait_for_timeout(150)
        t = card(p)
        check('E1 alte Einträge: Check-in erledigt, Check-out braucht Einschlafzeit', 'CHECK-IN ERLEDIGT' in t and 'EINSCHLAFEN' in t, t)
        ev(p, "dayOff=-1;render()")
        p.wait_for_timeout(150)
        check('E2 alter Tag mit Stimmung und alter Dauer danach: erledigt', 'CHECK-IN UND -OUT ERLEDIGT' in card(p), card(p))
        tap(p, '[data-act=ciEdit]')
        t = card(p)
        check('E3 alte Dauer bleibt sichtbar', 'Schlaf ' in p.locator('#main .ci-res').first.inner_text(), t)
        ev(p, "dayOff=0;ciEdit=null;render()")
        check('E ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- F: übrige Kalorien, Wahl Zielbedarf/Heute ----------
        p = fresh(b, T(2026, 11, 6, 12, 0))
        ev(p, """(()=>{S.nutri={sex:'m',age:'35',height:'180',weight:'80',wDate:today(),goal:'halten',diet:'normal',pal:'1.4'};
            const D=dayMut(today());D.food=[{id:'a',t:'08:00',n:'Haferflocken',k:612,p:20,c:90,f:12,sl:'fr'}];render()})()""")
        p.wait_for_timeout(150)
        txt = p.locator('#main .card:has([data-act=goFood])').inner_text().replace('\n', ' | ')
        tg = ev(p, "r10(foodTarget(nCalc(),today()).k)")
        check('F1 übrig = Ziel − gegessen', f"{tg - 612:,}".replace(',', '.') + ' | kcal übrig' in txt, (txt, tg))
        check('F1 Zeile gegessen', f"612 von {tg:,} kcal gegessen".replace(',', '.') in txt, txt)
        shot(p, 't_F1_kcal', full=False)
        ev(p, "S.days[today()].food.push({id:'b',t:'12:00',n:'Pizza',k:3000,p:100,c:300,f:120,sl:'mi'});render()")
        p.wait_for_timeout(100)
        txt = p.locator('#main .card:has([data-act=goFood])').inner_text().replace('\n', ' | ')
        check('F2 drüber', f"{3612 - tg:,}".replace(',', '.') + ' | kcal drüber' in txt, txt)
        # Tagebuch rechnet gleich
        ev(p, "goRoot('ernaehrung');render()")
        p.wait_for_timeout(300)
        check('F3 Tagebuch: gleiche Rechnung', f"{3612 - tg:,}".replace(',', '.') + ' drüber' in main_text(p), main_text(p)[:300])
        # Wahl „Heute“ bleibt nach Neustart
        ev(p, "goRoot('ernaehrung',['bedarf']);render()")
        p.wait_for_timeout(300)
        p.locator('#main [data-act=nView][data-v=heute]').click()
        p.wait_for_timeout(150)
        check('F4 Wahl gespeichert', S(p)['nutri'].get('view') == 'heute', S(p)['nutri'])
        p.wait_for_timeout(800)
        p.reload()
        p.wait_for_selector('#main')
        p.wait_for_timeout(300)
        check('F4 nach Neustart noch „Heute“', ev(p, "nViewGet()") == 'heute')
        tgh = ev(p, "r10(nCalc().heute.k)")
        txt = p.locator('#main .card:has([data-act=goFood])').inner_text().replace('\n', ' | ')
        check('F4 Heute-Karte rechnet mit „Heute“', f"von {tgh:,} kcal".replace(',', '.') in txt, (txt, tgh))
        check('F ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- G: g/ml überall ----------
        p = fresh(b, T(2026, 11, 6, 12, 0))
        ev(p, """openProduct({code:'4000000000006',n:'Milch 1,5 %',b:'Test',q:'1 Liter',u:'ml',k:47,p:3.4,c:4.9,f:1.5,sv:200,src:'off'},{date:today()})""")
        p.wait_for_timeout(300)
        mt = main_text(p)
        check('G1 Produkt: Menge in g/ml', 'MENGE IN G/ML' in mt and 'pro 100 g/ml' in mt, mt[:400])
        check('G1 Chips ohne Einheit, Portion', '1 PORTION · 200' in mt.upper() and '\n250\n' in mt, mt[:600])
        check('G1 Einheit neben der Zahl', p.locator('#main .amt-u').first.inner_text() == 'g/ml')
        shot(p, 't_G1_produkt', full=False)
        p.locator('#main [data-act=prodAmt][data-v="250"]').click()
        p.locator('#main [data-act=prodAdd]').click()
        p.wait_for_timeout(300)
        ev(p, "goRoot('ernaehrung');render()")
        p.wait_for_timeout(300)
        ev(p, "document.querySelectorAll('#main .ms-tog').forEach(b=>{if(!b.disabled)b.click()})")
        p.wait_for_timeout(200)
        check('G2 Tagebuch: 250 g/ml', '250 g/ml' in main_text(p), main_text(p)[:800])
        ev(p, "openOwnForm({n:'Saft'},{})")
        p.wait_for_timeout(300)
        mt = main_text(p)
        check('G3 eigenes Produkt ohne Umschalter', 'NÄHRWERTE PRO 100 G/ML' in mt and 'ml (flüssig)' not in mt and 'EINE PORTION IN G/ML' in mt, mt[:500])
        shot(p, 't_G3_eigenes', full=False)
        check('G4 Packung „1 Liter“ erkannt', ev(p, "packG({q:'1 Liter',u:'g'})") == 1000 and ev(p, "packG({q:'500 g',u:'ml'})") == 500)
        check('G ohne Fehler', not p.errs, p.errs)
        p.context.close()

        # ---------- H: alle Seiten mit Beispieldaten, hell und dunkel ----------
        for dark in (False, True):
            p = open_app(b, T(2026, 11, 6, 18, 30), dark=dark, scale=2)
            views = ['heute', 'training', 'ernaehrung', 'fortschritt', 'ich']
            for v in views:
                ev(p, f"goRoot('{v}');render()")
                p.wait_for_timeout(250)
            for sub in ['fMind', 'fErn', 'fKoerper', 'fTraining', 'fGewohn']:
                ev(p, f"goRoot('fortschritt',['{sub}']);render()")
                p.wait_for_timeout(200)
            for sub in ['bedarf', 'rezepte', 'mahlzeit']:
                ev(p, f"mealReset();meal=newMeal(today());goRoot('ernaehrung',['{sub}']);render()")
                p.wait_for_timeout(200)
            ev(p, "goRoot('ich',['journal']);render()")
            p.wait_for_timeout(200)
            ev(p, "goRoot('heute');render()")
            p.wait_for_timeout(300)
            if dark:
                p.locator('#main .cicard').scroll_into_view_if_needed()
                shot(p, 't_H_dunkel_checkout', full=False)
            check('H Seiten ohne Fehler' + (' (dunkel)' if dark else ''), not p.errs, p.errs)
            p.context.close()

        # ---------- I: schmales iPhone (375 px): Zeile bleibt einzeilig ----------
        c = b.new_context(viewport={'width': 375, 'height': 667}, device_scale_factor=2, is_mobile=True, has_touch=True,
                          locale='de-DE', timezone_id='Europe/Berlin', service_workers='block')
        p = c.new_page()
        p.clock.install(time=T(2026, 11, 6, 18, 30))
        p.goto(BASE)
        p.wait_for_selector('#main')
        p.wait_for_timeout(300)
        ev(p, "S.days[today()].mood=4;dayMut(offFrom(today(),1)).sleep={bed:'23:30'};render()")
        p.wait_for_timeout(150)
        hd = p.locator('#main .cidone .pane-h')
        check('I1 eine Zeile bei 375 px', hd.count() == 1 and hd.bounding_box()['height'] < 30, hd.bounding_box() if hd.count() else None)
        p.locator('#main .cidone').scroll_into_view_if_needed()
        shot(p, 't_I1_375', full=False)
        c.close()
        b.close()


run()
print(f'{len(OK)} bestanden, {len(BAD)} fehlgeschlagen')
for x in BAD:
    print('FEHLER', x)
sys.exit(1 if BAD else 0)
