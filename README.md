# Casino Noir – konfigurierbares Glücksrad

Eine statische, responsive Glücksrad-Web-App im Casino-Noir-Stil. Das Rad besteht vollständig aus SVG und wird für jede Segmentanzahl neu berechnet. Es gibt **keine fest eingebrannte Segmentgrafik**.

## Start

- **Einfach:** `casino-noir-standalone.html` im Browser öffnen. Dieses Dokument enthält HTML, CSS und JavaScript vollständig eingebettet.
- **Für GitHub Pages:** `index.html`, `styles.css` und `app.js` ins Stammverzeichnis der gewünschten Branch legen und GitHub Pages dafür aktivieren. Es wird kein Build-Schritt benötigt.
- **Lokal mit Webserver:** Im Ordner `python -m http.server 8000` starten und `http://localhost:8000` öffnen.

## Funktionen

- Segmente hinzufügen, löschen, duplizieren und nach oben/unten sortieren; auch ein leeres Rad wird unterstützt.
- Pro Segment eigene Farbe, Text und/oder Symbol; Text und Symbol können unabhängig eingeblendet werden.
- Vollständiger durchsuchbarer Google-Material-Symbols-Rounded-Katalog (mehr als 4.300 Namen), sortiert, vollständig durchsuchbar und per virtualisiertem Raster ohne manuelle Seitennavigation scrollbar; kuratierte Schnellkategorien und verifizierte Eingabe von Symbolnamen. Freie Suchbegriffe wie „shirt“, „T-Shirt“ und „Kleidung“ liefern das offizielle Symbol `apparel`; `shirt` selbst ist kein offizieller Google-Symbolname. Der Katalog wird von Googles offizieller Codepoints-Liste geladen und sieben Tage lokal zwischengespeichert. Beim allerersten Offline-Start stehen die Favoriten zur Verfügung.
- Live-SVG, anpassbar an die Segmentanzahl: 1–12 volle Inhalte; 13–20 kompakte Inhalte; 21–72 Nummern; darüber reine Segmente. Vollständige Werte bleiben im Editor und beim Gewinnergebnis vorhanden.
- Nur die goldene Radmitte löst die Drehung aus, der Zeiger bleibt feststehend.
- Gewinnerermittlung per zufälliger Auswahl, unabhängig von der Drehkraft; die Animation endet geometrisch beim ausgewählten Sektor.
- Vertikaler, schnell pendelnder Drehkraftbalken (0–100 % in 0,8 Sekunden nach oben und in 0,8 Sekunden nach unten). Nur der Klick auf die goldene Radmitte übernimmt die momentane Kraft. Je nach Kraft macht das Rad 2–10 volle Umdrehungen und läuft unterschiedlich lang aus.
- Die einstellbare maximale Drehdauer beträgt 3–12 Sekunden; bei schwacher Kraft ist die tatsächliche Drehdauer kürzer. Optionaler synthetisierter Klicksound und vier Farbpaletten.
- Präsentationsmodus ohne Editor.
- Automatische Browser-Speicherung über `localStorage`, JSON-Import und JSON-Export.
- Desktop- und Mobilansicht, Fokus-/Tastaturbedienung und reduzierte Animation bei aktiver Betriebssystemeinstellung.

## Technische Hinweise

Das Rad verwendet vektorbasierte Pfade, Licht-/Metallverläufe und goldene Nieten. Seine Geometrie ist unabhängig von der Zahl der Segmente. Für die Ergebnisermittlung wird `crypto.getRandomValues` verwendet, soweit im Browser verfügbar. Die zufällige Zielposition bleibt innerhalb der Grenzen des ausgewählten Segments.

