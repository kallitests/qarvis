# QARVIS — Étape 1 : validation de la qualité du Gherkin généré

> **Ce que ce POC prouve (ou réfute) :** est-ce qu'une user story + une URL suffisent à
> produire des scénarios Gherkin de smoke test *réellement utilisables* ?
> Tant que la réponse n'est pas « oui » sur ~10 cas réels, **ne construis pas le plugin Jira.**
> Le bouton est l'emballage ; ceci est le produit.

## Pourquoi pas de MCP ici ?

Le Playwright MCP sert à ce qu'un **agent** pilote un navigateur en boucle. Ici on veut
quelque chose de **déterministe et scriptable**. On utilise donc directement
`locator.aria_snapshot()` — c'est exactement l'arbre d'accessibilité que le MCP exploite
sous le capot, sans la boucle d'agent. Plus simple, moins cher, reproductible.
Le MCP reprendra sa place plus tard, au *build* des tests.

## Installation

```bash
pip install -r requirements.txt
python -m playwright install chromium

cp .env.example .env      # puis renseigne ANTHROPIC_API_KEY
```

## Usage

```bash
# 1 cas
python generate_gherkin.py \
  --url https://www.saucedemo.com \
  --story "En tant que client je veux me connecter pour accéder au catalogue"

# Lot (recommandé : c'est ainsi qu'on juge la qualité)
python generate_gherkin.py --cases cases.example.yaml

# Page derrière un login : enregistre la session une fois, réutilise-la ensuite
python -m playwright codegen --save-storage=auth.json https://mon-app.com
python generate_gherkin.py --url https://mon-app.com/dashboard \
  --story "..." --storage-state auth.json
```

Les `.feature` atterrissent dans `features/`.

## Comment le script combat l'hallucination

C'est le cœur du POC. On ne demande **jamais** au modèle d'inventer des étapes depuis la
seule story. Le pipeline est :

1. **Capture** — Playwright ouvre l'URL et extrait l'arbre d'accessibilité (rôles + noms
   accessibles). C'est la *source de vérité*.
2. **Contrainte** — le prompt système impose : chaque étape doit correspondre à un élément
   présent dans le snapshot ; tout ce qui n'est pas vérifiable part en `# TODO(à vérifier)`
   au lieu d'être inventé.
3. **Langage métier** — sélecteurs CSS/XPath/`data-testid` interdits dans les étapes.

C'est précisément ce mécanisme que tu dois évaluer ci-dessous.

---

## 🎯 Grille de relecture (le vrai livrable)

Génère les 3 cas d'exemple, puis note **chaque fichier** sur ces 7 critères.
Note simple : ✅ conforme / ⚠️ limite / ❌ raté.

| # | Critère | Question à te poser |
|---|---------|---------------------|
| 1 | **Ancrage** | Chaque étape correspond-elle à un élément qui existe *vraiment* sur la page ? |
| 2 | **Zéro invention** | Le modèle a-t-il inventé un écran, un champ, un message inexistant ? |
| 3 | **Honnêteté** | Ce qu'il ne pouvait pas vérifier est-il bien en `# TODO`, plutôt que deviné ? |
| 4 | **Langage métier** | Un PM comprendrait-il ces scénarios ? Aucun sélecteur technique n'a fuité ? |
| 5 | **Smoke, vraiment** | 1-3 scénarios sur le chemin critique — ou une liste exhaustive inutile ? |
| 6 | **Implémentabilité** | Peux-tu écrire les step definitions Playwright sans deviner ? |
| 7 | **Gain de temps réel** | Corriger cette sortie va-t-il plus vite que l'écrire toi-même ? |

### Les 3 cas d'exemple sont un test piégé — c'est voulu

| Cas | Ce qu'il teste | Verdict attendu si le POC est bon |
|-----|----------------|-----------------------------------|
| `login_saucedemo` | story correcte + page riche | Gherkin propre et implémentable |
| `story_vague` | « je veux me connecter », sans plus | Doit rester **sobre** et s'appuyer sur la page, pas broder |
| `story_hors_perimetre` | parle de reset password par e-mail — **absent de la page** | Doit produire des **TODO**, surtout pas inventer un formulaire |

> **Le cas décisif est `story_hors_perimetre`.** S'il invente un écran de réinitialisation
> qui n'existe pas, le concept ne tient pas et il faut retravailler le prompt avant tout
> le reste. S'il dit honnêtement « je ne vois pas ça sur la page », tu tiens quelque chose.

### Critère de décision (à fixer AVANT de regarder les résultats)

- **≥ 7 cas sur 10 utilisables après retouche mineure** → le concept tient. On passe à
  l'étape 2 (webhook Jira Automation), puis au plugin Forge.
- **Entre 4 et 6** → le concept tient mais le prompt/l'ancrage doit être retravaillé.
  Itère sur `SYSTEM_PROMPT`, pas sur la plomberie.
- **≤ 3** → ne construis pas le plugin. Le problème est en amont (qualité des stories,
  ou besoin d'un vrai crawl multi-pages plutôt qu'un snapshot d'une seule page).

## Limites connues (assumées à ce stade)

- **Une seule page.** Le snapshot ne couvre pas les parcours multi-écrans (checkout en
  3 étapes...). Attendu : le modèle TODO-ise la suite. Un crawl multi-pages est un
  chantier d'étape 2, pas d'étape 1.
- **Pages authentifiées** → nécessitent `--storage-state`. C'est le mur identifié : en
  production, il faudra des credentials de test par client.
- **Snapshot tronqué** sur les pages très lourdes (`QARVIS_MAX_SNAPSHOT_CHARS`).
  Le script te prévient quand ça arrive.
- **Sortie = brouillon.** Un humain relit et garantit. C'est le principe QARVIS :
  *l'IA propose, l'humain garantit.*

## Et ensuite ?

1. ✅ **Ici** — la qualité est-elle au rendez-vous ? (ce POC)
2. Webhook : règle *Automation for Jira* → `Send web request` vers ce script hébergé.
   Déclencheur depuis Jira **sans écrire un plugin**.
3. Forge app + Atlassian Marketplace — seulement une fois 1 et 2 validés.
