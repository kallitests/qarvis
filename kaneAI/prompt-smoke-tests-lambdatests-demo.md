bjectif: exécuter un smoke test unique sur https://www.lambdatest.com/

Identifie le chemin critique principal accessible depuis cette URL (ex: recherche produit, inscription ou connexion) et exécute-le en un seul scénario, sans suite complète.

Contraintes:
- Sélecteurs résilients (rôle/texte visible), pas d'attente fixe (sleep/wait codé en dur)
- Un seul parcours, pas de variantes
- Si un appel API est visible dans les requêtes réseau du parcours, vérifie son status code

Une fois exécuté, exporte:
1. Les steps en Gherkin (BDD)
2. Le test en Cypress
3. Si un appel API a été détecté: le test API correspondant