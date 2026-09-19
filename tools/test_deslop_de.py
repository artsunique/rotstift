#!/usr/bin/env python3
"""
Regressionstests fuer den Katalog.

Nach jeder Regelaenderung laufen lassen:

    python3 tools/test_deslop_de.py

Die zweite Haelfte ist die wichtigere: echter deutscher Text darf nicht
anschlagen. Ein Linter mit Fehlalarmen wird abgeschaltet, und dann
schuetzt er gar nichts mehr.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deslop_de import KATALOG_DEFAULT, pruefe, punktzahl  # noqa: E402

with open(KATALOG_DEFAULT, "r", encoding="utf-8") as fh:
    KATALOG = json.load(fh)


def treffer_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for ergebnis in pruefe(text, KATALOG):
        for treffer in ergebnis.treffer:
            ids.add(treffer.regel_id)
    return ids


def harte_treffer_ids(text: str) -> set[str]:
    """Nur Regeln mit vollem Gewicht. Tier-2-Woerter duerfen als Hinweis
    erscheinen, ohne einen sauberen Satz zu verurteilen."""
    ids: set[str] = set()
    for ergebnis in pruefe(text, KATALOG):
        for treffer in ergebnis.treffer:
            if treffer.gewicht >= 1.0:
                ids.add(treffer.regel_id)
    return ids


# ------------------------------------------------------- muss anschlagen

FAENGT = [
    ("k-nicht-nur", "Das ist nicht nur schnell, sondern auch sicher."),
    ("k-nicht-nur", "Wir liefern nicht nur Technik, sondern auch Beratung."),
    ("k-heutige-zeit", "In der heutigen schnelllebigen Geschäftswelt zählt Tempo."),
    ("k-ins-spiel", "Genau hier kommt unsere Plattform ins Spiel."),
    ("k-wichtig-zu", "Es ist wichtig zu beachten, dass die Frist läuft."),
    ("k-selbstfrage", "Warum ist das relevant? Ganz einfach: weil es Zeit spart."),
    ("k-zusammenfassend", "Zusammenfassend lässt sich sagen, dass sich der Umbau lohnt."),
    ("k-lassen-sie-uns", "Lassen Sie uns gemeinsam starten."),
    ("v-nahtlos", "Die Anbindung erfolgt nahtlos."),
    ("v-nahtlos", "Eine nahtlose Integration in Ihre Systeme."),
    ("v-massgeschneidert", "Maßgeschneiderte Lösungen für Ihren Betrieb."),
    ("v-mehrwert", "Das schafft echten Mehrwert."),
    ("v-eintauchen", "Tauchen wir ein in die Details."),
    ("v-reise", "Begleiten Sie uns auf Ihrer digitalen Reise."),
    ("v-bahnbrechend", "Eine bahnbrechende Neuerung."),
    ("v-bahnbrechend", "Das revolutioniert die Branche."),
    ("d-amtsdeutsch", "Hierbei ist die Frist zu beachten."),
    ("d-nominalstil", "Die Umsetzung der Strategie beginnt im Mai."),
    ("d-genitivkette", "Im Rahmen der Optimierung der Prozesse der Abteilung."),
    ("d-jedoch", "Das Ergebnis war gut, jedoch spät."),
    ("d-absatzstart", "Darüber hinaus senkt es die Kosten."),
    ("c-bullet-gedankenstrich", "– erster Punkt\n– zweiter Punkt"),
    ("b-kundenzahl", "Über 10.000 zufriedene Kunden vertrauen uns."),
    ("b-erfahrung", "Seit über 20 Jahren Erfahrung im Dachdeckerhandwerk."),
    ("b-superlativ-markt", "Der führende Anbieter der Region."),
]

# ------------------------------------------------------- darf NICHT anschlagen
# Echte deutsche Saetze, wie sie in Kundentexten vorkommen.

SAUBER = [
    "Wir decken Dächer, seit 2001, und nichts anderes.",
    "Das Handwerk lernt man nicht in vier Wochen.",
    "Der Kessel läuft mit 24 kW und heizt 180 Quadratmeter.",
    "Ruf an, wir schauen uns das an, und dann sagen wir dir was es kostet.",
    "Die Anlage ist effizient ausgelegt: 0,8 kWh pro Kilogramm.",
    "Wir bauen Treppen aus Eiche, Esche und Buche.",
    "Der Termin steht, aber das Material fehlt noch.",
    "Sie erreichen uns montags bis freitags von 7 bis 17 Uhr.",
    "Innovativ ist hier nichts — der Aufbau ist seit vierzig Jahren derselbe.",
    "Die Reise nach Basel dauert vierzig Minuten.",
]

# Gegenprobe: ein ganzer Slop-Absatz muss deutlich durchfallen.

SLOP_ABSATZ = """
In der heutigen schnelllebigen Geschäftswelt gewinnt die Digitalisierung
zunehmend an Bedeutung. Unsere maßgeschneiderten Lösungen integrieren sich
nahtlos in bestehende Prozesse und schaffen echten Mehrwert für Ihr
Unternehmen. Dabei setzen wir nicht nur auf modernste Technologie, sondern
auch auf persönliche Betreuung.

