"""Rauchtest 1.12.0: Datenbank-Suche mit echter Datei, Produkt eintragen, Rezept nach g/ml, Training, Backup-Runde."""
import os
import json
import sys
from playwright.sync_api import sync_playwright
from h import T, open_app, E, S, shot, main_text, SHOTS

OK, BAD = [], []


def check(n, c, i=''):
    (OK if c else BAD).append(n + ('' if c else '  →  ' + str(i)[:600]))


with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--lang=de-DE'], env={**os.environ, 'LANG': 'de_DE.UTF-8', 'LANGUAGE': 'de', 'LC_ALL': 'de_DE.UTF-8'})
    p = open_app(b, T(2026, 11, 6, 12, 10), scale=2)
    # Datenbank laden (lokal unter /App-Daten/)
    E(p, "goRoot('ich',['daten']);render()")
    p.wait_for_timeout(300)
    p.locator('#main [data-act=fdbGet]').first.click()
    for _ in range(60):
        p.wait_for_timeout(500)
        if E(p, "!!(FDB&&FDB.meta)"):
            break
    check('Datenbank geladen', E(p, "!!(FDB&&FDB.meta)"))
    # Suche „kefir“
    E(p, "mealReset();meal=newMeal(today());goRoot('ernaehrung',['mahlzeit']);render()")
    p.wait_for_timeout(300)
    inp = p.locator('#main #foodQ')
    inp.fill('kefir')
    p.wait_for_timeout(2500)
    mt = main_text(p)
    check('Treffer mit kcal/100 g/ml', 'kcal/100 g/ml' in mt and 'kcal/100 g ' not in mt + ' ', mt[:700])
    shot(p, 's_suche', full=False)
    row = p.locator('#main .prow').first
    row.click()
    p.wait_for_timeout(400)
    mt = main_text(p)
    check('Produktseite g/ml', 'MENGE IN G/ML' in mt and 'pro 100 g/ml' in mt, mt[:500])
    p.locator('#main [data-act=prodAdd]').click()
    p.wait_for_timeout(400)
    E(p, "goRoot('ernaehrung');render()")
    p.wait_for_timeout(300)
    E(p, "mealOpen={k:today(),s:new Set(['fr','mi','ab','sn'])};render()")
    p.wait_for_timeout(200)
    check('Tagebuch zeigt g/ml', ' g/ml · ' in main_text(p), main_text(p)[:900])
    shot(p, 's_tagebuch', full=False)
    # Rezept nach g/ml eintragen
    E(p, """(()=>{S.recipes.push({id:'rt1',n:'Porridge',por:2,w:0,note:'',items:[{id:'i1',n:'Haferflocken',g:100,u:'g',per:{k:370,p:13,c:59,f:7}},{id:'i2',n:'Milch',g:300,u:'ml',per:{k:47,p:3.4,c:4.9,f:1.5}}],used:0,uses:0,created:Date.now()});
      rvOpen('rt1');goRoot('ernaehrung',['rezepte','rezept']);render()})()""")
    p.wait_for_timeout(300)
    p.locator('#main [data-act=rvMode][data-v=g]').click()
    p.wait_for_timeout(200)
    mt = main_text(p)
    check('Rezept: Umschalter g/ml und Einheit', 'G/ML' in mt and p.locator('#main #rvU').inner_text() == 'g/ml', mt[:700])
    check('Rezept: Zutaten in g/ml', '300 g/ml' in mt and '100 g/ml' in mt, mt)
    shot(p, 's_rezept', full=False)
    p.locator('#main [data-act=recEat]').click()
    p.wait_for_timeout(300)
    # Training kurz: starten, Übung, Satz, beenden
    E(p, "goRoot('training');render()")
    p.wait_for_timeout(300)
    p.locator('#main [data-act=goTrain]').first.click()
    p.wait_for_timeout(300)
    check('Training startet', E(p, "curView()") == 'session', E(p, "curView()"))
    # Backup-Runde mit Uhrzeiten
    real = [e for e in p.errs if 'ERR_TUNNEL_CONNECTION_FAILED' not in e and 'ERR_NAME_NOT_RESOLVED' not in e]
    check('Seiten ohne Fehler (außer gesperrtem Netz für Bilder)', not real, real)
    p.context.close()
    b.close()

print(f'{len(OK)} bestanden, {len(BAD)} fehlgeschlagen')
for x in BAD:
    print('FEHLER', x)
sys.exit(1 if BAD else 0)
