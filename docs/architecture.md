# Architecture

```
            ┌────────────────────┐
            │  Streamlit (8501)  │  étudiants + administrateur
            └─────────┬──────────┘
                      │ HTTP/JSON
            ┌─────────▼──────────┐        ┌──────────────┐
            │   FastAPI (8000)   │───────►│  Groq (LLM)  │
            │  auth • chat • docs│        └──────────────┘
            │  RAG: embeddings   │
            │  locaux + retrieval│
            └───▲──────────┬─────┘
   /internal    │          │ SQL
   (clé API)    │   ┌──────▼──────────────────────┐
         ┌──────┴───┤ PostgreSQL + pgvector (5432)│
         │   n8n    │ users • documents • chunks  │
         │  (5678)  │ conversations • messages    │
         └──────────┴─────────────────────────────┘
```

## Flux d'ingestion
Document (PDF/TXT) → extraction du texte → découpage en chunks → embeddings → stockage
(chunks + vecteurs) dans PostgreSQL/pgvector.

## Flux d'une question
Question → embedding de la requête → recherche top-k (similarité cosinus) → seuil de confiance
→ prompt contraint + extraits → LLM (Groq) → réponse + sources (ou refus explicite).
