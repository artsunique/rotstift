---
name: slopwaechter
description: Entfernt KI-typische Schreibmuster aus deutschen Texten. Linten, umschreiben, von einem fremden Modell gegenlesen lassen, erneut linten. Nutze diesen Skill, wenn ein deutscher Text nach Mensch klingen soll — Landingpages, Newsletter, Blogposts, Produkttexte, Stellenanzeigen, E-Mails.
---

# slopwaechter

Deutscher Text rein, deutscher Text raus, der nicht nach Sprachmodell klingt.

Der Linter hat das erste und das letzte Wort. Er ist ehrlich, das Modell ist
überzeugend. „Weitgehend sauber" ist der Weg, auf dem eine Seite am Ende
klingt wie jede andere KI-Seite im Netz.

## Die Schleife

```
1. LINTEN     tools/deslop_de.py    Score /6, rot unter 6. Regex, keine Meinung.
2. UMSCHREIBEN  drei Durchgänge     Wörter → Satzformen → eine Person einsetzen
3. GEGENLESEN  tools/cleanse.sh     ein fremdes Modell entfernt, was das erste schrieb
4. NACHLINTEN  tools/deslop_de.py   erst bei 6/6 raus damit
```

## Schritt 1 — Linten

```bash
python3 tools/deslop_de.py entwurf.md
```

Lies die Ausgabe vollständig, bevor du irgendetwas änderst. Jede Fundstelle
kommt mit Begründung und Ersatzvorschlag. Die Gruppe **Menschliche Signale**
ist die wichtigste und die einzige, die misst, was *fehlt*.

## Schritt 2 — Umschreiben, in drei getrennten Durchgängen

Nicht alles auf einmal. Jeder Durchgang hat eine Aufgabe.

**Durchgang A — die Wörter.** Jede Fundstelle aus *KI-Vokabular* ersetzen.
Nicht durch ein Synonym, sondern durch das, was gemeint war. „Maßgeschneiderte
Lösungen" wird nicht zu „individuellen Lösungen", sondern zu „Wir bauen die
Schnittstelle auf euer Warenwirtschaftssystem".

**Durchgang B — die Satzformen.** *KI-Satzschablonen* und *Deutschspezifische
Tells*. Nominalstil auflösen, Genitivketten trennen, Amtsdeutsch rauswerfen,
aufzählende Absatzanfänge streichen. „Die Umsetzung der Optimierung der
Abläufe" wird zu „Wir bauen die Abläufe um".

**Durchgang C — eine Person einsetzen.** Das ist der Durchgang, den die
meisten Humanizer auslassen, und der einzige, der den Text gut macht statt
nur sauber. Konkret:

- Mindestens ein **aber** dort, wo der Text wirklich dreht. Nicht „jedoch".
- Satzlängen auseinanderziehen. Ein langer Satz, dann ein kurzer. So.
- Eine Einschätzung, die ein Modell nicht hätte: was der Autor nicht anbietet,
  was schiefgehen kann, was er anders macht als die anderen.
- Eine überprüfbare Einzelheit statt eines Superlativs. Ein Datum, eine Stadt,
  eine Zahl, ein Name.

## Schritt 3 — Gegenlesen durch ein fremdes Modell

```bash
tools/cleanse.sh entwurf.md > gereinigt.md
```

Die Regel: Der Reinigungsdurchgang läuft auf einer **anderen Modellfamilie**
als der Entwurf. Familien haben verschiedene Akzente, und kein Modell hört
seinen eigenen. Ein Modell, das die eigene Arbeit korrigiert, ist genau das,
was dieser Schritt verhindert.

Ist keine zweite CLI da, gibt das Skript den Prompt aus, den du in den anderen
Chat kopierst.

## Schritt 4 — Nachlinten, immer

```bash
python3 tools/deslop_de.py gereinigt.md
```

Ein starkes Modell entfernt Tells zuverlässig und baut dabei gern neue ein.
Unter 6/6 geht nichts raus.

## Die eine harte Regel

**Nie Belege erfinden.** Keine Kundenzahlen, keine Bewertungen, keine
Erfahrungsjahre, die niemand nachgezählt hat. Fehlt eine Zahl, schreib
`[Zahl fehlt]` und mach weiter. Der Gewinn aus einer erfundenen Zahl ist
kleiner als der Gewinn aus echter Konkretheit, und es ist der eine Fehler
ohne Rückweg. In Deutschland kommt dazu, dass unbelegte Marktbehauptungen
wettbewerbsrechtlich angreifbar sind.

Und: Dieser Skill verspricht nicht, KI-Detektoren zu überlisten. Detektoren
sind Rauschen. Das Ziel ist das Bauchgefühl eines menschlichen Lesers.

## Was der Score nicht sagt

6/6 heißt „keine bekannten Muster". Es heißt nicht „guter Text". Ein flacher,
belangloser Text besteht mühelos. Der Linter ist ein Gitter, kein Lektorat.

## Ohne Terminal

Läuft der Skill in einer Oberfläche ohne Dateizugriff, arbeite den Katalog
`references/katalog.json` gedanklich ab, Gruppe für Gruppe, und melde Score
und Fundstellen im selben Format. Die Gruppe *Menschliche Signale* prüfst du
dann von Hand: Kommt „aber" vor? Schwanken die Satzlängen? Steht irgendwo
eine eigene Sicht?
