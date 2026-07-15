# Cahier des charges — QARVIS

### Projet de startup solopreneur · SaaS de tests automatisés Playwright + IA/MCP

> **Mantra directeur du projet :** *je vends un service clé en main et ajustable — un résultat récurrent, pas des heures indéterminées.* Objectif de vie : **~4h de travail par jour**, de n'importe où, pendant que le pipeline de tests du client tourne.

---

## Synthèse QQOQCCP (vue rapide)

| Axe | En une phrase |
|---|---|
| **Quoi** | Un SaaS/service d'abonnement qui maintient la suite de tests E2E + API d'un produit verte en continu, avec une couche IA (MCP) qui génère et trie les tests. |
| **Qui** | Moi, solopreneuse SDET (test + IA) ; cible : startups SaaS seed–série A sans QA dédiée ; décideur : CTO / Head of Eng / fondateur technique. |
| **Où** | 100 % remote, marché France/francophone d'abord ; exécution dans la CI du client ; control plane cloud (AWS, plus tard). |
| **Quand** | Lancement progressif à 4h/jour ; POC + démo à 3 mois, 1er client à ~5 mois, revenu cible à 12–15 mois. |
| **Comment** | Pipeline Playwright CLI (UI+API) + MCP + Docker + multi-CI + alerting + IA (LangChain/LangGraph/LangSmith) + reporting ; vendu en 3 abonnements bornés. |
| **Combien** | Offres de 600 à 3 500 €+/mois ; objectif ~4 000 € net/mois ; marge SaaS 80–90 % ; coût infra bas et différé. |
| **Pourquoi** | Un marché en tension (QA+IA), un avantage rare (SDET qui automatise le test par l'IA), et un mode de vie choisi : liberté, produit, revenu récurrent. |

---

## 1. QUOI — De quoi s'agit-il ?

**Le produit.** QARVIS (*QA + JARVIS*) est un service d'abonnement qui installe, fait grandir et **maintient** la suite de tests automatisés d'un produit logiciel, et garantit qu'elle reste **verte à chaque déploiement**. Une couche d'IA génère les tests (via Playwright MCP), trie les échecs (vraie régression vs test instable), suggère les correctifs, et répond aux questions du client via un **chatbot RAG** sur ses propres données de test.

**Le périmètre inclus :** tests UI + API (Playwright CLI), smoke/E2E/régression/BDD, intégration CI/CD (GitHub Actions **et** GitLab CI), conteneurisation Docker, alerting multi-canal (Slack/Discord/Teams/email), reporting (Mochawesome + dashboard), triage IA, chatbot RAG, documentation et passation.

**Hors périmètre (assumé) :** développement applicatif du produit client, tests de charge lourds, refonte produit. QARVIS teste et fiabilise ; il ne développe pas l'app.

**Nature du livrable :** un **résultat récurrent cadré**, décliné en 3 formules à périmètre et prix fixes — jamais un compteur d'heures.

---

## 2. QUI — Qui est concerné ?

**Le porteur (moi).** Solopreneuse, profil SDET spécialisée **test automatisé + IA/agents** — un croisement rare qui est l'avantage déloyal du projet. Rôle : conception, supervision et garantie ; l'IA fait le gros de la génération/maintenance.

**Le client cible (ICP).** Startups / scale-ups SaaS, stade **seed à série A**, ~8 à 40 personnes (5–25 devs), **sans ingénieur QA/SDET dédié**, qui shippent vite. Secteurs prioritaires où un bug coûte cher : fintech/paiement, healthtech, data sensible, B2B SaaS à clients payants. Stack idéale JS/TS (React/Vue).

**Le décideur / interlocuteur.** CTO, Head of Engineering, Lead Dev ou fondateur technique — celui qui *ressent* la douleur des régressions et signe. Pas les RH.

**Les utilisateurs finaux du service.** Les développeurs du client (reçoivent rapports et alertes, interrogent le chatbot) et les décideurs (dashboard de tendance).

**Les parties prenantes externes.** Expert-comptable, éventuelle société de portage, fournisseurs cloud/LLM (AWS, Anthropic/Bedrock).

---

## 3. OÙ — Où le projet se déploie-t-il ?

**Mode de travail :** 100 % **remote**, de n'importe où (contrainte de vie centrale).

**Marché géographique :** **France / francophone en priorité** (même langue, même fuseau, confiance facilitée pour les premiers clients), élargissement remote ensuite.

**Où s'exécute la technique :**
- Les **tests tournent dans la CI du client** (GitHub Actions / GitLab CI) — c'est lui qui porte le compute, ce qui protège la marge.
- Le **control plane** (cerveau IA, chatbot, portail, reporting) est hébergé côté QARVIS, en **cloud AWS** — mais *plus tard* (voir roadmap), pas au démarrage.

**Où se fait la vente :** LinkedIn (canal principal), email, job boards et bases de financement comme mines de prospection (Welcome to the Jungle, Dealroom, Crunchbase, écosystème French Tech / Station F).

---

## 4. QUAND — Dans quel calendrier ?

**Contrainte structurante :** un rythme de **~4h de travail par jour**. Le calendrier est donc pensé pour une solo à temps partiel, pas une équipe à plein temps.

**Grands jalons (détaillés en roadmap SMART §8) :**
- **Vendre tôt, cloudifier tard** — principe de séquencement non négociable.
- POC technique + démo Loom : ~**3 mois**.
- Premier abonné signé : ~**5 mois**.
- Revenu cible (~4 000 € net/mois) : **12–15 mois**.
- Industrialisation (onboarding templatisé, début cloud AWS) : **12–18 mois**.
- Structuration / changement de statut (SASU) et scale : **18–24 mois**.

---

## 5. COMMENT — Par quels moyens ?

**Comment techniquement (le pipeline).** Playwright CLI (UI + API) en TypeScript, structuré en pyramide (smoke, E2E, API, régression) + BDD/Gherkin ; génération et maintenance assistées par **Playwright MCP** ; orchestration **Docker/docker-compose** (→ Kubernetes plus tard) ; **multi-CI** (GitHub Actions et GitLab CI) avec gating et sharding ; **alerting** Slack/Discord/Teams/email ; **IA** en Python (LangChain / LangGraph / LangSmith) pour triage, self-healing et evals ; **chatbot RAG** ; **reporting** Mochawesome + Power BI/QuickSight.

> Principe non négociable : **MCP au *build* des tests, jamais en dépendance de *run* en CI.** L'IA propose, l'humain garantit.

**Comment commercialement (le modèle).** Vente en **abonnement** (MRR), 3 formules à périmètre borné : Smoke (~600–900 €), Regression (~1 500–2 200 €, offre phare), Quality Partner (~3 500–4 500 €). Prospection ciblée par lots de 10–12, avec offre de **valeur d'abord** (smoke test gratuit) pour décrocher le premier client sans étude de cas.

**Comment la livraison est cadrée (DoD).** Chaque engagement est encadré par une **Definition of Done écrite au jour 1** : administratif (facture/preuve de valeur, ou CRA en régie), technique (framework + CI + reporting), documentation, passation, critères d'acceptation. C'est le parapluie qui garantit « livré à temps + client satisfait ».

**Comment la charge reste à 4h/jour.** Automatisation par l'IA, onboarding templatisé, digests auto-générés, chatbot qui absorbe les questions — chaque brique vise à **réduire le temps par client**.

---

## 6. COMBIEN — Quels coûts et quels gains ?

**Objectif de revenu :** **~4 000 € net/mois**, soit ~5 400–6 500 € de CA/mois en micro (≈ 65–78 k€/an, sous le plafond micro de 83 600 €). Atteignable avec **3 abonnés Regression** ou **2 Regression + 1 Quality Partner**.

**Coûts du projet :**
- Démarrage : quasi nul (POC en local/Docker, outillage open-source, Apple/infra non requis).
- Infra cloud (différée) : quelques dizaines à ~300 €/mois à petite échelle (serverless-first).
- LLM (triage/chatbot/digests) : variable, quelques € à quelques dizaines €/client/mois — à encadrer par des quotas.
- Poste à risque : l'exécution navigateur hébergée (RAM++) → laissée au client, facturée en add-on sinon.

**Marge :** avec les runs chez le client, **marge brute typiquement 80–90 %+** — économie de micro-SaaS, pas de prestation.

**Investissement en temps :** 4h/jour, avec un ramp-up avant le premier revenu (période à financer/absorber).

**Seuil de bascule statut :** au-delà de ~7–8 k€/mois de CA, envisager SASU/EI au réel (sortie du plafond micro).

---

## 7. POURQUOI — Quelle raison d'être ?

**Le problème résolu.** Les startups qui shippent vite sans QA dédiée sont coincées entre « pas de tests » (on prie à chaque déploiement) et « des tests pourris » (rouges, ignorés). Recruter un SDET coûte 50–70 k€/an + le recrutement. QARVIS est la troisième voie : la qualité en continu, en abonnement, sans embaucher.

**Le pourquoi marché.** La demande QA est en tension, et la **prime IA/MCP** dans le testing est en train de se construire (testing augmenté par IA visé à ~70 % de pénétration entreprise d'ici 2028). Se positionner maintenant = être tôt sur la vague.

**Le pourquoi personnel (la vraie motivation).** Un mode de vie choisi : **liberté géographique, ~4h/jour, revenu récurrent et prévisible**, un business **produit** qui ne dépend pas de la vente de mes heures. QARVIS est le véhicule qui aligne mon avantage rare (SDET + IA) avec la vie que je veux.

---

## 8. Roadmap SMART

Chaque objectif est **S**pécifique, **M**esurable, **A**tteignable, **R**éaliste, **T**emporellement défini. Les échéances sont en mois relatifs au lancement (M0), calibrées pour un rythme de 4h/jour.

### 🎯 Objectif 1 — POC technique + démo (échéance : M+3)
- **S** : Livrer un pipeline QARVIS fonctionnel de bout en bout sur la Cypress Real World App + une démo Loom de 3 min.
- **M** : Pipeline vert (smoke + UI + API), triage IA opérationnel, 1 vidéo Loom publiée.
- **A** : Réutilise ma stack existante ; périmètre borné à une app de démo.
- **R** : Réalisable en ~3 mois à 4h/jour car sans client à gérer en parallèle.
- **T** : **M+3.**

### 🎯 Objectif 2 — Actifs commerciaux + pipeline de prospection (échéance : M+4)
- **S** : Publier la page de vente des 3 offres et constituer une liste de 30 prospects qualifiés (ICP).
- **M** : Page en ligne + 30 prospects avec signal d'achat documenté + 3 messages de prospection prêts.
- **A** : Cibles identifiables via LinkedIn/job boards ; templates déjà rédigés.
- **R** : 1 mois suffit en parallèle de la finition du POC.
- **T** : **M+4.**

### 🎯 Objectif 3 — Premier client fondateur signé (échéance : M+5)
- **S** : Convertir un prospect en 1er abonné payant (via offre « valeur d'abord »).
- **M** : 1 contrat signé + 1er paiement encaissé + 1 étude de cas en cours de constitution.
- **A** : Atteignable avec ~30 approches personnalisées et un smoke test offert.
- **R** : Réaliste dès lors que la démo et l'offre existent (Objectifs 1–2 faits).
- **T** : **M+5.**

### 🎯 Objectif 4 — Validation du modèle (échéance : M+9)
- **S** : Atteindre **3 abonnés actifs** et un premier socle de MRR.
- **M** : 3 clients payants, ~4 000–5 000 € de MRR, taux de churn = 0 sur la période.
- **A** : Le 1er client sert de preuve pour les suivants ; boosters de rétention en place.
- **R** : Réaliste avec un rythme de prospection continu par lots.
- **T** : **M+9.**

### 🎯 Objectif 5 — Revenu cible atteint (échéance : M+15)
- **S** : Sécuriser un revenu de **~4 000 € net/mois** stable et récurrent.
- **M** : MRR ≥ 5 400 € maintenu 3 mois consécutifs ; charge de travail ≤ 4h/jour vérifiée.
- **A** : Atteignable via 3 Regression ou un mix incluant un Quality Partner.
- **R** : Cohérent avec le plafond micro et la marge du modèle.
- **T** : **M+15.**

### 🎯 Objectif 6 — Industrialisation & cloudification (échéance : M+18)
- **S** : Réduire le temps par client et poser les bases SaaS (onboarding templatisé + control plane AWS minimal).
- **M** : Onboarding d'un nouveau client en ≤ 3 jours ; portail client v1 en ligne ; temps/client réduit de 30 %.
- **A** : Financé par le MRR existant ; serverless-first pour limiter le coût.
- **R** : N'est lancé qu'*après* validation du revenu (évite la sur-ingénierie prématurée).
- **T** : **M+18.**

### 🎯 Objectif 7 — Structuration & scale (échéance : M+24)
- **S** : Passer un cap de structure (statut adapté) et dépasser le plafond du modèle initial.
- **M** : ≥ 5 abonnés / MRR ≥ 8 000 € ; bascule vers SASU/EI au réel étudiée et décidée.
- **A** : Justifié par le volume ; accompagné par l'expert-comptable.
- **R** : Réaliste sur 2 ans à ce rythme et avec l'effet composé des boosters.
- **T** : **M+24.**

---

## 9. Contraintes & risques

**Contraintes :** temps limité (4h/jour) ; solo (goulot = moi) ; plafond micro ; pas d'étude de cas au départ ; dépendance aux coûts LLM variables.

**Risques principaux :**
1. **Sur-ingénierie prématurée** — construire le cloud avant les clients. *Parade :* vendre tôt, cloudifier tard.
2. **Scope creep** — l'abonnement redevient du temps-contre-argent. *Parade :* périmètre borné + avenants.
3. **Le goulot d'étranglement, c'est moi.** *Parade :* boosters qui réduisent le temps/client.
4. **Acquisition lente** du 1er client. *Parade :* offre « valeur d'abord » + volume de prospection ciblée.
5. **Coût LLM non maîtrisé.** *Parade :* quotas par tier.

---

## 10. Facteurs clés de succès & indicateurs

**Facteurs clés :** un ICP précis, une offre clé en main réellement cadrée, une preuve (démo + 1er client), et une discipline de rétention.

**Indicateurs à suivre :** MRR, nombre d'abonnés, taux de churn, temps réel travaillé/jour, temps d'onboarding par client, coût LLM/client, taux de réponse en prospection, marge brute.

> **Boussole de décision, à chaque arbitrage :** est-ce que cette action (a) réduit mon temps par client, (b) augmente la rétention, ou (c) justifie un prix plus haut ? Si non → ce n'est pas prioritaire.
