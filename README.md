# slopwächter

**Deutsche Texte, die nicht nach Sprachmodell klingen.**

Linten, umschreiben, von einer fremden Modellfamilie gegenlesen lassen, erneut
linten. Für Landingpages, Newsletter, Produkttexte, Stellenanzeigen — alles,
was ein Mensch liest und beurteilt.

Kein Port eines englischen Humanizers. Die lautesten Tells im Deutschen gibt
es im Englischen gar nicht: Nominalstil, Genitivketten, Amtsdeutsch,
aufzählende Absatzanfänge. Und der allerstärkste ist eine Abwesenheit — ein
deutscher Text ohne ein einziges **aber**, der stattdessen auf „jedoch" und
„allerdings" ausweicht, ist fast immer maschinell.

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
git clone https://github.com/<dein-account>/slopwaechter && cd slopwaechter

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
   zu gleichförmige Satzlängen, keine erste Person. Greift ab 120 Wörtern.

## Als Skill einbinden

**Claude (Web):** Ordner als ZIP herunterladen, in claude.ai unter *Anpassen →
Skills → Skill hochladen* einspielen. Dann: „Nutze slopwächter auf diesen Text".

**Claude Code:** `git clone … ~/.claude/skills/slopwaechter`, dann
`/slopwaechter`. Hier kann Claude den Linter selbst ausführen und so lange
iterieren, bis 6/6 steht — der eigentliche Gewinn.

**ChatGPT / Codex:** `SKILL.md` und `references/katalog.json` als Wissensdateien
in einen Custom GPT, oder den Agenten auf `SKILL.md` zeigen lassen. Der Skill
enthält nichts Claude-Spezifisches.

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

Und dieses Projekt verspricht nicht, KI-Detektoren zu überlisten. Detektoren
sind Rauschen. Das Ziel ist das Bauchgefühl eines menschlichen Lesers.

## Was 6/6 nicht heißt

Es heißt „keine bekannten Muster", nicht „guter Text". Ein flacher, belangloser
Text besteht mühelos. Der Linter ist ein Gitter, kein Lektorat. Wer nur gegen
die Wortliste optimiert, schreibt in zwei Jahren den nächsten erkennbaren
Einheitssound.

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

MIT. Wie das, worauf es steht.
