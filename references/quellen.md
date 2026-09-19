# Quellen

Dieses Projekt ist eine Zusammenführung, keine Neuerfindung. Was von wo kommt:

## Code und Architektur

- **[SlopMonster](https://github.com/ItsssssJack/SlopMonster)** (MIT) — die
  Vier-Schritt-Schleife, der Gedanke, dass ein deterministischer Linter das
  erste und letzte Wort haben muss, und die Regel, dass der Reinigungsdurchgang
  auf einer fremden Modellfamilie laufen muss. Englisch.
- **[klartext](https://github.com/severinschweiger/klartext)** (MIT, Severin
  Schweiger) — der deutsche Musterkatalog, insbesondere die deutschspezifischen
  Tells: Nominalstil, Genitivketten, Amtsdeutsch, aufzählende Absatzanfänge und
  die Beobachtung zur Abwesenheit von „aber".
- **[ai-text-cleaner](https://pypi.org/project/ai-text-cleaner/)** (PyPI) — das
  Muster, Regeln in einer externen, editierbaren Datei zu halten statt im Code,
  und die Zweistufigkeit aus deterministischen Regeln plus optionalem
  Modelldurchgang.
- **[KI-Detektor von Schübeler Consulting](https://schuebeler-consulting.de/ki-detektor/)**
  — die Idee, jede Fundstelle mit einer Begründung auszugeben statt nur zu
  markieren, und die Kategorie der Lehnübersetzungen aus dem Englischen.

## Eigene Ergänzungen

Nicht aus den obigen Quellen übernommen, sondern hier hinzugekommen:

- Die Gruppe **Menschliche Signale** als messbare Umkehrprüfung: „aber"-Quote,
  Variationskoeffizient der Satzlängen, Abwesenheit der ersten Person. klartext
  beschreibt das „aber"-Signal, prüft es aber nicht maschinell.
- **Gewichtung** von Tier-2-Vokabular, damit Fachwörter wie „effizient" in
  technischen Texten keinen Fehlalarm auslösen.
- **Groß-/Kleinschreibung als Merkmal** bei Dreiergruppen — im Deutschen trennt
  das Adjektivketten („schneller, einfacher und besser") sauber von normalen
  Substantivaufzählungen („Eiche, Esche und Buche"). Im Englischen gibt es
  diese Unterscheidung nicht.
- Die Belege-Gruppe berücksichtigt, dass unbelegte Marktbehauptungen in
  Deutschland wettbewerbsrechtlich angreifbar sind, nicht nur unglaubwürdig.

## Bewusst nicht verwendet

Werkzeuge, die damit werben, KI-Detektoren zu umgehen. Detektoren sind
unzuverlässig, gegen sie zu optimieren ist Zeitverschwendung, und im
akademischen Umfeld ist es Täuschung.
