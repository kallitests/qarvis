#!/usr/bin/env python3
"""
QARVIS — Étape 1 : générateur de scénarios Gherkin (user story + URL -> .feature)

But : valider la QUALITÉ du Gherkin généré avant d'investir dans un plugin Jira.
Aucune plomberie : un script, une commande, un fichier .feature à relire.

Principe clé (anti-hallucination) :
  On ne demande PAS au LLM d'inventer des étapes à partir de la seule user story.
  On capture d'abord un snapshot d'accessibilité de la page réelle (ariaSnapshot),
  et on force le modèle à n'écrire que des étapes ancrées dans ce qu'il voit.
  Tout ce qui n'est pas vérifiable part en TODO explicite, pas en invention.

Usage :
    # cas unique
    python generate_gherkin.py --url https://www.saucedemo.com \
        --story "En tant que client je veux me connecter pour accéder au catalogue"

    # cas unique, story dans un fichier
    python generate_gherkin.py --url https://... --story-file ma_story.txt

    # lot de cas (recommandé pour juger la qualité sur ~10 cas)
    python generate_gherkin.py --cases cases.yaml

    # page derrière un login : enregistrer une session une fois, puis la réutiliser
    #   playwright codegen --save-storage=auth.json https://mon-app.com
    python generate_gherkin.py --url https://... --story "..." --storage-state auth.json
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from anthropic import Anthropic
from playwright.sync_api import sync_playwright

# --- Réglages -----------------------------------------------------------------

# Vérifie le nom de modèle courant sur https://docs.claude.com avant usage sérieux.
MODEL = os.getenv("QARVIS_MODEL", "claude-sonnet-5")
MAX_TOKENS = 4000
# Un snapshot d'accessibilité peut être énorme : on borne pour maîtriser le coût.
MAX_SNAPSHOT_CHARS = int(os.getenv("QARVIS_MAX_SNAPSHOT_CHARS", "40000"))
PAGE_TIMEOUT_MS = 30_000

SYSTEM_PROMPT = """Tu es un SDET senior, expert en Playwright et en BDD/Gherkin.

Tu reçois (1) une user story et (2) un snapshot d'accessibilité d'une page web réelle.
Tu produis des scénarios Gherkin de SMOKE TEST : le chemin critique, rien de plus.

RÈGLES ABSOLUES
1. ANCRAGE. Chaque étape doit correspondre à un élément réellement présent dans le
   snapshot (rôle + nom accessible). N'invente JAMAIS un champ, un bouton ou un écran.
2. NON-VÉRIFIABLE = TODO. Si la user story implique quelque chose que le snapshot ne
   permet pas de confirmer (écran suivant, e-mail envoyé, calcul...), ne l'invente pas :
   ajoute une ligne de commentaire `# TODO(à vérifier) : ...` en fin de fichier.
3. LANGAGE MÉTIER. Les étapes décrivent une intention utilisateur, pas une technique.
   Interdit dans les étapes : sélecteurs CSS/XPath, `#id`, `data-testid`, `click()`.
   Bon    : `Quand je me connecte avec un compte valide`
   Mauvais: `Quand je clique sur #login-button`
4. SMOKE = MINIMAL. 1 à 3 scénarios maximum. Le parcours qui rapporte de l'argent.
   Pas de cas exotiques, pas de exhaustivité.
5. STRUCTURE. Utilise `Feature:`, un `Background:` si un préalable est partagé, des
   tags (`@smoke` obligatoire, plus un tag de domaine : `@auth`, `@cart`, `@checkout`...).
   Utilise `Scenario Outline` + `Examples` UNIQUEMENT si la story est explicitement
   data-driven. Sinon, des `Scenario:` simples.
6. NÉGATIF. Ajoute au plus UN scénario négatif, et seulement si le snapshot montre
   de quoi le tester (ex. un formulaire de connexion).

