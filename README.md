# Casino Noir – konfigurierbares Glücksrad

Eine statische, responsive Glücksrad-Web-App im Casino-Noir-Stil. Das Rad besteht vollständig aus SVG und wird für jede Segmentanzahl neu berechnet. Es gibt **keine fest eingebrannte Segmentgrafik**.

## Start

- **Einfach:** `casino-noir-standalone.html` im Browser öffnen. Dieses Dokument enthält HTML, CSS und JavaScript vollständig eingebettet.
- **Für GitHub Pages:** `index.html`, `styles.css`, `wheel-physics.js` und `app.js` ins Stammverzeichnis der gewünschten Branch legen und GitHub Pages dafür aktivieren. Es wird kein Build-Schritt benötigt.
- **Lokal mit Webserver:** Im Ordner `python -m http.server 8000` starten und `http://localhost:8000` öffnen.

## Funktionen

- Segmente hinzufügen, löschen, duplizieren und nach oben/unten sortieren; auch ein leeres Rad wird unterstützt.
- Pro Segment eigene Farbe, Text und/oder Symbol; Text und Symbol können unabhängig eingeblendet werden.
- Vollständiger durchsuchbarer Google-Material-Symbols-Rounded-Katalog (mehr als 4.300 Namen), sortiert, vollständig durchsuchbar und per virtualisiertem Raster ohne manuelle Seitennavigation scrollbar; kuratierte Schnellkategorien und verifizierte Eingabe von Symbolnamen. Freie Suchbegriffe wie „shirt“, „T-Shirt“ und „Kleidung“ liefern das offizielle Symbol `apparel`; `shirt` selbst ist kein offizieller Google-Symbolname. Der Katalog wird von Googles offizieller Codepoints-Liste geladen und sieben Tage lokal zwischengespeichert. Beim allerersten Offline-Start stehen die Favoriten zur Verfügung.
- Live-SVG, anpassbar an die Segmentanzahl: 1–12 volle Inhalte; 13–20 kompakte Inhalte; 21–72 Nummern; darüber reine Segmente. Vollständige Werte bleiben im Editor und beim Gewinnergebnis vorhanden.
- Nur die goldene Radmitte löst die Drehung aus. Der Zeiger sitzt an einem festen Gelenk und federt bei Segmentkontakten sichtbar mit.
- Standardmäßig entsteht der Gewinner erst durch mechanisches Auslaufen; optional bleibt eine ausdrücklich gekennzeichnete, vorab gewichtete Ziehung verfügbar.
- Vertikaler Drehkraftbalken: Der Klick auf die goldene Radmitte übernimmt den momentanen Kraftwert. Im Physikmodus verändert er den Anfangsimpuls, nicht eine vorher festgelegte Umdrehungszahl.
- Einstellbarer Dauer- bzw. Trägheitsrichtwert (3–30 Sekunden): Im Physikmodus entsteht die tatsächliche Auslaufzeit dynamisch; im gewichteten Modus wird die Drehdauer gezielt gesteuert. Optionaler synthetisierter Klicksound und vier Farbpaletten.
- Präsentationsmodus ohne Editor.
- Automatische Browser-Speicherung über `localStorage`, JSON-Import und JSON-Export.
- Desktop- und Mobilansicht, Fokus-/Tastaturbedienung und reduzierte Animation bei aktiver Betriebssystemeinstellung.

## Technische Hinweise

Das Rad verwendet vektorbasierte Pfade, Licht-/Metallverläufe und goldene Nieten. Seine Geometrie ist unabhängig von der Zahl der Segmente. Im Physikmodus ergibt sich der Gewinner aus dem Endwinkel der Simulation. `crypto.getRandomValues` liefert dort lediglich natürliche Streuungen des Startimpulses und der Reibung. Im gezielt gewichteten Modus dient der kryptografische Zufallswert der Auswahl des Gewinnersegments, dessen Mitte anschließend angefahren wird.

Material Symbols werden mit ihren offiziellen Unicode-Codepoints statt mit Ligaturen angezeigt. Ungültige Symboleinträge werden im Editor abgewiesen; „shirt“ wird auf `apparel` abgebildet, auch bei gespeicherten Konfigurationen. Ein einfaches T-Shirt-SVG dient als lokale Fallbackgrafik für `apparel`. Material Symbols werden über Google Fonts eingebunden. Der Symbolkatalog wird aus der offiziellen Datei `google/material-design-icons/variablefont/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].codepoints` geladen. Alternative Quelle ist jsDelivr. Symbolnamen **und Codepoints** werden lokal gespeichert; neue Symbole werden beim nächsten Aktualisierungsintervall synchronisiert. **Dafür ist eine Internetverbindung erforderlich.** Wird das externe Symbol-Font blockiert oder offline geöffnet, verwendet die App dekorative Unicode-Fallbacksymbole. Es werden keine Fontdateien mitgeliefert. Die Icons werden von Google unter der **Apache License 2.0** angeboten: https://developers.google.com/fonts/docs/material_icons .

