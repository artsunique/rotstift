#!/usr/bin/env python3
"""
slopwaechter - Linter fuer KI-typische Schreibmuster in deutschen Texten.

Nur Standardbibliothek. Keine Abhaengigkeiten, kein Netz, kein Modell.
Der Linter hat das erste und das letzte Wort, weil er ehrlich ist
und das Modell ueberzeugend.

    python3 tools/deslop_de.py --text "Nicht nur schnell, sondern auch nahtlos."
    python3 tools/deslop_de.py texte/landingpage.md
    python3 tools/deslop_de.py index.html --belege-ok
    python3 tools/deslop_de.py ueber-mich.md --textsorte profil
    python3 tools/deslop_de.py entwurf.md --json

Exit 0 ab der Mindestpunktzahl (Default 6/6), sonst 1.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser

KATALOG_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references",
    "katalog.json",
)

# Default der Textsorte "standard". Jede Textsorte im Katalog darf ihn senken.
MIN_WOERTER_STIMME = 120
MAX_TREFFER_PRO_REGEL = 8
TEXTSORTE_DEFAULT = "standard"

FARBEN = {
    "rot": "\033[31m",
    "gelb": "\033[33m",
    "gruen": "\033[32m",
    "grau": "\033[90m",
    "fett": "\033[1m",
    "aus": "\033[0m",
}


def faerbe(text: str, farbe: str, aktiv: bool) -> str:
    if not aktiv:
        return text
    return f"{FARBEN[farbe]}{text}{FARBEN['aus']}"


# ---------------------------------------------------------------- HTML


class SichtbarerText(HTMLParser):
    """Zieht nur das heraus, was ein Besucher auch sieht."""

    UNSICHTBAR = {"script", "style", "head", "title", "meta", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.teile: list[str] = []
        self._tiefe = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.UNSICHTBAR:
            self._tiefe += 1

    def handle_endtag(self, tag):
        if tag in self.UNSICHTBAR and self._tiefe > 0:
            self._tiefe -= 1

    def handle_data(self, data):
        if self._tiefe == 0 and data.strip():
            self.teile.append(data.strip())

    def text(self) -> str:
        return "\n".join(self.teile)


def lade_text(pfad: str) -> str:
    with open(pfad, "r", encoding="utf-8", errors="replace") as fh:
        roh = fh.read()
    if pfad.lower().endswith((".html", ".htm")):
        parser = SichtbarerText()
        parser.feed(roh)
        return parser.text()
    return roh


# ---------------------------------------------------------------- Modell


@dataclass
class Treffer:
    gruppe: str
    regel_id: str
    fundstelle: str
    zeile: int
    hinweis: str
    ersatz: str
    gewicht: float = 1.0


@dataclass
class Gruppenergebnis:
    schluessel: str
    titel: str
    schwelle: int
    treffer: list[Treffer] = field(default_factory=list)
    uebersprungen: bool = False
    notiz: str = ""

    @property
    def last(self) -> float:
        return sum(t.gewicht for t in self.treffer)

    @property
    def bestanden(self) -> bool:
        if self.uebersprungen:
            return True
        return self.last < self.schwelle


# ---------------------------------------------------------------- Hilfen


def zeile_von(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def saetze(text: str) -> list[str]:
    ohne_md = re.sub(r"(?m)^\s*(#{1,6}|[-*+]|\d+\.)\s+", "", text)
    roh = re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ])", ohne_md)
    return [s.strip() for s in roh if len(s.split()) >= 3]


def woerter(text: str) -> list[str]:
    return re.findall(r"\b[\wÄÖÜäöüß]+\b", text)


# ---------------------------------------------------------------- Metriken


def pruefe_metriken(
    text: str,
    metriken: list[dict],
    gruppe: str = "stimme",
    min_woerter: int = MIN_WOERTER_STIMME,
) -> list[Treffer]:
    treffer: list[Treffer] = []
    alle_woerter = woerter(text)
    if len(alle_woerter) < min_woerter:
        return treffer

    for metrik in metriken:
        if metrik.get("typ") != "gedankenstrich_dichte":
            continue
        striche = len(re.findall(r"[\u2013\u2014]", text))
        je_1000 = 1000 * striche / len(alle_woerter)
        if je_1000 >= metrik.get("schwelle_je_1000", 25):
            treffer.append(Treffer(gruppe, metrik["id"],
                f"{striche} Gedankenstriche, {je_1000:.0f} je 1000 Woerter", 1,
                metrik["hinweis"], metrik["ersatz"], float(metrik.get("gewicht", 1.0))))

    satzliste = saetze(text)
    klein = text.lower()

    for metrik in metriken:
        typ = metrik.get("typ")

        if typ == "aber_quote":
            aber = len(re.findall(r"\baber\b", klein))
            ausweich = len(
                re.findall(r"\b(jedoch|allerdings|nichtsdestotrotz|gleichwohl|indes)\b", klein)
            )
            if aber == 0 and ausweich >= 1:
                treffer.append(
                    Treffer(
                        "stimme",
                        metrik["id"],
                        f"0x 'aber', {ausweich}x Ausweichform",
                        1,
                        metrik["hinweis"],
                        metrik["ersatz"],
                    )
                )

        elif typ == "satzlaengen_varianz":
            laengen = [len(s.split()) for s in satzliste]
            if len(laengen) >= 6:
                mittel = statistics.mean(laengen)
                vk = statistics.pstdev(laengen) / mittel if mittel else 1.0
                if vk < metrik.get("schwelle_vk", 0.38):
                    treffer.append(
                        Treffer(
                            "stimme",
                            metrik["id"],
                            f"Variationskoeffizient {vk:.2f}, Schnitt {mittel:.0f} Woerter",
                            1,
                            metrik["hinweis"],
                            metrik["ersatz"],
                        )
                    )

        elif typ == "perspektive":
            if not re.search(r"\b(ich|wir|uns|unser\w*|mein\w*)\b", klein):
                treffer.append(
                    Treffer(
                        "stimme",
                        metrik["id"],
                        "keine erste Person im Text",
                        1,
                        metrik["hinweis"],
                        metrik["ersatz"],
                    )
                )

    return treffer


# ---------------------------------------------------------------- Kern


def lade_textsorte(katalog: dict, name: str) -> dict:
    """Profil einer Textsorte holen. Unbekannter Name ist ein Fehler, keine
    stille Ruecknahme auf Standard — sonst prueft man monatelang das Falsche."""
    sorten = katalog.get("textsorten", {})
    if name == TEXTSORTE_DEFAULT and name not in sorten:
        return {}
    if name not in sorten:
        bekannt = ", ".join(sorten) or "keine im Katalog hinterlegt"
        raise KeyError(f"Unbekannte Textsorte '{name}'. Bekannt: {bekannt}")
    return sorten[name]


def pruefe(
    text: str,
    katalog: dict,
    belege_ok: bool = False,
    textsorte: str = TEXTSORTE_DEFAULT,
) -> list[Gruppenergebnis]:
    ergebnisse: list[Gruppenergebnis] = []
    profil = lade_textsorte(katalog, textsorte)
    min_woerter = int(profil.get("min_woerter_stimme", MIN_WOERTER_STIMME))
    abgeschaltet = set(profil.get("aus", []))
    wortzahl = len(woerter(text))

    for schluessel, gruppe in katalog["gruppen"].items():
        ergebnis = Gruppenergebnis(
            schluessel=schluessel,
            titel=gruppe["titel"],
            schwelle=int(gruppe.get("schwelle", 1)),
        )

        for regel in gruppe.get("regeln", []):
            if regel["id"] in abgeschaltet:
                continue
            flags = re.UNICODE if regel.get("case") else re.IGNORECASE | re.UNICODE
            muster = re.compile(regel["muster"], flags)
            gewicht = float(regel.get("gewicht", 1.0))
            for n, fund in enumerate(muster.finditer(text)):
                if n >= MAX_TREFFER_PRO_REGEL:
                    break
                roh = fund.group(0).strip()
                fundstelle = re.sub(r"\s+", " ", roh)
                if len(fundstelle) > 90:
                    fundstelle = fundstelle[:87] + "..."
                ergebnis.treffer.append(
                    Treffer(
                        schluessel,
                        regel["id"],
                        fundstelle,
                        zeile_von(text, fund.start()),
                        regel["hinweis"],
                        regel["ersatz"],
                        gewicht,
                    )
                )

        if gruppe.get("metriken"):
            aktiv = [m for m in gruppe["metriken"] if m["id"] not in abgeschaltet]
            stumm = [m["id"] for m in gruppe["metriken"] if m["id"] in abgeschaltet]
            vermerke: list[str] = []

            if wortzahl < min_woerter:
                vermerke.append(
                    f"Metriken nicht geprueft, {wortzahl} < {min_woerter} Woerter")
                # Eine Gruppe ohne Regeln haette hier gar nichts geprueft.
                # Die darf nicht als bestanden durchgehen.
                if not gruppe.get("regeln"):
                    ergebnis.uebersprungen = True
            else:
                ergebnis.treffer.extend(
                    pruefe_metriken(text, aktiv, schluessel, min_woerter))

            if stumm:
                vermerke.append(
                    f"abgeschaltet durch --textsorte {textsorte}: {', '.join(stumm)}")
            ergebnis.notiz = " · ".join(vermerke)

        if schluessel == "belege" and belege_ok:
            ergebnis.uebersprungen = True
            ergebnis.notiz = "--belege-ok gesetzt, Zahlen gelten als belegt"

        ergebnisse.append(ergebnis)

    return ergebnisse


def punktzahl(ergebnisse: list[Gruppenergebnis]) -> tuple[int, int]:
    return sum(1 for e in ergebnisse if e.bestanden), len(ergebnisse)


# ---------------------------------------------------------------- Ausgabe


def bericht(ergebnisse: list[Gruppenergebnis], farbig: bool, ausfuehrlich: bool) -> str:
    zeilen: list[str] = []
    erreicht, gesamt = punktzahl(ergebnisse)

    for ergebnis in ergebnisse:
        if ergebnis.uebersprungen:
            kopf = f"  [ uebersprungen ] {ergebnis.titel}"
            zeilen.append(faerbe(kopf, "grau", farbig))
        elif ergebnis.bestanden and not ergebnis.treffer:
            zeilen.append(faerbe(f"  [ ok ] {ergebnis.titel}", "gruen", farbig))
            if ergebnis.notiz:
                zeilen.append(faerbe(f"         {ergebnis.notiz}", "grau", farbig))
            continue
        elif ergebnis.bestanden:
            kopf = (f"  [ ok ] {ergebnis.titel} — {len(ergebnis.treffer)} Hinweis(e), "
                    f"Last {ergebnis.last:g} unter Schwelle {ergebnis.schwelle}")
            zeilen.append(faerbe(kopf, "gelb", farbig))
        else:
            kopf = (f"  [ -1 ] {ergebnis.titel} — {len(ergebnis.treffer)} Treffer, "
                    f"Last {ergebnis.last:g} (Schwelle {ergebnis.schwelle})")
            zeilen.append(faerbe(kopf, "rot", farbig))

        if ergebnis.notiz:
            zeilen.append(faerbe(f"         {ergebnis.notiz}", "grau", farbig))

        zeige = ergebnis.treffer if ausfuehrlich else ergebnis.treffer[:6]
        for treffer in zeige:
            zeilen.append(f"         Z{treffer.zeile}  „{treffer.fundstelle}“")
            zeilen.append(faerbe(f"              {treffer.hinweis}", "grau", farbig))
            zeilen.append(faerbe(f"              → {treffer.ersatz}", "grau", farbig))
        rest = len(ergebnis.treffer) - len(zeige)
        if rest > 0:
            zeilen.append(faerbe(f"         … {rest} weitere (--alles zeigt sie)", "grau", farbig))

    farbe = "gruen" if erreicht == gesamt else ("gelb" if erreicht >= gesamt - 1 else "rot")
    geschenkt = [e.schluessel for e in ergebnisse if e.uebersprungen]
    zusatz = f" · {len(geschenkt)} ungeprueft ({', '.join(geschenkt)})" if geschenkt else ""
    zeilen.append("")
    zeilen.append(faerbe(f"  Score {erreicht}/{gesamt}", farbe, farbig)
                  + faerbe(zusatz, "gelb", farbig))
    return "\n".join(zeilen)


def als_json(ergebnisse: list[Gruppenergebnis],
             textsorte: str = TEXTSORTE_DEFAULT) -> str:
    erreicht, gesamt = punktzahl(ergebnisse)
    return json.dumps(
        {
            "score": erreicht,
            "max": gesamt,
            "bestanden": erreicht == gesamt,
            "textsorte": textsorte,
            "ungeprueft": [e.schluessel for e in ergebnisse if e.uebersprungen],
            "gruppen": [
                {
                    "schluessel": e.schluessel,
                    "titel": e.titel,
                    "bestanden": e.bestanden,
                    "uebersprungen": e.uebersprungen,
                    "notiz": e.notiz,
                    "schwelle": e.schwelle,
                    "last": e.last,
                    "treffer": [
                        {
                            "regel": t.regel_id,
                            "zeile": t.zeile,
                            "fundstelle": t.fundstelle,
                            "hinweis": t.hinweis,
                            "ersatz": t.ersatz,
                            "gewicht": t.gewicht,
                        }
                        for t in e.treffer
                    ],
                }
                for e in ergebnisse
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------- CLI


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deslop_de",
        description="Linter fuer KI-typische Schreibmuster in deutschen Texten.",
    )
    parser.add_argument("datei", nargs="?", help="Datei (.md, .txt, .html) — oder --text nutzen")
    parser.add_argument("--text", help="Text direkt uebergeben")
    parser.add_argument("--katalog", default=KATALOG_DEFAULT, help="eigener Regelkatalog (JSON)")
    parser.add_argument("--belege-ok", action="store_true",
                        help="Zahlen sind belegbar: Gruppe blockiert nicht, Fundstellen erscheinen trotzdem")
    parser.add_argument("--textsorte", default=TEXTSORTE_DEFAULT,
                        help="Textsorte aus dem Katalog (Default: standard). --textsorten listet sie auf")
    parser.add_argument("--textsorten", action="store_true",
                        help="Verfuegbare Textsorten anzeigen und beenden")
    parser.add_argument("--min", type=int, default=None, help="Mindestpunktzahl fuer Exit 0 (Default: alle)")
    parser.add_argument("--json", action="store_true", help="Maschinenlesbare Ausgabe")
    parser.add_argument("--alles", action="store_true", help="Alle Treffer statt der ersten sechs")
    parser.add_argument("--keine-farben", action="store_true")
    args = parser.parse_args(argv)

    try:
        with open(args.katalog, "r", encoding="utf-8") as fh:
            katalog = json.load(fh)
    except (OSError, json.JSONDecodeError) as fehler:
        print(f"Katalog nicht lesbar ({args.katalog}): {fehler}", file=sys.stderr)
        return 2

    if args.textsorten:
        sorten = katalog.get("textsorten", {})
        if not sorten:
            print("Dieser Katalog kennt keine Textsorten.", file=sys.stderr)
            return 2
        print()
        for name, profil in sorten.items():
            marke = " (Default)" if name == TEXTSORTE_DEFAULT else ""
            print(f"  {name}{marke} — {profil.get('titel', '')}")
            print(f"      Stimme ab {profil.get('min_woerter_stimme', MIN_WOERTER_STIMME)} Woertern"
                  + (f", aus: {', '.join(profil['aus'])}" if profil.get("aus") else ""))
            if profil.get("notiz"):
                print(f"      {profil['notiz']}")
        print()
        return 0

    if args.text is not None:
        text = args.text
        quelle = "--text"
    elif args.datei:
        if not os.path.exists(args.datei):
            print(f"Datei nicht gefunden: {args.datei}", file=sys.stderr)
            return 2
        text = lade_text(args.datei)
        quelle = args.datei
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
        quelle = "stdin"
    else:
        parser.print_help()
        return 2

    if not text.strip():
        print("Leerer Text.", file=sys.stderr)
        return 2

    try:
        ergebnisse = pruefe(text, katalog, belege_ok=args.belege_ok,
                            textsorte=args.textsorte)
    except KeyError as fehler:
        print(str(fehler).strip('"'), file=sys.stderr)
        return 2

    erreicht, gesamt = punktzahl(ergebnisse)
    schwelle = args.min if args.min is not None else gesamt

    if args.json:
        print(als_json(ergebnisse, args.textsorte))
    else:
        farbig = sys.stdout.isatty() and not args.keine_farben
        print()
        print(faerbe(
            f"  slopwaechter · {quelle} · {len(woerter(text))} Woerter"
            f" · Textsorte {args.textsorte}", "fett", farbig))
        print()
        print(bericht(ergebnisse, farbig, args.alles))
        print()

    return 0 if erreicht >= schwelle else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # nachgeschaltetes head/less hat dichtgemacht - kein Fehler
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        raise SystemExit(0)
