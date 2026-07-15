# agents/

Agents LangGraph :
- **triage** : classe chaque échec de run (régression / flaky / UI attendue / env) -> résumé priorisé.
- **self-healing** : détecte les sélecteurs cassés, propose un correctif.

Principe non négociable : MCP au *build* des tests (génération de sélecteurs/Page Objects), jamais en dépendance de *run* en CI.
Entrées attendues : artefacts JUnit/JSON des runs Playwright (`../tests-node/test-results/`).
