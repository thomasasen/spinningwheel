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
- Die einstellbare maximale Drehdauer beträgt 3–30 Sekunden; bei schwacher Kraft ist die tatsächliche Drehdauer kürzer. Optionaler synthetisierter Klicksound und vier Farbpaletten.
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

## Auslaufspannung und Gewinnhervorhebung

Die **maximale Drehdauer** ist zwischen 3 und 30 Sekunden konfigurierbar. Wie bisher skaliert die tatsächlich gewählte Dauer mit dem beim Klick abgefangenen Kraftwert (35–100 % der eingestellten Obergrenze). Zusätzlich steuert **Auslaufspannung** (0–100 %, Standard: 65 %) die Bremskurve unabhängig von der Dauer: Niedrige Werte bremsen früher stark, hohe Werte bewegen das Rad noch bis kurz vor Schluss langsam über Segmentgrenzen. Die Abbremsung ist stetig und monoton; es gibt keinen künstlichen Nachrück-Sprung und keinen manipulierten Gewinner.

Nach jedem Stillstand erhält der echte Gewinnersektor eine pulsierende Goldkontur mit leichtem Highlight. Die Hervorhebung bleibt bis zur nächsten Drehung oder Segmentänderung sichtbar; bei reduzierter Animation ohne Pulsieren. Die JSON-Konfiguration enthält nun `coast`, ältere Konfigurationen verwenden den Standardwert 65.

## Radgeometrie: kleiner Zeiger und außenliegende Beschriftungen

Der feststehende Auswahlzeiger ist kürzer und schmaler; seine Spitze reicht im
640×640-SVG nur bis circa Radius 240 statt bisher 210. Inhalte werden je nach
Segmentanzahl in größere Radien gelegt: 190 bei bis zu 8 Segmenten, 198 bei
9–12 Segmenten, 204 bei 13–20 Segmenten und 220 für Nummern bei 21–72
Segmenten. Das lässt mehr freie Fläche um die Radnabe und verhindert, dass
Zeiger, Schrift und Symbole bei der 12-Uhr-Position überlagern.

## Gewinnerinszenierung und Sounds

Im Konfigurationsmenü stehen sechs Hervorhebungen zur Verfügung: Golden Edge (Kontur), Casino Spotlight (Abdunklung der anderen Segmente), Golden Lift (3D-Anhebung), Jackpot Lights (laufende Randbeleuchtung), Golden Celebration (Goldpartikel) und Casino Cinematic (Kontur + Spotlight + Lichter). Die Effektstärke lässt sich als Dezent, Edel oder Show festlegen. Der Button **Effekt vorführen** demonstriert die Auswahl ohne Drehung. Die Hervorhebung folgt stets dem tatsächlichen Gewinnersegment im SVG, bleibt nach dem Stopp sichtbar und ignoriert Zeiger-/Mausklicks. Bei reduzierter Bewegung werden die Animationen deaktiviert.

Gewinner-Sounds: Keiner, Sanfter Ton, Casino-Glocke, Goldener Dreiklang, Jackpot und Show-Fanfare. Eine **Sound anhören**-Taste spielt den gewählten Effekt direkt ab. Alle Tonfolgen sind original synthetisiert mit der Web Audio API; es werden keine externen Sounddateien benötigt. Das mechanische Zeigerklicken kann unabhängig davon ein- oder ausgeschaltet werden. Gewinnerstil, -stärke und Sound werden lokal gespeichert und beim JSON-Export/-Import berücksichtigt.

## Unverdeckte Effektvorschau

Der Knopf **Effekt im Vollbild vorführen** schließt vorübergehend das Konfigurationsmenü samt abgedunkeltem und weichgezeichnetem Hintergrund. Die gewählte Gewinneranimation läuft auf dem echten, unverdeckten Rad ohne Drehung. **Zurück zur Konfiguration** sowie `Escape` öffnen den Editor erneut an seiner bisherigen Scrollposition. Die Soundvorschau bleibt im Editor. Der normale Präsentationsmodus bleibt unverändert.


## Effektvorschau ohne Unschärfe

**Effekt 4 Sekunden vorführen** blendet das seitliche Konfigurationsmenü und dessen
abgedunkelte, weichgezeichnete Überlagerung für vier Sekunden aus. Der Effekt
läuft direkt auf dem unverändert positionierten Glücksrad, ohne Drehung und ohne
Vollbildwechsel. Danach wird das Menü automatisch wiederhergestellt, einschließlich
Scrollposition und Fokus auf dem Vorschauknopf. Mit `Escape` lässt sich die Vorschau
vorzeitig beenden. Während der Vorschau ist die Radmitte gegen unbeabsichtigte
Drehungen gesperrt.

## Effektvorschau bei geöffnetem Editor

Beim Klick auf **Effekt 4 Sekunden vorführen** bleibt das Konfigurationsmenü geöffnet, einschließlich Scrollposition und Einstellungen. Für vier Sekunden werden **nur Abdunklung und Blur der Hintergrund-Überlagerung** ausgeschaltet. Die gewählte Gewinneranimation wird direkt am Rad gezeigt, ohne eine Drehung. Danach kehren Abdunklung und Blur automatisch zurück. `Escape` beendet die Vorschau vorzeitig. Während der Vorschau ist die Radmitte gegen unbeabsichtigte Drehungen gesperrt.