Material Symbols werden mit ihren offiziellen Unicode-Codepoints statt mit Ligaturen angezeigt. Ungültige Symboleinträge werden im Editor abgewiesen; „shirt“ wird auf `apparel` abgebildet, auch bei gespeicherten Konfigurationen. Ein einfaches T-Shirt-SVG dient als lokale Fallbackgrafik für `apparel`. Material Symbols werden über Google Fonts eingebunden. Der Symbolkatalog wird aus der offiziellen Datei `google/material-design-icons/variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints` geladen. Alternative Quelle ist jsDelivr. Symbolnamen **und Codepoints** werden lokal gespeichert; neue Symbole werden beim nächsten Aktualisierungsintervall synchronisiert. **Dafür ist eine Internetverbindung erforderlich.** Wird das externe Symbol-Font blockiert oder offline geöffnet, verwendet die App dekorative Unicode-Fallbacksymbole. Es werden keine Fontdateien mitgeliefert. Die Icons werden von Google unter der **Apache License 2.0** angeboten: https://developers.google.com/fonts/docs/material_icons .

JSON-Import begrenzt einzelne Dateien auf 2 MB und 5.000 Segmente zum Schutz des Browsers; das UI setzt keine feste Segmentobergrenze. Bei sehr großen Zahlen sind die Segmente auf einem realen Bildschirm naturgemäß nicht mehr einzeln lesbar.

Die Konfiguration wird nur im jeweils verwendeten Browser gespeichert, nicht mit anderen Geräten synchronisiert. Für den Wechsel zwischen Geräten dienen JSON-Export und -Import.

## Tests

Browsertests liegen unter `tests/`. Sie benötigen Python mit `playwright` und ein lokales Chromium. Für die Testumgebung wird die externe Fonts-Abfrage deaktiviert, sodass die Offline-Fallbacks mitgetestet werden. Getestet wurden Desktop und Smartphone, 0/1/2/3/8/12/20/21/24/72/73/90/100/220 Segmente, Ergebnis-/Zeigerposition, Bearbeitung, lokale Speicherung, Import/Export und ungültige JSON-Dateien.

## Ausrichtung der Beschriftungen

Text, Material-Symbole und Segmentnummern werden entlang der jeweiligen Segmentachse ausgerichtet. Das Rad stoppt exakt mit der Mitte des Gewinnersegments unter dem Zeiger bei **12 Uhr**. Dadurch ist der Inhalt des Gewinnersegments dort **horizontal und aufrecht lesbar**. Während der Drehung bewegen sich Beschriftungen und Symbole fest mit dem Rad, wie bei einem physischen Glücksrad. Bei mehr als 20 Segmenten wird wegen des begrenzten Platzes die Segmentnummer angezeigt; der vollständige Inhalt steht weiterhin im Editor und im Ergebnis.

## Platzsparende Konfiguration

Die Anwendung startet mit **eingeklapptem Konfigurationsmenü**. Das Glücksrad nutzt die gesamte verfügbare Breite und skaliert nach der Viewport-Höhe. Über **Konfiguration** (Zahnrad auf schmalen Displays) lässt sich ein seitliches Einstellungsmenü öffnen, ohne das Rad zu verkleinern. Der Editor wird durch das Schließen-Symbol, einen Klick außerhalb oder `Escape` geschlossen. Die Symbolauswahl erscheint über dem Editor und bleibt bedienbar. Der Konfigurationsstand wird weiterhin lokal gespeichert; die Sichtbarkeit des Menüs wird bewusst nicht gespeichert.

## Drehkraft und Timing

Der vertikale Kraftbalken pendelt ständig zwischen 0 und 100 Prozent (vollständiger Zyklus 1,6 Sekunden). Beim Klick auf **DREHEN** wird der genaue aktuelle Wert eingefroren. Er bestimmt die Anzahl der vollen Umdrehungen (2–10) und die Dauer (35–100 Prozent der eingestellten maximalen Drehdauer). Die Gewinnwahrscheinlichkeit der Segmente bleibt gleich; die Zielausrichtung wird unabhängig bestimmt und anschließend mathematisch korrekt angefahren. Die Anzeige funktioniert auch im Präsentationsmodus, ohne einen zusätzlichen Startknopf bereitzustellen.
