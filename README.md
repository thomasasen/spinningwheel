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
- Gewinnerermittlung anhand konfigurierbarer Segmentgewichte mit kryptografischem Zufall, unabhängig von der Drehkraft; die Animation endet geometrisch in der Mitte des ausgewählten Sektors.
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


## Mehrere Glücksräder und Gewinnchancen (Version 2)

Die Konfiguration wird weiterhin über **Konfiguration** rechts oben geöffnet und bleibt beim Start geschlossen. Oben im Menü befindet sich **Gespeicherte Glücksräder**. Über **Neu** legst du ein zusätzliches Rad mit eigenen Einstellungen an. **Duplizieren**, **Umbenennen**, **Löschen** und **Speichern** verwalten die gewählte Variante. Die Auswahlliste lädt ein anderes Rad, ohne dessen Segmentreihenfolge, Darstellung, Sounds oder Effekte mit anderen Rädern zu vermischen. Bearbeitungen werden automatisch lokal gesichert. Ein Speicherfehler erscheint oben als Warnung und verhindert einen ungesicherten Profilwechsel.

Jedes Segment hat jetzt ein **Gewicht** (Standard: `1`). Die individuelle Gewinnchance ist

`Chance = Gewicht / Summe aller positiven Gewichte × 100 %`.

Beispiel: Gewichte `1 / 3 / 2 / 4` ergeben **10 / 30 / 20 / 40 %**. Gewicht `0` schließt ein Segment von der Ziehung aus. Sind alle Gewichte `0`, wird **DREHEN** gesperrt. Nur endliche Werte von `0` bis `1.000.000` sind gültig; negative, nicht numerische und unendlich große Werte werden nicht angenommen.

Unter **Gewinnwahrscheinlichkeiten** gibt es zwei Darstellungen:

- **Gleich große Segmente**: Wie bisher nehmen alle Felder gleich viel Platz auf dem Rad ein. Die tatsächlichen Chancen stehen ausdrücklich in der Segmentliste und hängen trotzdem von den Gewichten ab. Gleiche Fläche bedeutet in dieser Ansicht **nicht** gleiche Gewinnchance.
- **Proportionale Segmente**: Der Winkel eines Felds entspricht der hinterlegten Chance. Bei `40 %` nimmt das Segment `144°` ein. Felder mit Gewicht `0` haben keinen sichtbaren Winkel, bleiben jedoch in der Liste bearbeitbar. Winzige Segmente werden aus Lesbarkeitsgründen nicht innen beschriftet.

**Drehkraft ist nicht Gewinnchance.** Der bewegte Kraftbalken beeinflusst ausschließlich Drehdauer und Anzahl der Umdrehungen. Der Gewinner wird vorher unabhängig davon anhand der Gewichte mit `crypto.getRandomValues` ermittelt. Der Radwinkel läuft ohne nachträgliche Korrektur kontinuierlich zur tatsächlichen Sektormitte. Der Auswahlzeiger stimmt dadurch auch bei proportionaler Darstellung mit der Gewinneranzeige überein.

## Realistische Bewegung und Klang

Die neue Animation verwendet `requestAnimationFrame`. Nach einer kurzen Beschleunigungsphase sinkt die Winkelgeschwindigkeit stetig. **Auslaufspannung** bleibt der einzige Regler für das Bremsprofil (0 %: frühes Abbremsen, 100 %: langes langsames Auslaufen). Die maximal einstellbare Drehdauer beträgt weiterhin **30 Sekunden**. Unter **Zeigermechanik und Klickklang** stehen folgende Einstellungen:

- **Zeigerfederung** steuert die Geschwindigkeit, mit der der Zeiger in die Ruheposition zurückkehrt.
- **Zeigerdämpfung** regelt das Nachschwingen.
- **Zeigerausschlag** bestimmt die Stärke der mechanischen Kontaktreaktion.
- **Mechanischer Klang** bietet *Dezent*, *Klassische Ratsche*, *Massiver Metallzeiger* und *Casino*. Mit **Klang vorhören** lässt sich der ausgewählte Sound testen. Gewinner-Sounds sind davon unabhängig.

Die Zeigerbewegung folgt einem numerisch integrierten, gedämpften Feder-Masse-Modell. Kontakte werden zusammengefasst, wenn viele Segmentgrenzen in sehr kurzer Zeit vorbeilaufen; so kann die Browseranimation nicht durch Tausende gleichzeitige Audioereignisse überlastet werden. Alle Töne werden direkt mit der Web Audio API synthetisiert, es werden keine Sounddateien übertragen. Bei aktivierter Systemeinstellung `prefers-reduced-motion` werden rasche Radumdrehungen und das Zeigernachschwingen vermieden.

