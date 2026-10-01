# TP01 — Elasticsearch et Kibana

Rendu du TP d’introduction : lancement de la stack, mapping, ingestion de 5 000 offres, recherches Query DSL, agrégations et mini-moteur Python.

## Fichiers principaux

- `docker-compose.yml` : stack corrigée utilisée pour le TP.
- `ingest.py` : création de l’index et ingestion NDJSON.
- `search.py` : mini-moteur de recherche.
- `requetes/partie1.txt`, `partie3.txt`, `partie4.txt` : requêtes Kibana Dev Tools.
- `REPONSES.md` : réponses aux exercices.

## Lancement

1. Copier `.env.example` en `.env` et remplacer les secrets. Ne jamais versionner `.env`.
2. `docker compose up -d`
3. `python -m venv .venv`, activer l’environnement puis `python -m pip install -r requirements.txt`.
4. `python data/generate_offres.py` puis `python ingest.py --reset`.

Les fichiers de données générés et l’environnement virtuel sont ignorés par Git.