FORMAT DE SORTIE
Uniquement le contenu du fichier .feature. Pas de ``` , pas de préambule, pas
d'explication. Le français pour les étapes, sauf si la story est en anglais.
"""

USER_PROMPT = """## User story

{story}

## Page analysée

URL   : {url}
Titre : {title}

## Snapshot d'accessibilité (source de vérité){truncated_note}

```yaml
{snapshot}
```

Génère maintenant le fichier .feature de smoke test."""


# --- Capture -------------------------------------------------------------------


@dataclass
class PageCapture:
    url: str
    title: str
    snapshot: str
    truncated: bool


def capture_page(
    url: str, storage_state: str | None = None, headless: bool = True
) -> PageCapture:
    """Ouvre l'URL et renvoie son arbre d'accessibilité (le même que celui du MCP)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=storage_state if storage_state else None
        )
        page = context.new_page()
        page.set_default_timeout(PAGE_TIMEOUT_MS)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=PAGE_TIMEOUT_MS)

        title = page.title()
        snapshot = page.locator("body").aria_snapshot()

        browser.close()

    truncated = len(snapshot) > MAX_SNAPSHOT_CHARS
    if truncated:
        snapshot = snapshot[:MAX_SNAPSHOT_CHARS]

    return PageCapture(url=url, title=title, snapshot=snapshot, truncated=truncated)


# --- Génération ----------------------------------------------------------------


def generate_gherkin(client: Anthropic, story: str, capture: PageCapture) -> str:
    note = (
        "\n(snapshot tronqué : la page est plus longue que la limite configurée)"
        if capture.truncated
        else ""
    )
    prompt = USER_PROMPT.format(
        story=story.strip(),
        url=capture.url,
        title=capture.title,
        snapshot=capture.snapshot,
        truncated_note=note,
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(block.text for block in response.content if block.type == "text")
    return strip_fences(text).strip() + "\n"


def strip_fences(text: str) -> str:
    """Filet de sécurité si le modèle ajoute des ``` malgré la consigne."""
    text = re.sub(r"^\s*```(?:gherkin|cucumber)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    return text


# --- Utilitaires ---------------------------------------------------------------


def slugify(value: str, fallback: str = "scenario") -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return (slug or fallback)[:50]


def run_case(client: Anthropic, case_id: str, url: str, story: str,
             storage_state: str | None, out_dir: Path, headless: bool) -> Path:
    print(f"  [1/2] capture  {url}", file=sys.stderr)
    capture = capture_page(url, storage_state=storage_state, headless=headless)
    if capture.truncated:
        print("        ⚠️  snapshot tronqué (page volumineuse)", file=sys.stderr)

    print(f"  [2/2] génération ({MODEL})", file=sys.stderr)
    gherkin = generate_gherkin(client, story, capture)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slugify(case_id)}.feature"
    header = (
        f"# Généré par QARVIS (POC) — À RELIRE, ce n'est pas un artefact final.\n"
        f"# Source  : {url}\n"
        f"# Story   : {' '.join(story.split())[:120]}\n\n"
    )
    out_path.write_text(header + gherkin, encoding="utf-8")
    print(f"  ✅ {out_path}", file=sys.stderr)
    return out_path


# --- CLI -----------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Génère des scénarios Gherkin de smoke test à partir d'une user story et d'une URL."
    )
    parser.add_argument("--url", help="URL de la page à analyser")
    parser.add_argument("--story", help="User story (texte)")
    parser.add_argument("--story-file", help="Fichier contenant la user story")
    parser.add_argument("--cases", help="Fichier YAML de cas (mode lot)")
    parser.add_argument("--storage-state", help="Fichier de session Playwright (pages authentifiées)")
    parser.add_argument("--out", default="features", help="Dossier de sortie (défaut: features)")
    parser.add_argument("--headed", action="store_true", help="Afficher le navigateur")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY manquante (voir .env.example).", file=sys.stderr)
        return 1

    client = Anthropic()
    out_dir = Path(args.out)
    headless = not args.headed

    # --- Mode lot
    if args.cases:
        cases = yaml.safe_load(Path(args.cases).read_text(encoding="utf-8")) or []
        if not isinstance(cases, list) or not cases:
            print("❌ Le fichier de cas doit contenir une liste non vide.", file=sys.stderr)
            return 1

        failures = 0
        for i, case in enumerate(cases, 1):
            case_id = str(case.get("id") or f"case_{i}")
            print(f"\n▶ [{i}/{len(cases)}] {case_id}", file=sys.stderr)
            try:
                run_case(
                    client,
                    case_id=case_id,
                    url=case["url"],
                    story=case["story"],
                    storage_state=case.get("storage_state") or args.storage_state,
                    out_dir=out_dir,
                    headless=headless,
                )
            except Exception as exc:  # on continue le lot même si un cas casse
                failures += 1
                print(f"  ❌ échec : {exc}", file=sys.stderr)

        print(f"\n{len(cases) - failures}/{len(cases)} cas générés -> {out_dir}/", file=sys.stderr)
        print("👉 Relis chaque .feature avec la grille du README avant d'aller plus loin.", file=sys.stderr)
        return 1 if failures else 0

    # --- Mode cas unique
    if not args.url:
        parser.error("--url est requis (ou utilise --cases)")
    story = args.story
    if args.story_file:
        story = Path(args.story_file).read_text(encoding="utf-8")
    if not story:
        parser.error("--story ou --story-file est requis")

    run_case(
        client,
        case_id=slugify(story.split("\n")[0], "feature"),
        url=args.url,
        story=story,
        storage_state=args.storage_state,
        out_dir=out_dir,
        headless=headless,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
