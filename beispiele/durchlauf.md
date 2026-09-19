# Ein Durchlauf, ungekuerzt

Ein typischer deutscher KI-Absatz, durch die Schleife geschickt. Beide Texte
sind fast gleich lang (107 gegen 112 Woerter), es wurde nichts erfunden und
nichts Inhaltliches weggelassen.

|  | Score |
| --- | --- |
| `vorher.md`, wie das Modell es ausgab | **2/6** |
| `nachher.md`, nach den drei Durchgaengen | **6/6** |

## Was der Linter im Vorher fand

**KI-Vokabular**, Last 6 bei Schwelle 2 -> Punkt verloren

- Z4 „nahtlos“ — Klassischer Lehnuebersetzungs-Tell von 'seamless'.
- Z8 „ganzheitlichen“ — Leerformel, sagt nie, was enthalten ist.
- Z3 „maßgeschneiderten“ — Behauptet Individualitaet, statt sie zu zeigen.
- Z4 „Mehrwert“ — Beratersprech, ersetzt den konkreten Nutzen.
- Z16 „Potenzial entfalten“ — Uebersetztes 'unlock your potential'.
- Z10 „effizient“ — Tier 2: in technischen Texten legitim, in Werbetexten leer.
- Z15 „entscheidender“ — Tier 2: Bedeutungs-Inflation.

**KI-Satzschablonen**, Last 3 bei Schwelle 1 -> Punkt verloren

- Z10 „Genau hier kommt unsere langjährige Expertise ins Spiel“ — 'That's where X comes in'.
- Z2 „In der heutigen schnelllebigen Geschäftswelt“ — Der haeufigste KI-Einstieg im Deutschen.
- Z15 „Lassen Sie uns gemeinsam“ — 'Let us' — im Deutschen ungebraeuchlich ausserhalb von KI-Text.

**Deutschspezifische Tells**, Last 4 bei Schwelle 3 -> Punkt verloren

- Z9 „Umsetzung der“ — Nominalstil: das Verb ist im Substantiv verschwunden.
- Z9 „Optimierung der“ — Nominalstil: das Verb ist im Substantiv verschwunden.
- Z9 „der Optimierung der internen“ — Genitivkette. Zwei Genitive hintereinander bremsen jeden Satz aus.
- Z7 „Darüber hinaus“ — Aufzaehlender Absatzanfang. Drei davon machen aus Text eine Liste in Prosaform.

**Satzzeichen und Rhythmus**, Last 1 bei Schwelle 2

- Z10 „transparent, effizient und zuverlässig“ — Dreiergruppe aus Adjektiven oder Verben. Eine ist Rhetorik, zwei auf einer Seite sind eine Maschine.

**Erfundene Belege**, Last 1 bei Schwelle 1 -> Punkt verloren

- Z13 „Über 10.000 zufriedene Kunden“ — Zahl neben Nomen. Belegbar?

## Die drei Durchgaenge im Einzelnen

**A, die Woerter.** „Maßgeschneiderte Lösungen integrieren sich nahtlos“ sagt
nicht, was passiert. Ersetzt durch das, was tatsächlich gebaut wird: die
Schnittstelle zwischen Warenwirtschaft und Angebotsvorlage.

**B, die Satzformen.** „Die Umsetzung der Optimierung der internen Abläufe
erfolgt“ wurde zu „Das dauert etwa sechs Wochen“. Drei Nominalisierungen und
eine Genitivkette weniger, dafür ein Zeitraum, den man nachhalten kann.

**C, die Person.** Der Vorher-Text hat keine Haltung. Der Nachher-Text sagt,
was die Firma *nicht* macht und wann Software gar nicht hilft. Das ist der
Absatz, den ein Modell von sich aus nie schreibt, und der einzige, dem ein
Leser glaubt.

## Reproduzieren

```bash
python3 tools/deslop_de.py beispiele/vorher.md
python3 tools/deslop_de.py beispiele/nachher.md
```
