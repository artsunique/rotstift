# Rotstift

**Stop the slop – auf Deutsch.** Ein Linter für Floskeln, Nominalstil und
leere Behauptungen in deutschen Texten, egal ob sie aus einem Sprachmodell
stammen oder aus der eigenen Feder.

Linten, umschreiben, von einer fremden Modellfamilie gegenlesen lassen, erneut
linten. Für Landingpages, Newsletter, Produkttexte, Stellenanzeigen, also
alles, was ein Mensch liest und beurteilt.

Die lautesten Tells im Deutschen gibt es im Englischen gar nicht: Nominalstil,
Genitivketten, Amtsdeutsch, aufzählende Absatzanfänge. Und der stärkste ist
eine Abwesenheit. Ein deutscher Text ohne ein einziges **aber**, der
stattdessen auf „jedoch" und „allerdings" ausweicht, klingt fast immer nach
Maschine.

## Wofür das gedacht ist

Slop ist Text, in dem nichts steht. Den gab es lange vor den Sprachmodellen:
Nominalstil, Amtsdeutsch und Genitivketten füllen seit Jahrzehnten
Geschäftsberichte. Die Modelle haben diese Muster aus solchen Texten gelernt
und setzen sie heute häufiger als jeder Mensch. Deshalb funktioniert der
Linter bei eigenen Texten genauso. Er fragt nicht, wer geschrieben hat, sondern
ob da etwas steht.

Das Ziel ist ein besserer Text, kein unauffälligerer. Die meisten Korrekturen
machen einen Text überprüfbarer: das Gründungsjahr statt „langjährige
Erfahrung", eine gemessene Zahl statt „deutlich schneller". Erfundene Belege
sind die einzige harte Regel. KI-Detektoren zu überlisten verspricht dieses
Projekt ausdrücklich nicht. Detektoren sind Rauschen, das Ziel ist das
Bauchgefühl eines menschlichen Lesers.

Verhindern lässt sich trotzdem nicht, dass jemand damit einen KI-Text als
eigenen ausgibt. Aber wo Offenlegung verlangt ist (in der Hausarbeit, in der
Redaktion, bei einer gesetzlichen Kennzeichnungspflicht), ersetzt ein Score
von 6/6 sie nicht.

## Die Schleife

```
1. LINTEN      tools/deslop_de.py   Score /6, rot unter 6. Regex, keine Meinung.
2. UMSCHREIBEN drei Durchgänge      Wörter → Satzformen → eine Person einsetzen
3. GEGENLESEN  tools/cleanse.sh     fremde Modellfamilie räumt auf
4. NACHLINTEN  tools/deslop_de.py   erst bei 6/6 raus damit
```

Der Linter hat das erste und das letzte Wort, weil er ehrlich ist und das
Modell überzeugend.

## Schnellstart

```bash
git clone https://github.com/artsunique/rotstift && cd rotstift

# einen Satz prüfen
python3 tools/deslop_de.py --text "Nicht nur schnell, sondern auch nahtlos."
# → Score 5/6, benennt beide Tells, Exit 1

# eine Datei prüfen
python3 tools/deslop_de.py texte/landingpage.md

# eine gebaute Seite prüfen (liest nur, was ein Besucher sieht)
python3 tools/deslop_de.py index.html

# Zahlen sind belegbar? Gruppe blockiert nicht mehr, Fundstellen bleiben sichtbar
python3 tools/deslop_de.py index.html --belege-ok

# Entwurf von der anderen Modellfamilie gegenlesen lassen
tools/cleanse.sh entwurf.md > gereinigt.md && python3 tools/deslop_de.py gereinigt.md

# Regel geändert? Das hier fängt einen halbblinden Katalog
python3 tools/test_deslop_de.py
```

Keine Abhängigkeiten. Der Linter ist reines Python aus der Standardbibliothek,
offline, ohne Modellaufruf. Das Cleanse-Skript braucht eine KI-CLI (`claude`,
`codex` oder `gemini`) — oder keine, dann gibt es den Prompt zum Kopieren aus.

## Nachweis statt Behauptung

Ein echter Durchlauf an einem typischen deutschen KI-Absatz:

|  | Score |
| --- | --- |
| Wie das Modell es ausgab | **2/6** — `nahtlos`, `Mehrwert`, „nicht nur … sondern auch", zwei Genitivketten |
| Nach einem Durchlauf | **6/6** — Aussage unverändert, Länge im Rahmen, nichts erfunden |

Jeder Befehl mit seiner Ausgabe: [`beispiele/durchlauf.md`](beispiele/durchlauf.md).

## Die sechs Gruppen

Je ein Punkt. Voller Katalog mit Fundstellen und Ersatzvorschlägen:
[`references/katalog.json`](references/katalog.json).

1. **KI-Vokabular** — `nahtlos`, `ganzheitlich`, `maßgeschneidert`, `Mehrwert`,
   `Potenzial entfalten`, `Reise`. Zwei Stufen: Wörter ohne normale Bedeutung
   werden über den Wortstamm gefangen, Wörter mit echter Fachbedeutung
   (`effizient`, `innovativ`) zählen nur halb — damit „Die Anlage ist effizient
   ausgelegt: 0,8 kWh pro Kilogramm" sauber bleibt.
