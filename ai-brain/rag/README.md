# rag/

Module "Ask QARVIS" : ingestion (loaders sur résultats de runs, rapports Mochawesome/JUnit, logs,
code de test, traces LangSmith) -> splitting -> embeddings -> stockage `pgvector` -> retrieval.
Interface : widget web + (option) bot Slack/Discord.
