KaneAI fonctionne différemment d'un LLM classique auquel on donne un system prompt : c'est un agent qui pilote lui-même un navigateur réel (il "voit" le DOM en direct), tu lui donnes des instructions en langage naturel dans son Test Planner, il exécute, puis tu exportes le code (Cypress, Playwright, Selenium...). Deux conséquences pour l'adaptation : plus besoin de la consigne "inspecte le DOM avant de générer un sélecteur" (il le fait nativement), mais il faut restructurer le prompt en instructions d'exécution plutôt qu'en demande de génération de code brute.

Autre point : LambdaTest s'est rebrandé en **TestMu AI** début 2026 — KaneAI reste le nom de l'agent mais l'interface a pu bouger un peu depuis, à vérifier sur ta version.

Voici le prompt adapté, à coller dans le Test Planner de KaneAI (champ prompt du nouveau test) :

```
Objectif: exécuter un smoke test unique sur https://www.lambdatest.com/

Identifie le chemin critique principal accessible depuis cette URL (ex: recherche produit, inscription ou connexion) et exécute-le en un seul scénario, sans suite complète.

Contraintes:
- Sélecteurs résilients (rôle/texte visible), pas d'attente fixe (sleep/wait codé en dur)
- Un seul parcours, pas de variantes
- Si un appel API est visible dans les requêtes réseau du parcours, vérifie son status code

Une fois exécuté, exporte:
1. Les steps en Gherkin (BDD)
2. Le test en Cypress
3. Si un appel API a été détecté: le test API correspondant
```

Concrètement dans l'UI : Create Test → colle ce texte dans le prompt du planner avec l'URL de départ renseignée → Run → une fois le run vert, utilise le bouton d'export et choisis Cypress (+ Gherkin si proposé séparément). Si KaneAI ne propose pas d'export API natif dans ta version, le point 3 restera à faire manuellement à partir des requêtes réseau capturées pendant le run.

Sources :
- [KaneAI: Autonomous AI Test Automation Agent](https://www.testmuai.com/kane-ai/)
- [How to Use Cypress AI: Complete 2026 Guide](https://www.testmuai.com/blog/cypress-ai/)
- [LambdaTest Rolls Out Major Updates to KaneAI](https://www.globenewswire.com/news-release/2025/01/24/3014994/0/en/lambdatest-rolls-out-major-updates-to-kaneai-transforming-the-end-to-end-software-testing-experience.html)