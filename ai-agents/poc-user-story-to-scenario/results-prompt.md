Bonne décision — c'est l'ordre qui évite de brûler trois semaines sur de la plomberie pour un résultat médiocre. Je te construis le script.

Un choix d'ingénierie que je fais et que je t'explique : pas de MCP à cette étape. Le MCP existe pour qu'un agent pilote un navigateur en boucle ; ici tu as besoin d'une chose déterministe et scriptable. J'utilise donc directement l'ariaSnapshotde Playwright — c'est exactement ce que le MCP utilise sous le capot, sans la boucle d'agent. Plus simple, moins cher, reproductible.Syntaxe validée, YAML valide, et aria_snapshot bien présent dans Playwright 1.56. Maintenant la pièce la plus importante — la grille de relecture, puisque l'objectif est de juger la qualité, pas de générer.Voilà le POC. Trois commandes et tu as tes 10 cas générés.

pip install -r requirements.txt && python -m playwright install chromium
cp .env.example .env   # ta clé API
python generate_gherkin.py --cases cases.example.yaml
Le mécanisme qui fait tout le travail. Le script ne demande jamais au LLM d'inventer des étapes depuis la story. Il capture d'abord l'arbre d'accessibilité de la page réelle (aria_snapshot), le pose comme source de vérité, et impose au modèle : chaque étape doit correspondre à un élément réellement présent ; tout ce qui n'est pas vérifiable part en # TODO(à vérifier) au lieu d'être deviné. C'est ça que tu dois évaluer — pas la beauté du Gherkin, mais sa capacité à dire « je ne sais pas ».

Les 3 cas d'exemple sont piégés exprès. Un cas normal, une story volontairement vague, et — le plus important — story_hors_perimetre : une story qui parle de reset password par e-mail, fonctionnalité absente de SauceDemo. S'il t'invente un formulaire de réinitialisation qui n'existe pas, le concept ne tient pas et il faut retravailler le prompt avant toute plomberie. S'il te répond honnêtement « je ne vois pas ça sur la page », tu tiens quelque chose. C'est ton test décisif.

La grille de relecture est dans le README, avec 7 critères — dont le seul qui compte vraiment en n°7 : « corriger cette sortie va-t-il plus vite que l'écrire moi-même ? ». Et surtout un critère de décision à fixer avant de regarder les résultats (≥7/10 utilisables → on continue ; ≤3 → on ne construit pas le plugin). Fixe-le maintenant, pas après : sinon tu trouveras toujours une raison de te dire que c'est « prometteur ».

Deux points d'honnêteté :

Je n'ai pas pu l'exécuter de bout en bout. J'ai vérifié la syntaxe Python, la validité du YAML et l'existence de l'API aria_snapshot dans Playwright 1.56 — mais mon sandbox n'a ni clé API ni accès au CDN de téléchargement des navigateurs. Le premier vrai run, c'est toi qui le fais. Attends-toi éventuellement à un ajustement mineur.

Vérifie le nom du modèle (MODEL = "claude-sonnet-5") sur docs.claude.com — c'est surchargeable par QARVIS_MODELsans toucher au code.

Une limite assumée que le README détaille : une seule page par capture. Les parcours multi-écrans (checkout en 3 étapes) seront TODO-isés. C'est volontaire — le crawl multi-pages est un chantier d'étape 2, et l'ajouter maintenant t'empêcherait de répondre à la seule question qui compte aujourd'hui : est-ce que la génération vaut quelque chose ?

Lance-le, note tes 10 cas, et reviens avec le verdict — on saura alors s'il faut itérer sur le prompt ou passer au webhook Jira.