## Speicherung, Export, Import und Datenschutz

Die App speichert vollständige Profile unter `casino-noir-wheel-studio-workspace-v2` im **localStorage** des jeweiligen Browsers, ohne Benutzerkonto und ohne Upload. Ein zusätzliches Abbild des aktiven Rads bleibt unter dem bisherigen Schlüssel `casino-noir-wheel-studio-v1`. Existiert noch keine Profilsammlung, liest die App beim ersten Öffnen diese ältere Einzelradkonfiguration ein. Fehlende Gewichte werden zu `1`, neue Physikparameter erhalten Standardwerte. Ein Import älterer JSON-Dateien aus Version 1 ist möglich.

Mit **Aktuelles Rad exportieren** erhältst du ein JSON mit sämtlichen Segmenten, IDs, Texten, Symbolen, Farben, Gewichten, Dreh- und Zeigereinstellungen, Gewinnerinszenierung und Sounds. **Alle Räder exportieren** schreibt eine Sammlung. Beide enthalten die Formatversion `2` und einen Datumsstempel im Dateinamen. Beim Import wählst du vorher **Aktives Glücksrad ersetzen** oder **Als neues Glücksrad anlegen**. Sammlungen importieren mehrere Profile und erkennen vorhandene IDs beziehungsweise Namen im Ersetzen-Modus. Vor der Speicherung wird die gesamte Datei geprüft; ein ungültiger Datensatz verwirft den gesamten Import, ohne vorhandene Profile zu überschreiben.

**Wichtig:** Browserdaten sind geräte- und browserprofilabhängig. Bei gelöschten Websitedaten oder privatem Browsen können sie verschwinden. Sichere wichtige Räder zusätzlich per **Alle Räder exportieren**. `localStorage` reicht für typische Textkonfigurationen aus; bei extrem vielen großen Rädern kann das Browserlimit greifen. In diesem Fall erscheint eine Speicherwarnung, und ein Profilwechsel wird blockiert, bis die Änderungen gesichert werden können. Der Google-Material-Symbol-Katalog wird unabhängig davon wie bisher gecacht.

## Tests und technische Entscheidungen

Der Workflow `.github/workflows/casino-noir-qa.yml` erstellt zunächst die eigenständige HTML-Fassung mit `python build_standalone.py` und testet sie mit Playwright/Chromium. `tests/test_probabilities_and_profiles.py` führt mindestens **600.000 Ziehungen** aus: Gleichverteilung, Gewichtung, ausgeschlossene Felder, ein einziges Gewinnfeld, viele Felder und ein Extremverhältnis. Die Toleranz orientiert sich an sechs Standardabweichungen der jeweiligen Binomialverteilung (zusätzlich mindestens drei Ziehungen); Zufallsschwankungen werden dadurch sinnvoll berücksichtigt. Hinzu kommen Tests für Radgeometrie, korrekte Gewinnerposition, Konfigurationswechsel, Export/Import, ungültige JSON-Dateien, Speicherfehler und mobiles Layout. Bestehende Tests prüfen etwa Winner-Effekte, Material-Symbolsuche, Auslaufspannung und Drehkraft.

Zum lokalen Testen: `pip install playwright`, `python -m playwright install chromium`, `python build_standalone.py`, danach `python tests/test_probabilities_and_profiles.py`. Zusätzlich die weiteren Python-Tests im Ordner `tests` ausführen. Der eigenständige Build und die GitHub-Pages-Version nutzen dieselben Quell-Dateien. Der Arbeitsstand soll nur nach erfolgreich durchlaufener Browser- und Regressions-QS veröffentlicht werden.

**Bekannte Grenzen:** Sehr viele Segmente reduzieren zwangsläufig die Lesbarkeit im Rad (ab 73 Segmenten ohne Innenbeschriftungen); extrem kleine proportionale Winkel werden nicht mit Text überzeichnet. Die Genauigkeit gewichteter Ziehungen basiert auf 53 Zufallsbits und doppeltgenauer JavaScript-Arithmetik. Bei höchstens 5.000 Segmenten mit Gewichten bis 1.000.000 ist die Summe deutlich kleiner als `Number.MAX_SAFE_INTEGER`.
