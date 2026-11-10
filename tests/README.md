# Tests der Web-App

Playwright mit Chromium in iPhone-Größe (390 × 844), Zeitzone Berlin, Uhr über `page.clock`.
Die Tests laufen gegen eine Testkopie der App, in der `window.__ev` die internen Funktionen erreichbar macht.
Die veröffentlichte App bleibt unverändert.

1. Web-Ordner anlegen, z. B. `www/`, und die Lebensmittel-Datenbank vom Zweig `gh-pages` des Repositorys
   `App-Daten` nach `www/App-Daten/` legen (`manifest.json` und die `.tsv.gz`-Datei, nur für `smoke_112.py`).
2. `./mkt.sh <Checkout von gh-pages> www`
3. `cd www && python3 -m http.server 8765 --bind 127.0.0.1`
4. `python3 pwa_112_test.py`, `python3 pwa_113_test.py` und `python3 smoke_112.py` (Bilder landen in `shots/`)

Für 24-Stunden-Zeitfelder starten die Tests Chromium mit `LANG=de_DE.UTF-8`.

| Datei | Prüft |
|---|---|
| `pwa_112_test.py` | 1.12.0 (Erwartungen seit 1.13.0 an die Symbole angepasst): Check-in ab 3 Uhr, Check-out ab 17 Uhr und nachts für gestern, Dauer aus Uhrzeiten (über Mitternacht, auf 5 Minuten), Vorschläge, − und +, Eintippen, alte Einträge, frühere Tage, übrige Kalorien, gespeicherte Wahl Zielbedarf/Heute, g/ml, alle Seiten hell und dunkel, 375 px |
| `pwa_113_test.py` | 1.13.0: Symbole statt Erklärtext – Gesichter und Akku als Skalen, Körperkarten für Kategorien, Tageszeit-Symbole für Mahlzeiten, Symbol je Gewohnheit (passend zum Namen oder gewählt, im Backup), Arten als Vorschau, Pfeile statt „ggü. davor“, Symbole an Diagrammachsen, Erklärungen hinter „i“, kurze Rückmeldung beim Antippen, keine Text-Symbole wie ★ ✓ ✎ auf den Seiten, alle Seiten hell und dunkel, 375 px |
| `smoke_112.py` | Datenbank laden und suchen, Produkt eintragen, Rezept nach g/ml, Training starten |
