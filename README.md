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

Der Knopf **Effekt im Vollbild vorführen** schließt vorübergehend die Konfiguration samt abgedunkeltem und weichgezeichnetem Hintergrund. Er zeigt den Effekt am tatsächlichen Rad in einer unverdeckten Vollbildansicht, ohne eine Drehung auszulösen. **Zurück zur Konfiguration** sowie `Escape` bringen die Eingaben und die bisherige Scrollposition wieder zurück. Die Soundvorschau bleibt im Editor. Normale Präsentationsansicht und Gewinnerermittlung sind unverändert.


## Effektvorschau ohne Unschärfe

**Effekt 4 Sekunden vorführen** blendet das seitliche Konfigurationsmenü und dessen
abgedunkelte, weichgezeichnete Überlagerung für vier Sekunden aus. Der Effekt
läuft direkt auf dem unverändert positionierten Glücksrad, ohne Drehung und ohne
Vollbildwechsel. Danach wird das Menü automatisch wiederhergestellt, einschließlich
Scrollposition und Fokus auf dem Vorschauknopf. Mit `Escape` lässt sich die Vorschau
vorzeitig beenden. Während der Vorschau ist die Radmitte gegen unbeabsichtigte
Drehungen gesperrt.


## Effektvorschau bei geöffnetem Editor

Beim Klick auf **Effekt 4 Sekunden vorführen** bleibt das Konfigurationsmenü
geöffnet, mitsamt Scrollposition und Einstellungen. Für vier Sekunden werden
**nur** Abdunklung und Weichzeichnung der Hintergrund-Überlagerung ausgeschaltet.
Die ausgewählte Hervorhebung wird auf dem echten Rad sichtbar, ohne Drehung.
Danach kehrt der Hintergrund automatisch in seinen ursprünglichen Zustand zurück.
`Escape` beendet die Vorschau bei geöffnetem Menü vorzeitig.


## Sechs visuell eigenständige Gewinnerinszenierungen

- **Golden Edge:** Eine Goldspur zeichnet die Sektorkontur mit Leuchtpunkten nach.
- **Casino Spotlight:** Die übrigen Felder werden abgedunkelt, ein beweglicher Scheinwerfer beleuchtet das Gewinnerfeld.
- **Golden Lift:** Das Segment mit Bild und Text hebt sich als 3D-Element aus der Scheibe.
- **Jackpot Lights:** Ein pink-goldenes Lauflicht umrundet die Nieten des Rades; ausgewählte Lichter bleiben stehen.
- **Golden Celebration:** Ein Partikel- und Sternenfeuerwerk bricht aus dem Siegerfeld hervor.
- **Casino Cinematic:** Mehrstufige Inszenierung aus Verdunkelung, Scheinwerfer, animiertem Außenring, Lichtwellen und Ergebnisplakette.

Alle Bewegungen sind endlich, hinterlassen einen eindeutigen Ruhezustand und werden bei der Betriebssystemoption für reduzierte Bewegung deaktiviert. Die Vorschau hält das Konfigurationsmenü offen und nimmt nur für vier Sekunden den Blur vom Rad. Änderungen an den Gewinnerstilen verändern nicht die Gewinnauswahl.

## Design der Bedienelemente

Der Bereich **Gewinnerinszenierung** nutzt abgestimmte Casino-Noir-Selects und einheitliche Vorschau-Buttons mit festem Icon-Bereich, klaren Fokuszuständen, ausreichend großen Touch-Zielen und responsiver Anordnung. Die fehlenden Editor-Styles der vorigen Version wurden wiederhergestellt.

## Reihenfolge per Drag-and-drop ändern

Jede Segmentzeile besitzt links einen eigenen Ziehgriff. Damit lassen sich Segmente mit Maus, Stift oder Finger in eine andere Position ziehen. Die goldene Einfügelinie zeigt die Ablageposition. Beim Loslassen wird die Reihenfolge im SVG-Rad aktualisiert und automatisch lokal gespeichert; Text, Icon und Farbe bleiben zusammen. Bei langen Listen scrollt die Konfiguration am Rand während des Ziehens weiter. Mit fokussiertem Griff ermöglichen auch Pfeil hoch/runter sowie Pos1/Ende eine Sortierung per Tastatur. Die bisherigen Auf-/Ab-Schaltflächen bleiben erhalten. Während einer Drehung ist die Sortierung gesperrt.

## Anheben und Verschieben der Segmente

Mit dem goldenen Ziehgriff lässt sich die **gesamte Segmentkarte aufnehmen**. Sie folgt beim Ziehen dem Mauszeiger, Stift oder Finger, erhält einen deutlichen Schatten und eine leichte 3D-Neigung. An der Einfügeposition entsteht eine **voll hohe Lücke**; die anderen Karten rücken animiert an ihre neue Position. Beim Loslassen gleitet die Karte in den Zielplatz, die Reihenfolge wird sofort am Rad aktualisiert und lokal gespeichert. Abbruch über `Esc` oder Touch-Abbruch verändert nichts. Die bisherigen Pfeiltasten und Auf-/Ab-Schaltflächen bleiben nutzbar. Reduzierte Animationen werden berücksichtigt.

## Semantische Material-Symbol-Suche

Der gesamte aktuelle Rounded-Codepoint-Katalog bleibt durchsuchbar. Zusätzlich lädt die Symbolauswahl beim Öffnen den lokal mitgelieferten **icon-search-index.json** (3.946 Icons mit offiziellen englischen Tags und Beliebtheitswerten aus einem Snapshot der Google-Metadaten). Icons, die im neueren Font vorhanden sind, aber nicht im Suchindex, bleiben selbstverständlich per Symbolname auffindbar. Die Trefferrangfolge berücksichtigt Originalnamen, exakte Tags, Teiltreffer und Beliebtheit. Bei `shirt` erscheinen `apparel` und `laundry`. Die bisherige deutsche Synonymhilfe bleibt ergänzend erhalten. Der vollständige lokale Suchindex vermeidet eine Laufzeitabhängigkeit von einer undokumentierten Google-Such-API; GitHub Pages liefert ihn als statische Datei aus. Beim Standalone-Build wird er eingebettet, damit dieselbe Suche ohne externen Metadatenserver funktioniert. Google Fonts wird weiter nur für die Icon-Glyphen verwendet. Quelle: Google Material Symbols-Metadaten, Snapshot aus `timmaffett/material_symbols_icons`, Apache-2.0. Der Suchindex wird bei Bedarf durch Aktualisierung der Quelldaten erneuert; eine 1:1-Identität mit Googles interner Suche ist nicht zugesichert.
