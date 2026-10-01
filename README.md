# TP Elasticsearch, Kibana et Logstash

Rendu des TP 01 et 02 — Diginamic EISI.

## Contenu

- TP01 : Docker Compose, Elasticsearch/Kibana, mapping, ingestion Python, recherches et agrégations.
- TP02 : Logstash, pipelines `offres` et `web`, ingestion de logs, requêtes d'enquête.
- `REPONSES.md` rassemble les réponses et les résultats calculés avec les jeux de données fournis.

## Lancer le TP01

1. Copier `.env.example` vers `.env`, puis remplacer les valeurs de démonstration par tes propres secrets.
2. Créer l'environnement Python et installer les dépendances :

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

3. Démarrer Elasticsearch et Kibana :

   ```powershell
   docker compose up -d
   ```

4. Générer et ingérer les offres :

   ```powershell
   python data/generate_offres.py
   python ingest.py --reset
   ```

## Lancer le TP02

1. Ajouter `LOGSTASH_INTERNAL_PASSWORD` dans `.env`.
2. Dans Kibana Dev Tools, exécuter les requêtes de `requetes/logstash.txt`, en remplaçant le marqueur du mot de passe par la même valeur que dans `.env`.
3. Générer les logs et lancer Logstash :

   ```powershell
   python data/generate_access_logs.py
   docker compose up -d logstash
   ```

4. Vérifier les deux flux avec les requêtes de `requetes/enquete.txt` et Kibana Discover.

Exécuter les requêtes de fichiers `.txt` une par une dans Dev Tools. La capture du tableau de bord demandée par le TP02 est à enregistrer dans `captures/tableau-de-bord.png` après sa création dans Kibana.

## Sécurité du dépôt

Ne jamais ajouter `.env`, `data/offres.ndjson`, `data/access.log`, un mot de passe ou une clé privée à Git. Le `.gitignore` exclut les secrets et les fichiers de données générés.