JSON-Import begrenzt einzelne Dateien auf 2 MB und 5.000 Segmente zum Schutz des Browsers; das UI setzt keine feste Segmentobergrenze. Bei sehr großen Zahlen sind die Segmente auf einem realen Bildschirm naturgemäß nicht mehr einzeln lesbar.

Die Konfiguration wird nur im jeweils verwendeten Browser gespeichert, nicht mit anderen Geräten synchronisiert. Für den Wechsel zwischen Geräten dienen JSON-Export und -Import.

## Tests

Browsertests liegen unter `tests/`. Sie benötigen Python mit `playwright` und ein lokales Chromium. Für die Testumgebung wird die externe Fonts-Abfrage deaktiviert, sodass die Offline-Fallbacks mitgetestet werden. Getestet wurden Desktop und Smartphone, 0/1/2/3/8/12/20/21/24/72/73/90/100/220 Segmente, Ergebnis-/Zeigerposition, Bearbeitung, lokale Speicherung, Import/Export und ungültige JSON-Dateien.

## Ausrichtung der Beschriftungen

Text, Material-Symbole und Segmentnummern werden entlang der jeweiligen Segmentachse ausgerichtet. Im standardmäßigen Physikmodus ergibt sich die Endposition frei aus dem Auslauf, also auch **innerhalb** eines Segments und nicht zwingend in dessen Mitte. Die Texte und Symbole drehen sich fest mit dem Rad und sind für die Segmentmitte bei 12 Uhr ausgerichtet. Nur im ausdrücklich gewählten Modus „Gezielte Gewichtung“ wird die Mitte des vorab gezogenen Segments angefahren. Während der Drehung bewegen sich Beschriftungen und Symbole fest mit dem Rad, wie bei einem physischen Glücksrad. Bei mehr als 20 Segmenten wird wegen des begrenzten Platzes die Segmentnummer angezeigt; der vollständige Inhalt steht weiterhin im Editor und im Ergebnis.

## Platzsparende Konfiguration

Die Anwendung startet mit **eingeklapptem Konfigurationsmenü**. Das Glücksrad nutzt die gesamte verfügbare Breite und skaliert nach der Viewport-Höhe. Über **Konfiguration** (Zahnrad auf schmalen Displays) lässt sich ein seitliches Einstellungsmenü öffnen, ohne das Rad zu verkleinern. Der Editor wird durch das Schließen-Symbol, einen Klick außerhalb oder `Escape` geschlossen. Die Symbolauswahl erscheint über dem Editor und bleibt bedienbar. Der Konfigurationsstand wird weiterhin lokal gespeichert; die Sichtbarkeit des Menüs wird bewusst nicht gespeichert.

## Drehkraft, Reibung und Gewinnhervorhebung

Der Kraftbalken pendelt zwischen 0 und 100 Prozent (Zyklus: 1,6 Sekunden). Der Klick auf **DREHEN** übernimmt den aktuellen Wert. Im standardmäßigen Physikmodus gibt er einen Anfangsimpuls vor; daraus folgen variable Umdrehungszahl und Stoppposition. Lagerreibung, geschwindigkeitsabhängiger Widerstand und Zeigerkontakte reduzieren die Rotationsenergie bis zum Stillstand. Bei geringem Tempo ist ein kleines Zurückprallen möglich. Nahe am Stillstand nimmt die Lagerreibung kontinuierlich ab. Derselbe Segmentstift erzeugt durch minimale Vor-/Zurückbewegungen nicht mehrfach einen neuen Aufprall. Es gibt **keine vorberechnete Zielposition**.

Die Einstellung **Drehträgheit** (3–30 Sekunden) skaliert die Reibungskoeffizienten. Die tatsächlich erlebte Auslaufzeit ist nicht exakt vorgegeben. **Auslaufspannung** steuert zusätzlich die Widerstände: Größere Werte bedeuten weniger Reibung und im Mittel längeres Auslaufen. Beim gezielt gewichteten Modus greifen dagegen weiterhin die ursprüngliche feste Zeitkurve und die Zahl der Umdrehungen (2–10), damit das vorher gezogene Ergebnis erreicht wird.

Erst wenn die Winkelgeschwindigkeit 400 Millisekunden lang unter 0,05°/s liegt, gilt das Rad als stillstehend. Ein Zeitlimit erzwingt keinen abrupten Stopp. **Erst danach** wird der Gewinner aus dem zuletzt erreichten Winkel bestimmt. Nach dem Stillstand erhält der ermittelte Sektor die gewählte Goldkontur bzw. Gewinnerinszenierung. Die Hervorhebung bleibt bis zum nächsten Spin oder einer Änderung sichtbar; bei reduzierter Bewegung ohne Pulsieren.

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


