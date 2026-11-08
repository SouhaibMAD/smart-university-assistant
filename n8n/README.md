# Workflows n8n

Les workflows exportés (JSON, **sans identifiants**) sont versionnés dans `workflows/`.

- Interface : http://localhost:5678
- Import : *Workflows → Import from file* puis sélectionner le JSON.
- Les workflows appellent l'API via `http://backend:8000` avec l'en-tête `X-API-Key`.
