# QARVIS — Spécification du POC

**QARVIS** = *QA + JARVIS* : le copilote IA qui maintient la suite de tests d'un produit **verte en continu**, sans que le client recrute un SDET.

> **Nature du document :** spécification fonctionnelle et technique du POC (aucun code à ce stade).
> **Finalité :** servir de base d'exemples pour une **démo Loom** commerciale, et de vitrine des 3 offres d'abonnement.
> **Modèle économique :** je vends un **résultat récurrent** (abonnement / MRR), pas des heures.

---

## 1. Vision en une phrase

> *« Votre suite de tests E2E + API reste verte à chaque déploiement — générée, maintenue et triée par l'IA — pour un abonnement mensuel, sans embaucher. »*

QARVIS n'est pas « un framework de test ». C'est un **service productisé** dont le POC démontre la mécanique de bout en bout : des tests Playwright (UI + API) pilotés en CLI, un cerveau IA (MCP + agents) qui les génère/maintient/triage, une exécution conteneurisée et multi-CI, des alertes multi-canal et un reporting lisible du dev jusqu'au décideur.

---

## 2. Application cible de la démo : Cypress Real World App (RWA)

Le POC s'exécute contre la **Cypress Real World App**, application de paiement open-source (type Venmo/PayPal) publiée par Cypress.

- **Stack de l'app :** full-stack Express/React, TypeScript, XState, Material-UI, base JSON locale (lowdb, ré-seedée entre les tests). Front sur `:3000`, **API backend sur `:3001`**. Licence MIT.
- **Pourquoi c'est la cible idéale :**
  1. Elle a un **vrai front ET une vraie API** → on démontre les deux couches (contrairement à une app front-only comme SauceDemo).
  2. Fonctionnalités riches et réalistes : auth locale, onboarding, **envoi/demande d'argent, feed de transactions, likes/commentaires, notifications, comptes bancaires, recherche** → matière abondante pour une pyramide complète.
  3. **Le hook de démo :** faire tourner un pipeline **Playwright** sur l'application vitrine de **Cypress** — message marketing implicite fort et mémorable.
- **Contrainte assumée :** c'est une app de démo (pas de prod). On teste donc des parcours, pas de la charge réelle ; le POC vise la **démonstration de méthode**, transposable ensuite à n'importe quel client.

---

## 3. Architecture fonctionnelle du pipeline (vue d'ensemble)

Six couches, du test brut jusqu'au décideur :

