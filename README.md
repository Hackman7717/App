# Trainingsbuch

Persönliche All-in-one-App für Training, Gewohnheiten, Ziele, Ernährung, Schlaf, Körper und Fortschritt.
Sie läuft als installierbare Web-App (PWA) auf dem iPhone, auf Android und am Computer.

- **Offline:** Nach dem ersten Öffnen funktioniert die App ohne Internet.
- **Kein Konto:** Alle Daten bleiben auf deinem Gerät. Fotos eingeschlossen.
- **Backup:** Unter *Ich → Daten & Backup* sicherst du alles als Datei, am besten in iCloud Drive. Die App erinnert dich daran.
- **Löschen mit Rückgängig:** Alle Daten oder nur die Einträge löschen und 30 Tage lang zurückholen.
- **Ernährung mit Barcode und Suche:** Strichcode mit der Kamera scannen, als Foto laden oder die Zahlen eintippen. Lebensmittel nach Namen suchen. Daten kommen von [Open Food Facts](https://world.openfoodfacts.org) (Lizenz ODbL). Fehlt ein Produkt, legst du es einmal selbst an. Gefundene und eigene Produkte merkt sich die App, sie funktionieren danach auch offline.
- **Rezepte:** Eigene Gerichte aus Zutaten anlegen und danach portionsweise oder nach Gewicht ins Ernährungstagebuch eintragen.

## Rezepte

- **Anlegen:** *Ernährung → Rezepte → Neues Rezept* oder *Mahlzeit eintragen → Rezepte → Neues Rezept*. Name eingeben und festlegen, wie viele Portionen das Rezept ergibt.
- **Zutaten:** *Zutat hinzufügen* sucht wie beim Eintragen einer Mahlzeit, das Strichcode-Symbol daneben scannt direkt. Für Dinge ohne Packung gibt es *Eigene Werte*. Mengen lassen sich in der Zutatenliste direkt ändern, die Nährwerte pro Portion rechnen sofort mit.
- **Gewicht fertig gekocht (optional):** Wer das fertige Essen wiegt, kann später auch in Gramm eintragen, etwa 350 g aus dem Topf.
- **Eintragen:** Rezept antippen, Portionen oder Gramm wählen, *Eintragen*. Im Tagebuch lassen sich die Portionen später ändern, die Werte rechnen sich neu. Spätere Änderungen am Rezept verändern frühere Einträge nicht.
- **Entwurf:** Ein Rezept, das noch nicht gespeichert ist, geht nicht verloren, auch wenn du zurückgehst oder die App zwischendurch schließt. Unter *Rezepte* kannst du weitermachen oder den Entwurf verwerfen.
- Rezepte sind im Backup enthalten.

## Daten löschen

- **Wo:** *Ich → Daten & Backup → Daten löschen …*. Die Seite zeigt vorher genau, was gelöscht wird.
- **Alles:** Trainings, Tagebuch, Fotos, Rezepte, gespeicherte Lebensmittel, Favoriten, Ziele, eigene Übungen, Pläne und Gewohnheiten, Tagesbedarf und Einstellungen. Die App startet danach wie neu, mit den Standard-Übungen, -Plänen und -Gewohnheiten als Vorlage.
- **Nur Einträge:** Trainings, Tagebuch (Gewohnheiten, Schlaf, Stimmung, Journal, Ernährung, Gewicht, Maße, Atemübungen) und Fotos. Übungen, Pläne, Gewohnheiten, Ziele, Rezepte, Lebensmittel, Favoriten und Einstellungen bleiben.
- **Rückgängig:** direkt im Hinweis nach dem Löschen, über die Karte auf *Heute* oder unter *Daten & Backup*, 30 Tage lang. Was du seitdem neu eingetragen hast, bleibt dabei erhalten.
- **Endgültig:** Nach 30 Tagen oder mit *Jetzt endgültig löschen* sind die Daten samt Fotos und Sicherheitskopien vom Gerät entfernt. Backup-Dateien, die du gespeichert hast, bleiben unberührt.

## Barcode und Lebensmittelsuche

- **Scannen:** *Ernährung* → Strichcode-Symbol neben „Mahlzeit eintragen“. Den Strichcode waagerecht in den Rahmen halten, etwa 15 bis 25 cm vom Handy entfernt. Lesbar sind EAN-13, EAN-8 und UPC-A. Ein Code gilt erst, wenn er in zwei Kamerabildern gleich gelesen wurde.
- **Suchen:** *Mahlzeit eintragen* → Suchbegriff eingeben → *Suchen*. Treffer auf dem Gerät erscheinen sofort, Open Food Facts wird erst beim Tippen auf *Suchen* gefragt. Open Food Facts erlaubt nur wenige Suchen pro Minute.
- **Menge:** Gewicht oder Milliliter eintippen oder eine Portion antippen. Kalorien und Makros rechnet die App aus den Werten pro 100 g aus. Die Menge lässt sich im Tagebuch später ändern, die Werte rechnen sich dann neu.
- **Datenschutz:** Für Suche und Barcode schickt die App nur den Suchbegriff oder die Barcode-Nummer an Open Food Facts. Deine Einträge bleiben auf dem Gerät.

## Installieren auf dem iPhone

1. Öffne die Adresse der App in **Safari**.
2. Tippe unten rechts auf **•••** und dann auf **Teilen**. In älteren iOS-Versionen ist *Teilen* direkt in der Leiste.
3. Wähle **Zum Home-Bildschirm** und dann **Hinzufügen**.
4. Öffne die App über das neue Symbol.

Die installierte App hat ihren eigenen Speicher, getrennt von Safari. Trag deine Daten deshalb erst in der installierten App ein oder lade dort dein Backup.

## Daten aus der Claude-Version übernehmen

1. In der Claude-Version: *Ich → Daten → Backup speichern* (oder *Backup kopieren*).
2. In dieser App: *Ich → Daten & Backup → Backup-Datei laden* (oder *Backup-Text einfügen*).

Fotos aus der Claude-Version kommen dabei nicht mit.

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | Die komplette App: Oberfläche, Logik und Gestaltung |
| `sw.js` | Service Worker für den Offline-Betrieb und Updates |
| `manifest.webmanifest` | Name, Symbol und Startverhalten der installierten App |
| `icons/` | App-Symbole |
| `fonts/` | Schriften Saira Condensed und Public Sans (SIL Open Font License, siehe `fonts/OFL-*.txt`) |

Daten liegen in IndexedDB (`trainingsbuch`, Speicher `kv` und `photos`) mit einer Kopie im localStorage (`trainingsbuch.v1`).

## Neue Version veröffentlichen

1. Änderungen an `index.html` vornehmen.
2. In `sw.js` die Konstante `VERSION` erhöhen und in `index.html` den Wert `app-version` anpassen.
3. Hochladen. Die installierte App meldet beim nächsten Öffnen „Neue Version“ und übernimmt sie auf Tippen. Die Daten bleiben erhalten.