## Gewichtete Ziehung, Radmechanik und mehrere gespeicherte Räder

Die Funktionen sind in der modularen und der eigenständigen HTML-Version enthalten. Die automatisierte Qualitätssicherung wird unter GitHub Actions dokumentiert.

### Zwei klar getrennte Drehmechaniken

**Echter Auslauf (Physik, Standard):** Das Rad erhält einen geschwindigkeitsabhängigen Startimpuls. Ein numerisches Bewegungsmodell berücksichtigt Lagerreibung, Luftwiderstand und den Energieverlust bei Segmentkontakten. Langsame Kontakte können das Rad kurz zurückprallen lassen. Der Gewinner wird **erst nach vollständigem Stillstand** aus der tatsächlichen Winkelposition ermittelt. Es gibt kein vorab ausgewähltes Ergebnis, kein Zielsegment und keinen künstlichen Korrektursprung. Die Dauer kann von der gewählten Drehträgheit abweichen; der Zahlenwert ist in diesem Modus nur ein Richtwert.

Das Modell ist eine **physikalisch motivierte Näherung**, kein messtechnisch kalibrierter digitaler Zwilling eines bestimmten Glücksrads. Die Resultate sind von Startimpuls, Winkel, Reibung und Zeigerkontakten abhängig. Die Trefferpositionen verteilen sich über die Sektoren und sind nicht auf die Mitte festgelegt.

- Bei **gleich großen Sektoren** sind die Chancen im mechanischen Modus näherungsweise gleich, auch wenn unterschiedliche Gewichte gespeichert sind.
- Bei **proportionalen Sektoren** legen die Gewichte die sichtbaren Winkelgrößen fest. Ein Segmentgewicht von 0 erzeugt keine Fläche. Die tatsächlichen Trefferhäufigkeiten können wegen mechanischer Wechselwirkungen von den geometrischen Anteilen abweichen. Die im Editor angezeigten Prozentwerte sind deshalb mit „≈“ gekennzeichnet.
- Ein Rad mit lauter Gewichten 0 kann im gleich großen mechanischen Modus trotzdem drehen. Der physikalische Auslauf hängt ausschließlich von der dargestellten Geometrie ab.

**Gezielte Gewichtung (alternativ):** Hier bleibt die bisherige exakte Ziehung erhalten. Gewicht 1, 3 und 0 bedeutet exakt 25 %, 75 % und 0 %, unabhängig von der Sektorgröße. Der kryptografische Zufallswert bestimmt den Gewinner *vorab*. Anschließend wird die Drehung zur Mitte dieses Gewinnersegments animiert. Das ist bewusst **keine freie Physiksimulation**, sondern die ausdrücklich gewählte Option für vorgegebene Gewinnchancen. Bei Gesamtgewicht 0 kann keine gewichtete Ziehung starten.

Das Umschalten unter **Spiel & Darstellung → Drehmechanik** und der ausgewählte Modus werden im jeweiligen Profil und im JSON-Export gespeichert. Frühere Konfigurationen ohne diese Angabe werden zum Standard „Echter Auslauf (Physik)“ migriert; ihre Gewichte und übrigen Einstellungen bleiben erhalten.

### Untersegmente, Rastpunkte und kürzeres Zurückpendeln

Jedes sichtbare Gewinnsegment wird standardmäßig in **sieben mechanische Rastabschnitte** eingeteilt. Bei acht Segmenten entstehen so 56 regelmäßig verteilte, goldene Außenpunkte mit passenden feinen Teilungsstrichen. Die Einstellung **Unterteilungen je Segment** erlaubt Werte von 1 bis 12. Sowohl die sichtbaren Nieten als auch die tatsächlichen Zeigerkontakte verwenden dieselbe Winkelgeometrie. Bei sehr vielen Segmenten wird die Anzahl der Nieten automatisch auf maximal 336 begrenzt, damit Darstellung und Simulation performant bleiben.

Ein langsamer Kontakt darf das Rad weiterhin ein kleines Stück zurückdrücken. Die rückwärts gerichtete Bewegung unterliegt jedoch einer deutlich stärkeren Ratschen- und Lagerdämpfung. Derselbe Rastpunkt erzeugt beim Zurückpendeln keinen zweiten künstlichen Schlag. Das Rad kommt dadurch nach dem letzten Kontakt schneller zur Ruhe, ohne sofort auf eine vorberechnete Position zu springen. Auch dann wird der Sieger erst nach der Stillstandsprüfung aus dem tatsächlich erreichten Winkel bestimmt.