1. **Couche Test — Playwright CLI (UI + API).** Toute la pyramide, exécutée via la CLI Playwright (pas d'IDE requis), en TypeScript. Tests UI (parcours navigateur) + tests API (appels directs au backend `:3001`), + smoke, + BDD/Gherkin lisible métier, + non-fonctionnel (a11y, visual, perf légère).
2. **Couche IA — MCP + agents (Python : LangChain / LangGraph / LangSmith).** Le « cerveau » QARVIS : génération de tests via **Playwright MCP**, triage des échecs, détection de flaky, suggestion de self-healing de sélecteurs, évals. LangSmith fournit l'observabilité/traçage des agents.
3. **Couche Orchestration — Docker / docker-compose (→ Kubernetes plus tard).** L'app cible, les runners de test et les services annexes tournent en conteneurs reproductibles. `docker-compose` pour le POC ; migration **k8s** prévue en phase ultérieure (scalabilité multi-clients).
4. **Couche CI/CD — GitHub Actions ET GitLab CI.** Le même pipeline décliné sur les deux plateformes (le client arrive avec l'une ou l'autre — on couvre les deux). Build → smoke (gate) → suite complète shardée → publication des rapports.
5. **Couche Alerting — Gmail, Discord, Slack, Teams.** Notification en temps quasi réel selon le canal du client : échec de smoke, régression détectée, rapport de run. Sévérité modulable par canal.
6. **Couche Reporting — Mochawesome + Power BI.** Mochawesome pour le rapport technique par run (lisible par les devs) ; **Power BI** pour le dashboard de tendance (santé de la suite, flakiness, couverture dans le temps) destiné aux leads et décideurs.

---

## 4. Le cerveau QARVIS (couche IA détaillée)

C'est le différenciateur — ce qui rend le multi-clients possible en peu d'heures, donc ce qui rend l'abonnement rentable. Quatre agents/capacités :

- **Générateur (MCP).** À partir d'un snapshot d'accessibilité de la RWA via Playwright MCP, scaffolde des Page Objects et des scénarios candidats (sélecteurs robustes par rôle/label/`data-test`). L'humain valide et fige en code versionné.
- **Triage d'échecs.** Sur un run rouge, un agent LangGraph classe chaque échec : *vraie régression* vs *flaky* vs *changement d'UI attendu* vs *problème d'environnement*. Sortie : un résumé priorisé, pas 40 stacktraces brutes.
- **Détecteur de flaky & self-healing.** Repère les tests instables (historique de runs), propose une correction de sélecteur quand l'UI a bougé, signale ce qui doit être re-stabilisé.
- **Évaluateur (evals).** Jeu d'évaluation pour mesurer la fiabilité des suggestions de l'IA elle-même (précision du triage, pertinence des sélecteurs générés), tracé dans **LangSmith**. C'est ce qui rend le système *sérieux* et non un gadget.

> Principe directeur : **l'IA génère et propose, l'humain (toi) valide et garantit.** En CI, aucun test ne dépend du MCP à l'exécution — le MCP sert au *build* des tests, pas à leur *run*.

### 4.5 Module Chatbot RAG — « Ask QARVIS »

Le module qui transforme QARVIS d'un *pipeline* en un *produit interactif*. Une interface conversationnelle (widget web + éventuellement bot Slack/Discord) qui répond en langage naturel aux questions du client sur **l'état de qualité de son produit**, en s'appuyant sur un **RAG** construit sur *ses* données de test.

**Ce que le chatbot ingère (base de connaissance RAG) :**
- l'historique des runs (résultats, durées, taux de flakiness dans le temps) ;
- les rapports Mochawesome / JUnit et les logs d'échec ;
- le code des tests lui-même (quels scénarios existent, quelle couverture) ;
- les traces de triage LangSmith ;
- en option : les specs/tickets du client (Jira, Linear, Notion) pour croiser **exigences ↔ tests**.

**Ce que le client peut demander :**
- *« Pourquoi le run de cette nuit est rouge ? »* → résumé du triage, en clair.
- *« Qu'est-ce qui est couvert sur le parcours paiement ? »* → inventaire de couverture.
- *« Quelles zones n'ont aucun test ? »* → détection des trous de couverture.
- *« Notre feature X est-elle testée ? »* → traçabilité exigence → test.
- *« Montre-moi la tendance de flakiness ce mois-ci. »* → synthèse chiffrée.

**Pourquoi c'est stratégique :** c'est un point de contact quotidien qui **ancre la valeur** (le client *voit* QARVIS travailler entre deux déploiements), réduit tes sollicitations directes (il interroge le bot au lieu de te pinger — protège tes 4h/jour), et constitue un **argument de vente différenciant** que quasi aucun prestataire QA n'offre. Techniquement, c'est le même socle Python/LangChain/LangGraph que le reste — tu réutilises ta stack.

**Positionnement dans les offres :** version *lecture seule basique* (statut du dernier run) dès **Regression** ; version *complète avec traçabilité exigences et trous de couverture* réservée à **Quality Partner**.

---

## 5. Scénarios de démonstration sur la RWA (par couche de pyramide)

Décrits ici au niveau **spécification** (comportement attendu), prêts à être formalisés en Gherkin puis implémentés.

### 5.1 Smoke (chemin critique — gate du pipeline, cible < 90 s)
- Login d'un utilisateur exemple → feed affiché.
- Envoi d'un paiement à un contact → transaction visible dans le feed.
- Réception d'une notification correspondante.
- Logout.

### 5.2 UI — fonctionnel / régression (un comportement isolé par test)
- **Auth & onboarding :** signup, création de compte bancaire à l'onboarding, login/logout, erreurs de validation.
- **Transactions :** envoyer de l'argent, demander de l'argent, accepter/refuser une demande, solde mis à jour.
- **Feed social :** onglets (public / contacts / perso), like et commentaire d'une transaction, pagination / infinite scroll.
- **Notifications :** génération à la réception d'un paiement, d'une demande, d'un like, d'un commentaire ; marquage lu.
- **Recherche & profil :** recherche d'utilisateur, mise à jour des paramètres du profil.

### 5.3 API — tests au niveau backend (`:3001`)
- Authentification et obtention de session/token.
- Création d'une transaction via l'API + assertions sur la réponse et l'état persistant.
- Validation : champs manquants, montants invalides → codes d'erreur attendus.
- Création/suppression de compte bancaire.
- Récupération et pagination des transactions et notifications.
- **Contrôle croisé UI↔API :** une action UI produit bien l'effet attendu côté API (cohérence de bout en bout).

### 5.4 Négatifs (prouver que la suite *détecte* vraiment)
- Login invalide, montants négatifs/nuls, accès non authentifié, requête malformée.

### 5.5 Non-fonctionnel (transverse)
- **Accessibilité** (axe) sur les pages clés (login, feed, transaction).
- **Visual regression** sur le feed et la page transaction.
- **Perf légère** : budget de temps sur le chargement du feed.

---

## 6. Les 3 abonnements (déclinaison du POC en offres)

Chaque tier = un **périmètre borné**, un **prix fixe**, un **résultat**. Le POC démontre visuellement ce que chaque niveau débloque.

| | **① SMOKE** | **② REGRESSION** *(offre phare)* | **③ QUALITY PARTNER** |
|---|---|---|---|
| **Promesse** | « Vous ne shippez plus un chemin critique cassé » | « Votre app ne régresse jamais deux fois sur le même bug » | « Un lead QA fractionné, sans le salaire » |
| **Prix indicatif /mois** | 600–900 € | 1 500–2 200 € | 3 500–4 500 € |
| **Couverture test** | Smoke UI du chemin critique | Smoke + régression UI **et API** qui grandit | Pyramide complète (UI, API, a11y, visual, perf) |
| **Volume** | Chemin critique figé | Jusqu'à ~15 nouveaux tests/mois + maintenance | Périmètre étendu + roadmap qualité |
| **IA / QARVIS** | Exécution automatisée | Triage d'échecs + détection flaky | Génération MCP + self-healing + **evals des features IA du client** |
| **CI/CD** | 1 plateforme (GH **ou** GitLab) | 1 plateforme, pipeline shardé complet | Multi-CI + gating de release |
| **Conteneurisation** | Docker | docker-compose | docker-compose → **k8s** |
| **Alerting** | 1 canal | 2 canaux + sévérités | Tous canaux + routage par sévérité |
| **Reporting** | Mochawesome | Mochawesome + tendance | Mochawesome + **dashboard Power BI** + gating |
| **Engagement humain** | Setup + run | Réponse prioritaire aux casses | Embarqué dans les sprints, accès Slack, stratégie |
| **Rôle dans le POC** | Produit d'appel (marge max) | **Ancre** — la démo tourne autour | Vitrine haut de gamme / upsell |

**Garde-fou anti scope-creep (à afficher dans chaque offre) :** plafond explicite de tests/mois, support en heures ouvrées, tout dépassement = avenant. On vend un résultat *cadré*, jamais une disponibilité illimitée — c'est ce qui protège le modèle « pas d'heures ».

**Rappel du calcul cible :** 3× Regression ≈ 5 400 €/mois (≈ 4 000 € net en micro) ; 2× Regression + 1× Quality Partner ≈ 7 500 €/mois (signal « penser SASU »). Les Smoke remplissent le pipeline et convertissent vers le haut.

---

## 7. Roadmap & livrables

Cinq phases. Chaque phase produit un **livrable démontrable** ; l'objectif intermédiaire est une **démo Loom** commercialisable dès la fin de la Phase 3.

### Phase 0 — Cadrage & socle *(fondations)*
**Livrables :**
- Ce document de spec validé + charte de nommage/branding QARVIS.
- Repo structuré (arborescence tests UI/API/smoke/BDD, dossiers IA, infra).
- RWA lancée en local via **Docker** ; utilisateurs et données de seed identifiés.
- Décision des baselines (navigateurs, ports, jeux d'utilisateurs de démo).

### Phase 1 — Cœur de test Playwright CLI (UI + API) *(la substance)*
**Livrables :**
- Suite **smoke** (chemin critique RWA) exécutable en CLI, < 90 s.
- Suite **UI de régression** (transactions, feed, notifications, auth) via Page Objects.
- Suite **API** (`:3001`) + un contrôle croisé UI↔API.
- Couche **BDD/Gherkin** lisible métier sur 3-4 parcours phares.
- **Rapport Mochawesome** généré à chaque run.
- ✅ *Démo-able :* « voici la suite qui tourne et le rapport ».

### Phase 2 — Conteneurisation & multi-CI *(l'industrialisation)*
**Livrables :**
- **docker-compose** orchestrant RWA + runner de tests, reproductible.
- Pipeline **GitHub Actions** : build → smoke (gate) → suite shardée → publication rapport.
- Pipeline **GitLab CI** équivalent (parité fonctionnelle).
- **Alerting** branché : échec smoke → Slack/Discord ; rapport de run → Gmail/Teams.
- ✅ *Démo-able :* « je pousse un commit, ça tourne tout seul, l'équipe est alertée ».

### Phase 3 — Cerveau IA QARVIS *(le différenciateur → cible démo Loom)*
**Livrables :**
- **Génération assistée par Playwright MCP** : scaffolding d'un nouveau scénario RWA à partir d'un snapshot, en direct.
- Agent de **triage d'échecs** (LangGraph) : d'un run rouge → résumé priorisé régression/flaky/env.
- **Détection de flaky** + suggestion de self-healing de sélecteur.
- **Observabilité LangSmith** sur les agents + premier jeu d'**evals**.
- ✅ *Démo-able :* **la démo Loom complète** — « je casse l'UI de la RWA, QARVIS détecte, trie, et propose le correctif ».

### Phase 4 — Reporting décideur & packaging commercial *(la vente)*
**Livrables :**
- **Dashboard Power BI** : santé de suite, flakiness, couverture et tendances dans le temps.
- Mapping final **capacités → 3 abonnements** matérialisé dans la démo (ce que chaque tier montre à l'écran).
- **Page de vente** des 3 offres + **script de prospection** (10 premières cibles startups).
- Script/storyboard de la **démo Loom** finalisée.
- ✅ *Livrable :* offre commercialisable de bout en bout.

### Phase 5 — Scalabilité *(plus tard, quand les premiers abonnés sont là)*
**Livrables :**
- Migration **docker-compose → Kubernetes** (exécution multi-clients isolée).
- Templatisation « onboarding d'un nouveau client en X jours ».
- Routage d'alerting et reporting multi-tenant.

---

## 8. Storyboard de la démo Loom (fil narratif cible)

1. **Accroche (15 s) :** « Un pipeline Playwright… sur l'app de démo de Cypress. » Écran : la RWA qui tourne.
2. **La suite verte (30 s) :** run CLI smoke + régression UI/API, rapport Mochawesome.
3. **L'automatisation (30 s) :** push commit → GitHub Actions (puis « et pareil sur GitLab ») → alerte Slack.
4. **Le moment QARVIS (60 s) :** je casse un sélecteur/une UI → run rouge → l'agent trie et dit « vraie régression ici, flaky là » + propose le correctif. Trace LangSmith à l'appui.
5. **La vue décideur (20 s) :** dashboard Power BI de tendance.
6. **Le pitch (20 s) :** les 3 abonnements à l'écran, « à partir de 600 €/mois, sans recruter de SDET ».

---

## 9. Hypothèses & hors-périmètre

- **Hors-périmètre POC :** k8s (repoussé Phase 5), tests de charge réels, auth tierce (Auth0/Okta/Cognito/Google) de la RWA — on reste sur l'auth locale pour la démo.
- **Hypothèses :** exécution locale/CI sur navigateurs Chromium en priorité (Firefox/WebKit en option) ; la RWA sert de proxy à « l'app d'un futur client » — tout est transposable.
- **Principe non négociable :** MCP au *build* des tests, jamais en dépendance de *run* en CI ; l'IA propose, l'humain garantit.

---

## 10. Ce que ce POC prouve commercialement

Que je vends un **résultat récurrent et cadré** — une suite qui reste verte, triée par l'IA, alertée et reportée — décliné en 3 niveaux de prix fixes. Pas des heures. Le POC est à la fois la **preuve technique** (ça marche de bout en bout) et le **support de vente** (la démo Loom et le mapping des offres). Mon avantage déloyal y est incarné, pas juste affirmé : un SDET qui **automatise le test par l'IA** peut tenir plusieurs abonnés en peu d'heures — ce qui est exactement ce qui transforme le service en produit.

---

## 11. Modules booster (au-delà du POC de base)

Idées classées par **rapport valeur/effort**, toutes alignées sur le mantra « clé en main, ajustable, pas d'heures indéterminées ». Elles ne sont pas toutes à faire tout de suite — c'est un menu d'évolution.

### Gains rapides (fort levier, faible effort) — à prioriser
- **Digest qualité hebdo auto-généré.** Un email/message récapitulatif de la semaine (santé, régressions attrapées, flakiness), rédigé par le LLM. Effort quasi nul, valeur perçue énorme, **renforce la rétention** (le client voit la valeur chaque semaine sans rien demander).
- **Bot de Pull Request.** QARVIS commente chaque PR : « ces tests couvrent ce changement / voici l'impact / attention zone non testée ». Point de contact au cœur du workflow dev, très différenciant.
- **Onboarding templatisé.** Un modèle reproductible « brancher un nouveau client en X jours » (repo type, configs CI, compose). C'est ce qui **protège tes 4h/jour** en rendant chaque nouvel abonné rapide à démarrer.

### Fort levier, effort moyen
- **Test impact analysis (sélection intelligente).** Ne lancer que les tests affectés par un changement → CI plus rapide et **moins chère**. Bon pour la marge et argument de vente direct (« vous payez moins de minutes CI »).
- **Traçabilité exigences → tests.** Ingestion Jira/Linear, mapping ticket ↔ test, alerte sur exigence non testée. Valeur forte pour le tier Quality Partner, alimente aussi le chatbot RAG.
- **Monitoring de production (synthetic).** Rejouer les smokes contre la prod du client sur planning (style uptime), pas seulement en CI. Nouvelle source de valeur récurrente, facilement un add-on.

### Structurants (à faire quand les abonnés arrivent)
- **Portail client multi-tenant.** Un dashboard où chaque client voit *son* statut, ses runs, son chatbot. C'est le passage de « prestation » à « vrai SaaS » (voir §12).
- **Evals-as-a-service pour features IA.** Beaucoup de tes clients shippent de l'IA ; leur vendre des suites d'évals dédiées est un produit à part entière, à forte marge, sur ton exact créneau rare (IA + test).
- **Posture sécurité formalisée.** Comme tu touches à la CI de tes clients, un modèle de sécurité clair (gestion des secrets, moindre privilège) devient un argument de vente — et prépare un futur discours type SOC2-light pour viser des clients plus gros.

> **Filtre de décision pour chaque module :** est-ce que ça (a) réduit mon temps par client, (b) augmente la rétention, ou (c) justifie un prix plus haut ? Si non → ce n'est pas prioritaire.

---

## 12. Cloudifier QARVIS sur AWS (architecture SaaS)

**Principe directeur pour une solo :** *serverless-first*. Tu veux un coût qui tend vers zéro quand c'est inactif, zéro serveur à administrer, et une infra reproductible par client. Et surtout **une distinction clé** : les *runs de tests* restent idéalement dans **la CI du client** (c'est lui qui paie le compute navigateur, gourmand en RAM) ; QARVIS n'héberge que le **control plane** (cerveau, chatbot, portail, reporting). L'exécution hébergée par QARVIS n'est qu'un *upsell* à part, tarifé pour couvrir son coût.

**Architecture cible (composants AWS) :**
- **Control plane / API & portail client :** conteneurs sur **ECS Fargate** (ou **App Runner**, encore plus simple pour démarrer). Pas de serveur à gérer.
- **Cerveau IA (agents LangGraph, triage, chatbot) :** **AWS Lambda** (tâches courtes) ou Fargate ; LLM via **Amazon Bedrock** (Claude y est disponible, tout reste dans AWS) ou l'API Anthropic directe.
- **RAG / base vectorielle :** **Aurora PostgreSQL Serverless v2 + pgvector** (simple, économique) ou **OpenSearch Serverless** (vectoriel managé). pgvector est le choix coût/simplicité pour démarrer.
- **Stockage artefacts** (rapports, traces, captures) : **S3**.
- **Métadonnées** (tenants, configs, historique de runs) : **DynamoDB** (serverless, quasi gratuit à petite échelle).
- **Orchestration & événements :** **EventBridge** + **SQS** pour déclencher triage/chatbot ; **Step Functions** si le pipeline se complexifie.
- **Auth du portail :** **Cognito**.
- **Alerting :** **SES** (email) + Lambda vers webhooks Slack/Discord/Teams.
- **Reporting :** dashboards statiques sur S3/CloudFront, embed **Power BI**, ou alternative native **QuickSight**.
- **Secrets** (tokens CI des clients) : **Secrets Manager**.
- **Infra as Code :** **Terraform** ou **AWS CDK** — indispensable en solo pour dupliquer proprement le setup par tenant.
- **Runners hébergés (upsell only) :** **CodeBuild** ou **Fargate/EC2 Spot** pour exécuter Playwright côté QARVIS — activé seulement pour les clients qui le paient.

**Séquencement :** ne construis **pas** ça avant d'avoir des clients payants. Tant que tu as 1-3 abonnés, un montage minimal (un petit App Runner + Aurora Serverless + S3 + l'API LLM) suffit. Le portail multi-tenant complet, c'est la **Phase 5** de la roadmap — quand le MRR le justifie.

---

## 13. Est-ce viable financièrement ?

Réponse courte : **oui, et avec une marge élevée** — à une condition claire (garder les runs dans la CI du client). Le raisonnement :

**Côté coûts (à petite échelle, serverless-first) :**
- Control plane + RAG + stockage + métadonnées : de l'ordre de quelques dizaines à ~100-300 €/mois selon l'activité (Fargate/App Runner + Aurora Serverless + S3 + DynamoDB restent bas quand c'est peu sollicité).
- LLM (triage + chatbot + digests) : coût **variable** à l'usage, typiquement quelques euros à quelques dizaines d'euros par client/mois selon le volume de requêtes. C'est ton principal poste variable — surveille-le.
- **Le poste qui peut exploser :** l'exécution des navigateurs Playwright (RAM++). C'est *précisément* pour ça qu'on la laisse chez le client par défaut, et qu'on la facture en add-on quand QARVIS l'héberge.

**Côté revenus (rappel) :** 3 à 5 abonnés bien choisis = **5 000 à 15 000 € de MRR** (Regression à ~1 500 €, Quality Partner à ~3 500 €+).

**La marge :** avec les runs chez le client, ton infra + LLM tourne à quelques centaines d'euros/mois face à plusieurs milliers de MRR → **marge brute typiquement 80-90 %+**. C'est le profil économique d'un vrai micro-SaaS, pas d'une prestation.

**Les vrais risques (à nommer honnêtement) :**
1. **Sur-ingénierie prématurée.** Construire la plateforme AWS multi-tenant complète *avant* d'avoir des clients = brûler du temps et un peu d'argent pour rien. Le plus gros risque n'est pas le coût cloud, c'est de coder au lieu de vendre.
2. **Coût LLM non maîtrisé** si le chatbot est très sollicité — mets des quotas par tier.
3. **Le goulot, c'est toi.** À ce modèle, la limite n'est pas financière mais ton temps de supervision/garantie. D'où l'importance des boosters qui réduisent le temps/client (§11).

**Verdict :** financièrement, oui, c'est valable — le modèle a une économie de SaaS (coût quasi fixe et bas, revenu récurrent qui scale). Mais la bonne stratégie est **inverse de l'instinct** : cloudifie *tard*, vends *tôt*. Le POC en Docker/compose + runs dans la CI client suffit pour signer tes premiers abonnés ; AWS devient pertinent quand tu passes de « quelques clients suivis à la main » à « une plateforme qui les onboarde en self-service » — et à ce stade, le MRR paie l'infra largement.

---

## 14. Livrables & Definition of Done (DoD) — le parapluie de livraison

Cette section garantit que **tout a été livré en temps et en heure et que le client est satisfait**. Règle d'or : la DoD se définit et se signe **au démarrage**, jamais à la fin — c'est ce qui évite la fin de mission floue où le client estime que « ce n'est pas fini ».

> **Distinction fondamentale à garder en tête :**
> - En **abonnement QARVIS** (modèle produit) : ce qui déclenche le paiement, c'est la **facture d'abonnement** + la **preuve de valeur du mois** (runs livrés, rapport). Les livrables techniques prouvent la valeur et sécurisent la **rétention**.
> - En **mission TJM / régie** (si tu opères chez un client au jour) : ce qui déclenche le paiement, c'est le **CRA validé + la facture**, PAS le livrable fini. En régie tu livres un *effort* et une *collaboration*, pas un résultat garanti à date. Les livrables techniques bouclent proprement la mission (réception, réputation, renouvellement).

### 14.1 Administratif — ce qui déclenche le paiement
**Modèle abonnement (QARVIS) :**
- [ ] Contrat / conditions d'abonnement signés (tier, périmètre borné, canaux, engagement).
- [ ] Facture mensuelle conforme (TVA selon statut).
- [ ] Preuve de valeur du mois : rapport de runs + digest qualité.

**Variante TJM / régie :**
- [ ] **CRA validé/signé par le client** — chaque mois, jamais en fin de mission.
- [ ] Facture conforme au CRA et au TJM contractuel.
- [ ] Bon de commande couvrant la période ; PV de réception si des jalons ont été contractualisés.

### 14.2 Technique — ce qui « boucle » la livraison
- [ ] **Framework de test** dans le repo du client, à ses conventions : architecture Playwright/TS (Page Objects), suites par couche (smoke, E2E, API, régression), BDD/Gherkin, fixtures/données de test, config multi-environnements.
- [ ] **Intégration CI/CD fonctionnelle** : pipeline (GitHub Actions / GitLab CI / autre) sur PR/merge/planning, sharding/parallélisation, règles de **gating**, Docker si utilisé, gestion propre des **secrets**, publication des artefacts (rapports, traces, screenshots, vidéos).
- [ ] **Reporting & alerting** : rapports lisibles (Playwright HTML / Mochawesome / Allure), **JUnit XML** pour le CI, alertes branchées (Slack/Discord/Teams/email) si au périmètre.
- [ ] **Volet MCP/IA documenté** : usage du MCP pour générer/maintenir les tests, avec le principe posé noir sur blanc — **MCP au build, jamais en dépendance de run en CI**.
- [ ] Suite **stable** (flakiness sous seuil convenu) et smoke qui **gate** réellement.

### 14.3 Documentation — ce qui rend le travail maintenable sans toi
- [ ] **README / guide de setup** : lancer en local et en CI.
- [ ] **Stratégie de test / test plan** : couverture, logique de pyramide, choix d'architecture.
- [ ] **Runbook opérationnel** : ajouter un test, débugger un échec, traiter un flaky.
- [ ] **Matrice de couverture / traçabilité** : parcours testés — et les trous, assumés honnêtement.

### 14.4 Passation — ce qui clôt vraiment
- [ ] **Transfert de connaissance** + démo du framework à l'équipe.
- [ ] **Pairing** pour que les devs internes sachent maintenir et étendre.
- [ ] **Rapport de fin de cycle/mission** : livré, couverture atteinte, limites connues, **recommandations pour la suite** (aussi ton meilleur argument de renouvellement).

### 14.5 Critères d'acceptation (la DoD, à convenir au jour 1)
La mission/le cycle est « done » quand :
- [ ] Le **chemin critique** est couvert et le pipeline est **vert**.
- [ ] La suite est **stable** (sous le seuil de flakiness convenu).
- [ ] La **doc** et la **passation** sont livrées.
- [ ] Le client a **réceptionné** (validation explicite, écrite).
- [ ] L'administratif (facture / CRA) est en règle.

> **Garde-fou réputation :** en abonnement comme en régie, une DoD écrite au démarrage protège à la fois ton paiement, ton renouvellement et ta crédibilité. Le détail exact dépend du **contrat** — relis-le en début de mission pour connaître les livrables contractuels et les modalités de réception.