Darüber hinaus profitieren Sie von einer ganzheitlichen Betrachtung Ihrer
Anforderungen. Die Umsetzung der Optimierung der internen Abläufe erfolgt
dabei stets transparent, effizient und zuverlässig. Genau hier kommt unsere
langjährige Expertise ins Spiel.

Über 10.000 zufriedene Kunden vertrauen bereits auf uns. Zusammenfassend
lässt sich sagen, dass die digitale Transformation Ihres Unternehmens von
entscheidender Bedeutung ist. Lassen Sie uns gemeinsam den nächsten Schritt
gehen und Ihr Potenzial entfalten.
"""

# Gegenprobe andersherum: echter, gut geschriebener deutscher Text muss 6/6 holen.

MENSCH_ABSATZ = """
Wir decken Dächer. Seit 2001, im Umkreis von dreißig Kilometern um
Schopfheim, und nichts anderes. Kein Bad, keine Heizung, keine Photovoltaik
nebenbei.

Das klingt nach wenig. Es heißt aber, dass wir bei einem Sturmschaden am
Dienstag da sind und nicht in drei Wochen, weil wir nicht gleichzeitig vier
Gewerke jonglieren. Zwei Kolonnen, sechs Leute, ich fahre selbst mit raus.

Was kostet ein Dach? Kommt drauf an, und jeder der dir am Telefon eine Zahl
nennt, rät. Wir schauen es uns an. Das dauert eine halbe Stunde und kostet
nichts. Danach kriegst du ein Angebot, auf dem jede Position steht, die wir
verbaut haben werden. Ruf einfach an.
"""


def main() -> int:
    fehler: list[str] = []

    for regel_id, satz in FAENGT:
        if regel_id not in treffer_ids(satz):
            fehler.append(f"BLIND   {regel_id} greift nicht bei: {satz!r}")

    for satz in SAUBER:
        ids = harte_treffer_ids(satz)
        if ids:
            fehler.append(f"FEHLALARM {sorted(ids)} bei sauberem Satz: {satz!r}")
        for ergebnis in pruefe(satz, KATALOG):
            if not ergebnis.bestanden:
                fehler.append(f"FEHLALARM Gruppe {ergebnis.titel} faellt bei: {satz!r}")

    slop_score, _ = punktzahl(pruefe(SLOP_ABSATZ, KATALOG))
    if slop_score > 2:
        fehler.append(f"ZU MILD  Slop-Absatz erreicht {slop_score}/6, erwartet <= 2")

    mensch = pruefe(MENSCH_ABSATZ, KATALOG)
    mensch_score, gesamt = punktzahl(mensch)
    if mensch_score < gesamt:
        offen = [
            f"{e.titel}: " + ", ".join(t.regel_id + f' („{t.fundstelle}“)' for t in e.treffer)
            for e in mensch
            if not e.bestanden
        ]
        fehler.append(f"ZU STRENG Menschentext erreicht {mensch_score}/{gesamt}: {offen}")

    if fehler:
        print(f"\n  {len(fehler)} Problem(e):\n")
        for eintrag in fehler:
            print(f"    {eintrag}")
        print()
        return 1

    geprueft = len(FAENGT) + len(SAUBER) + 2
    print(f"\n  alles gruen — {geprueft} Faelle, {len(KATALOG['gruppen'])} Gruppen\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