**Wichtig:** Die feinen Rastabschnitte sind mechanische Unterteilungen, **keine zusätzlichen Gewinner**. Jedes konfigurierte Hauptsegment bleibt ein einziges Gewinnfeld. Die Gewinnwahrscheinlichkeiten des gewichteten Modus ändern sich nicht, und auch die Anzahl der Gewinner im Physikmodus bleibt gleich.

### Einraststärke und die Frage nach dem letzten Klick

Der Regler **Einraststärke** (0–100 %, Standard 50 %) beeinflusst im Modus **Echter Auslauf (Physik)** den Widerstand der letzten Rastpunkte. **Sanft** bedeutet eine kleinere mechanische Energiebarriere; das langsam drehende Rad kann damit leichter noch den nächsten Punkt überwinden. **Kräftig** erhöht die Energiebarriere und führt bei identischer Restgeschwindigkeit eher zu einem kleinen gedämpften Rückprall statt zu einem weiteren Rastschritt. Zwischenwerte ermöglichen das typische „reicht es noch für einen Klick?“.

Jeder Kontakt prüft die tatsächlich vorhandene Winkelgeschwindigkeit und reduziert die Rotationsenergie durch die modellierte Zeigermechanik. Es wird **weder ein Gewinner vorab ausgesucht noch eine zusätzliche Rastbewegung künstlich ausgelöst**. Ein Wert von 0 % garantiert ebenso wenig einen weiteren Klick wie 100 % ein bestimmtes Gewinnerfeld. Stärke und Rastpunktgeometrie wirken zusammen mit Startimpuls, Reibung und der bestehenden Zeigerfederung. Nach einem Rückprall wird die Rückwärtsbewegung weiterhin stärker und kontinuierlich gedämpft; das Ergebnis erscheint erst nach nachgewiesenem Stillstand. Die Einstellung wird mit jedem Profil im Browser und bei JSON-Export/-Import gespeichert; ältere Profile erhalten den Standardwert 50 %. Der Modus **Gezielte Gewichtung** ignoriert diesen Regler, damit seine exakten Gewinnwahrscheinlichkeiten unverändert bleiben.

### Zeiger und Klickgeräusche

Der sichtbare Zeiger schwingt bei Segmentkontakten um ein festes SVG-Gelenk. Federung, Dämpfung und Ausschlag sind einstellbar. Vier Web-Audio-Klickcharaktere sind verfügbar: Casino, mechanisch, Ratsche und Metall. Über **Zeigerfederung vorführen** lässt sich die Bewegung bei geöffnetem Editor ohne Hintergrundunschärfe prüfen. Bei aktivierter Systemeinstellung „Bewegung reduzieren“ wird die lange Drehbewegung übersprungen und die Zeigeranimation unterdrückt; die physikalische Simulation bestimmt das Ergebnis weiterhin.

### Mehrere Glücksräder

Unter **Gespeicherte Glücksräder** kann man neue Räder erstellen, bestehende kopieren, umbenennen, laden und löschen. Der Browser hält bis zu 100 Profile in `localStorage` unter `casino-noir-wheel-profiles-v2`; das frühere `casino-noir-wheel-studio-v1` bleibt für die Migration verfügbar. Alle Änderungen werden automatisch gespeichert. Import akzeptiert ältere Einzelkonfigurationen, neue Einzelprofile oder Bündel. Man kann als neue Konfiguration importieren oder (bei einer einzelnen Konfiguration) das aktuell geladene Profil ersetzen. Export ist einzeln oder als Sammlung möglich. Speicherfehler erscheinen als Warnung im Kopfbereich.

`localStorage` ist für textbasierte Einstellungen ausreichend; Bilddateien und Mediendateien werden nicht gespeichert. Diese Daten sind geräte- und browsergebunden. Ein JSON-Export ist deshalb die empfohlene zusätzliche Sicherung. Ein fehlgeschlagener Import wird vor einem Profilwechsel geprüft und darf die gespeicherten Konfigurationen nicht verändern.

### Prüfung

`node --check app.js` prüft JavaScript-Syntax. `tests/weighted-browser.mjs` prüft mit Playwright-Chromium die Darstellungsmodi, 100.000 Ziehungen mit gewichteten Verhältnissen und Nullgewichten, den Stopp und das Wiederherstellen mehrerer Profile. Zusätzlich simuliert `tests/physics-browser.mjs` 350 mechanische Ausläufe ohne Zielsektor und verifiziert im Browser die Endwinkel-Ergebnisermittlung. `tests/pointer-browser.mjs` kontrolliert die sichtbare Zeigerbewegung. Die GitHub-Actions-Definition liegt unter `.github/workflows/casino-noir-ci.yml`. Die Chromium-Regression umfasst die modulare und die Standalone-Version sowie gewichtete Stichproben. Wie bei jedem modellierten Bewegungsablauf ersetzt das keine physikalische Messung an einem realen Glücksrad.
