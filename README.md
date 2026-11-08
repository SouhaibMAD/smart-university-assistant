# 🎓 Smart University Assistant

Assistant intelligent d'information universitaire basé sur une architecture **RAG**
(Retrieval-Augmented Generation).

## Problématique
Les règlements, guides pédagogiques et procédures administratives sont dispersés dans de
nombreux documents. Les étudiants perdent du temps à chercher l'information, et obtiennent
souvent des réponses contradictoires. 

## Objectifs
- Répondre en langage naturel aux questions sur la vie universitaire, les études et les procédures.
- Fournir des réponses **traçables** : chaque réponse cite les documents et pages utilisés.
- Refuser de répondre plutôt qu'inventer lorsque l'information est absente des documents.

## Utilisateurs
- **Étudiants** : posent des questions, consultent l'historique de leurs conversations.
- **Administrateur** : importe et gère les documents (PDF / TXT).

## Fonctionnalités
- Gestion des documents (import, liste, suppression)
- Assistant conversationnel
- Recherche sémantique des passages pertinents
- Affichage des sources
- Historique des conversations
- Réponses fiables (refus explicite hors corpus)
- Automatisation n8n (ingestion automatique, rapport des questions sans réponse)

## Architecture
Voir [docs/architecture.md](docs/architecture.md).

| Composant | Rôle |
|---|---|
| Streamlit | Interface étudiants + administration |
| FastAPI | API REST, authentification, orchestration RAG |
| PostgreSQL + pgvector | Données applicatives et vecteurs |
| Groq (`qwen/qwen3.8-27b`) | Génération des réponses |
| sentence-transformers (e5 multilingue) | Embeddings locaux |
| n8n | Workflows d'automatisation |

## Installation
Prérequis : Docker et Docker Compose, une clé API Groq.

```bash
git clone <url-du-depot>
cd smart-university-assistant
cp .env.example .env      # puis renseigner GROQ_API_KEY et changer les secrets
docker compose up --build
```

## Exécution
| Service | URL |
|---|---|
| Interface Streamlit | http://localhost:8501 |
| Documentation API (Swagger) | http://localhost:8000/docs |
| n8n | http://localhost:5678 |

Créer le compte administrateur :
```bash
docker compose exec backend python /scripts/seed_admin.py
```

## Tests
```bash
docker compose exec backend pytest -q
```

## Évaluation
Résultats et méthodologie : voir la page *Évaluation* de l'interface et le dossier `evaluation/`.

## Structure du dépôt
Voir `docs/architecture.md` et l'arborescence du projet.