2. **KI-Satzschablonen** — „nicht nur X, sondern auch Y" (der lauteste Tell
   überhaupt), „Genau hier kommt … ins Spiel", „In der heutigen schnelllebigen
   Geschäftswelt", selbstbeantwortete Fragen. 18 Formen.
3. **Deutschspezifische Tells** — Amtsdeutsch, Nominalstil, Genitivketten,
   `jedoch` statt `aber`, aufzählende Absatzanfänge, gestapeltes Passiv.
4. **Satzzeichen und Rhythmus** — zwei Gedankenstriche in einem Satz,
   Gedankenstrich als Listenzeichen, Dreiergruppen, Emojis. Dreiergruppen
   werden nur bei kleingeschriebenen Gliedern gezählt, weil deutsche
   Substantivlisten („Eiche, Esche und Buche") völlig normal sind.
5. **Erfundene Belege** — Zahl neben Nomen, Erfahrungsjahre, Marktführer-
   Behauptungen. Absichtlich streng: ein Fehlalarm kostet zehn Sekunden, eine
   erfundene Zahl die Glaubwürdigkeit — in Deutschland zusätzlich mit
   wettbewerbsrechtlichem Risiko.
6. **Menschliche Signale** — die Umkehrprüfung, und die eigentliche Neuerung
   hier. Sie misst nicht, was dasteht, sondern was fehlt: kein einziges „aber",
   zu gleichförmige Satzlängen, keine erste Person. Greift ab 120 Wörtern,
   bei anderen Textsorten früher (siehe unten).

## Textsorten

Gruppe 6 braucht Text, um etwas messen zu können. Unterhalb der Schwelle wurde
sie bisher still als bestanden verbucht — eine Über-mich-Seite mit 75 Wörtern
bekam 6/6, ohne dass je jemand nach dem fehlenden „aber" gesehen hätte. Genau
die Textsorten, die Kunden zuerst prüfen lassen, waren die ungeprüften.

`--textsorte` verschiebt die Schwelle und schaltet einzelne Metriken ab:

```
python3 tools/deslop_de.py --textsorten          # zeigt, was der Katalog kennt

python3 tools/deslop_de.py ueber-mich.md --textsorte profil
python3 tools/deslop_de.py claim.txt   --textsorte kurz
```

| Sorte      | Stimme ab | abgeschaltet    | wofür                                           |
| ---------- | --------- | --------------- | ----------------------------------------------- |
| `standard` | 120 W     | —               | Landingpage, Blogpost, Newsletter, Angebot      |
| `profil`   | 90 W      | `s-ich-wir`     | Über-mich-Seite, Unternehmensprofil, Pressetext |
| `kurz`     | 45 W      | `s-satzlaengen` | Claim, Hero, Social-Post, Betreffzeile          |

`profil` nimmt die Ich-Prüfung raus, weil ein Text in der dritten Person sie
nicht bestehen kann und sonst dauerhaft bei 5/6 deckelt. Die eigene Sicht muss
trotzdem irgendwo stehen — als Einwand, Abgrenzung oder Bedingung. Das prüft
kein Regex.

Was nicht geprüft werden konnte, steht jetzt in der Ausgabe:

```
[ uebersprungen ] Menschliche Signale (Umkehrpruefung)
       Metriken nicht geprueft, 75 < 120 Woerter

Score 6/6 · 1 ungeprueft (stimme)
```

Eigene Sorten kommen wie eigene Regeln in `references/katalog.json`, unter
`textsorten`. Ein Tippfehler im Namen bricht ab, statt stillschweigend auf
`standard` zurückzufallen — sonst prüft man monatelang das Falsche.

## Als Skill einbinden

### Claude Code

Der kürzeste Weg, weil kein Upload nötig ist:

```bash
git clone https://github.com/artsunique/rotstift ~/.claude/skills/rotstift
```

Neue Sitzung starten, dann `/rotstift` oder einfach „Rotstift über die
Landingpage". Für ein Projekt statt für alle: nach `.claude/skills/` im Repo
klonen, dann liegt der Skill im Git-Verlauf des Projekts und alle im Team haben
ihn.

### claude.ai und Claude Desktop

Voraussetzung ist ein Plan mit Codeausführung (Pro, Max, Team, Enterprise).
Erst *Einstellungen → Funktionen → Codeausführung und Dateierstellung*
einschalten — ohne das bleibt das Skills-Menü ausgegraut, und zwar unabhängig
vom Plan. Bei Team und Enterprise kann nur ein Owner den Schalter umlegen.

Dann ZIP bauen:

```bash
cd rotstift
zip -r ../rotstift.zip . -x '.git/*' '.DS_Store' '**/__pycache__/*'
```

Hochladen unter *Anpassen → Skills → +*. Wird das ZIP abgewiesen, liegt es fast
immer daran, dass `SKILL.md` nicht dort liegt, wo Claude sie sucht: sie gehört
auf die oberste Ebene des Archivs. Der Finder packt beim Rechtsklick den
Ordner *mit* ein und schiebt damit alles eine Ebene tiefer — deshalb der
Befehl oben mit `cd` und `.` statt `zip -r rotstift.zip rotstift`.

Anschließend im Chat: „Nutze Rotstift auf diesen Text". Weil Skills hier
ohnehin Codeausführung voraussetzen, läuft `deslop_de.py` in der Sandbox
wirklich — Claude rät den Score nicht, sondern misst ihn und kann iterieren,
bis 6/6 steht. Was dort nicht geht, ist `tools/cleanse.sh`: die Sandbox hat
keine zweite KI-CLI. Das Gegenlesen machst du von Hand, indem du den Entwurf
in einen Chat einer anderen Modellfamilie gibst und danach **erneut lintest**.

Ein Update ist kein Update, sondern ein zweiter Upload derselben Datei — die
alte Fassung vorher löschen, sonst hast du zwei.

### ChatGPT

Ein Skills-System wie bei Claude gibt es dort nicht. Zwei Wege, die
funktionieren:

**Custom GPT.** `SKILL.md` und `references/katalog.json` als Wissensdateien
hochladen, `tools/deslop_de.py` dazu. In die Instructions einen Satz, der den
Ablauf auslöst: „Bei deutschen Texten den Ablauf aus SKILL.md befolgen, den
Linter mit Code Interpreter ausführen, Score und Fundstellen ausgeben."
Code Interpreter muss aktiv sein, sonst wird nur geraten.

**Einzelner Chat.** Die drei Dateien in den Chat ziehen und schreiben: „Führe
deslop_de.py auf dem Text unten aus und halte dich an SKILL.md." Ohne Upload
geht es auch, dann arbeitet das Modell den Katalog von Hand ab — es findet
dann weniger und schätzt den Score. Der Abschnitt *Ohne Terminal* in
`SKILL.md` beschreibt genau diesen Fall.

### Codex und andere Agenten

Den Agenten auf `SKILL.md` im Repo zeigen lassen, oder den Pfad in `AGENTS.md`
aufnehmen. `SKILL.md` und der Katalog enthalten nichts Claude-Spezifisches;
der Linter braucht nur `python3` aus der Standardbibliothek.

### Was du unabhängig vom Weg merken solltest

Der Skill läuft **nur auf ausdrückliche Bitte**. Er lintet nichts, was das
Modell gerade selbst geschrieben hat, und hängt keine Score-Zeile unter normale
Antworten. Das ist Absicht: ein Linter, der sich ungefragt einmischt, wird
abgeschaltet.

## Eigene Regeln

`references/katalog.json` ist reines JSON, kein Python nötig. Eine Regel:

```json
{
  "id": "v-eigenes",
  "muster": "\\bhochkar(ae|ä)tig\\w*",
  "hinweis": "Superlativ ohne Beleg.",
  "ersatz": "Streichen oder belegen.",
  "gewicht": 1.0,
  "case": false
}
```

Danach `python3 tools/test_deslop_de.py`. Die Testdatei enthält eine Liste
echter deutscher Sätze, die *nicht* anschlagen dürfen — das ist die Hälfte,
die zählt. Ein Linter mit Fehlalarmen wird abgeschaltet, und dann schützt er
gar nichts mehr.

## Die eine harte Regel

**Nie Belege erfinden.** Keine Kundenzahlen, keine Bewertungen, keine
Erfahrungsjahre, die niemand nachgezählt hat. Fehlt eine Zahl, schreib
`[Zahl fehlt]` und mach weiter.

## Was 6/6 nicht heißt

Es heißt „keine bekannten Muster", nicht „guter Text". Ein flacher, belangloser
Text besteht mühelos. Ein Rotstift streicht an, was auffällt. Ob der Text gut
ist, weiß er nicht. Wer nur gegen die Wortliste optimiert, schreibt in zwei
Jahren den nächsten erkennbaren Einheitssound.

Bevor du es ausprobierst: Diese README fällt auf dem eigenen Linter durch, weil
sie jeden Tell zitiert, den sie dokumentiert. Lass ihn über deine Texte laufen,
nicht über den Katalog, der die Texte beschreibt.

## Worauf das aufbaut

Alle Quellen in [`references/quellen.md`](references/quellen.md). Kurz: die
Schleifen-Architektur und die Idee des gegenlesenden Fremdmodells stammen von
[SlopMonster](https://github.com/ItsssssJack/SlopMonster), der deutsche
Musterkatalog und die „aber"-Beobachtung von
[klartext](https://github.com/severinschweiger/klartext), das editierbare
Regelformat von [ai-text-cleaner](https://pypi.org/project/ai-text-cleaner/).
Alle drei MIT.

Für englische Texte gibt es
[stop-slop](https://github.com/hardikpandya/stop-slop) von Hardik Pandya, einen
verbreiteten Skill mit ähnlichem Ziel. Rotstift ist kein Fork davon, sondern
setzt dort an, wo englische Regeln im Deutschen nicht greifen.

MIT. Wie das, worauf es steht.
