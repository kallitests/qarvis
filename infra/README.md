# infra/

```bash
docker compose up -d       # RWA (front :3000 + API :3001) + Postgres/pgvector
docker compose down -v     # arrêt + suppression des volumes
```

`iac/` : Terraform/CDK pour le control plane AWS (différé, cf. spec technique §3.5, Phase 5).
