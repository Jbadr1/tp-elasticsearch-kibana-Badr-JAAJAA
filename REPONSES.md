# Réponses au TP Elasticsearch et Kibana

## Exercice 0

Les réponses obtenues dans Kibana et avec `curl` authentifié sont identiques : Elasticsearch 9.5.4, nœud `es01`, cluster `tp-eisi`. Sans authentification, le serveur renvoie le code HTTP `401 Unauthorized` et précise que les informations d'authentification sont absentes. Kibana utilise la session ouverte par l'utilisateur et transmet automatiquement ses informations de sécurité.

## Partie 1

### Exercice 1.1

La version utilisée est Elasticsearch 9.5.4. Le cluster possède un seul nœud, `es01`. Les index commençant par un point sont des index système créés par Elasticsearch et Kibana pour leur fonctionnement interne.

### Exercice 1.2

La version du document passe de 1 lors de sa création à 2 lors de sa modification, puis à 3 lors de sa suppression. Le document créé avec `POST` reçoit un identifiant généré automatiquement par Elasticsearch. Dans notre essai, cet identifiant était `zehl7aABnkErfUka42ia`. L'index `essai` n'existait pas avant le premier `PUT` : Elasticsearch l'a créé automatiquement.

### Exercice 1.3

Le champ `salaire` reçoit le type `text` avec un sous-champ `keyword`, car sa première valeur était une chaîne de caractères. `publication` reçoit le type `date`. Le second document est accepté car une valeur numérique peut être convertie en chaîne. En revanche, un salaire stocké comme texte ne permet pas d'effectuer correctement des comparaisons numériques comme `salaire > 50000`.

### Exercice 1.4

Un champ inconnu produit une `strict_dynamic_mapping_exception` avec le code 400. Le mapping strict évite l'ajout involontaire de champs mal orthographiés ou possédant un mauvais type. Cela améliore la qualité et la stabilité des données en production.

## Partie 2

### Exercice 2.2

Le nombre de documents ne double pas : il reste égal à 5 000. Le champ `id` est utilisé comme `_id` Elasticsearch. Une nouvelle ingestion remplace donc le document qui possède déjà le même identifiant. Avec des identifiants générés automatiquement, chaque ingestion créerait de nouveaux documents et le total passerait à 10 000.

### Exercice 2.3

Seul le document contenant le champ inconnu `prime` est rejeté. Les 5 000 documents valides sont traités. `raise_on_error=False` permet au pipeline de poursuivre l'ingestion et de récupérer la liste des erreurs au lieu de s'arrêter à la première erreur.

### Exercice 2.4

L'index `offres` est vert, contient 5 000 documents et possède un shard primaire sans réplique. Le document `OFF-00002` est bien retrouvé.

## Partie 3

### Exercice 3.1

Avec l'analyseur français, `les`, `sur` et `des` disparaissent. `l'analyse` devient `analys`. `donnée` et `données` deviennent toutes les deux `done`, alors que l'analyseur standard conserve deux termes différents. L'analyseur français permet donc de retrouver plus facilement les variantes d'un mot.

### Exercice 3.2

Les requêtes `term` initiales renvoient zéro résultat parce que `term` n'analyse pas la valeur. Le champ `ville`, de type `keyword`, contient exactement `Paris` avec une majuscule et non `paris`. Le champ `titre`, de type `text`, est analysé et ne conserve pas la phrase complète comme un terme unique. Les corrections sont `Paris` pour la ville et `titre.brut` pour le titre exact. Avec les données générées, le `match` en mode OU renvoie 2 774 documents, contre 393 en mode AND, car les deux mots deviennent obligatoires.

### Exercice 3.3

Le paramètre `fuzziness: AUTO` permet de corriger la faute `kubernetis`. Le poids `titre^3` donne trois fois plus d'importance aux correspondances trouvées dans le titre, qui remontent donc dans le classement.

### Exercice 3.4

Pour respecter l’énoncé, les requêtes booléennes utilisent le terme « données ». Le jeu généré contient des titres « Administrateur Bases de Données », que l’analyseur français permet de retrouver. Avec les filtres de l’exercice, 25 offres correspondent.

### Exercice 3.5

Le filtre `geo_distance` conserve les offres situées à moins de 20 km de Montpellier. Le tri `_geo_distance` les classe de la plus proche à la plus éloignée.

### Exercice 3.6

Pour une page 2 contenant 5 résultats, `from` vaut 5 et `size` vaut 5. Elasticsearch limite par défaut `from + size` à 10 000 pour éviter un coût trop important en mémoire et en calcul. Pour une pagination profonde, il faut utiliser `search_after` avec un point in time (PIT).

## Partie 4

### Exercice 4.1

Avec le jeu déterministe fourni, Paris possède le salaire minimum moyen le plus élevé, environ 57 441,65 euros. Cette moyenne est calculée sur 994 offres parisiennes qui possèdent réellement un salaire. Sur l'ensemble de l'index, 3 389 offres possèdent le champ `salaire_min`. Une agrégation directement sur `titre` produit une erreur indiquant que `fielddata` est désactivé sur les champs `text`. Il faut utiliser le sous-champ `titre.brut`, qui est de type `keyword`.

### Exercice 4.2

`date_histogram` crée un groupe pour chaque mois. La sous-agrégation `terms` répartit ensuite les offres de chaque mois selon leur contrat.

### Exercice 4.3

Le jeu fourni contient 484 offres avec un salaire inférieur à 40 000 euros, 1 363 entre 40 000 et 54 999 euros et 1 542 à partir de 55 000 euros. L'agrégation `stats` fournit pour chaque tranche le nombre de valeurs, le minimum, le maximum, la moyenne et la somme de l'expérience.

### Exercice 4.4

Pour les 462 offres Data Engineer, les cinq compétences les plus fréquentes sont Airflow (315), Spark (313), Kafka (312), Python (311) et SQL (301). Le télétravail partiel est le plus fréquent avec 284 offres. Les agrégations portent uniquement sur les documents retenus par la requête, et non sur tout l'index.

## Mini-défi

Le script `search.py` utilise une requête `bool`, une recherche `multi_match`, des filtres facultatifs, la pagination, le surlignage et trois facettes : villes, contrats et compétences.


---

# TP2 Logstash — comparaison et réponses

## Comparaison avec le TP fait hier

Le travail d'hier correspond au TP1 : Elasticsearch et Kibana sous Docker, index `offres`, mapping strict, ingestion Python, recherche et agrégations.

Le dépôt GitHub a été mis à jour avec le kit TP2. La capture fournie montre le nouveau commit « add: kit TP2 sorry ». Mon premier clonage datait de la révision précédente ; ma remarque disant que les configurations et le générateur manquaient était donc erronée.

Deux différences à conserver en tête :

- Le `docker-compose.yml` de TP1 sur GitHub contient toujours l'ancienne commande du service `setup`. Garde la version corrigée par ton professeur, celle que tu as utilisée hier.
- Le kit TP2 officiel contient désormais `docker-compose.override.yml`, `pipelines.yml`, les deux pipelines et `generate_access_logs.py`. L'archive inclut ces fichiers officiels tels quels.

## Mise en place

- Un compte `logstash_internal` limite les droits d'écriture de Logstash aux index `offres` et `logs-web-*`. Le compte `elastic` est administrateur : il ne doit pas être utilisé par le pipeline.
- Une écriture dans `logs-generic-default` doit être refusée, car ce nom n'est pas dans les index autorisés du rôle.
- Le secret est conservé dans `.env`, puis transmis par variable d'environnement. Il ne doit pas être écrit dans les fichiers `.conf` ou versionné dans Git.
- `--path.data /tmp/essai` donne à l'instance éphémère un répertoire de données propre.
- Pour le pipeline stdin, `@timestamp` correspond au moment où Logstash reçoit la phrase.

## Partie 1 — Recharger les offres

Le pipeline lit chaque objet JSON du fichier. Le filtre supprime `@timestamp`, `@version`, `event`, `log` et `host`, ajoutés par Logstash et refusés par le mapping strict. Il écrit ensuite dans l'index déjà créé `offres`, avec l'identifiant métier `id` comme `_id`.

Résultat attendu : 5 000 documents. Une nouvelle lecture ne double pas le nombre, car chaque document reprend le même `_id` et l'action `index` remplace l'ancienne version. Sans `document_id`, Elasticsearch générerait un nouvel identifiant à chaque passage.

Avec `sincedb_path => "/dev/null"`, Logstash ne mémorise pas la position du fichier et le relit au redémarrage. Avec une sincedb persistante, il reprend à la position enregistrée.

Le mapping strict protège la forme des documents métier. Le pipeline retire donc les métadonnées supplémentaires au lieu d'élargir le mapping.

## Partie 2 — Supervision et fiabilité

- `in` compte les événements reçus, `filtered` ceux traités par le filtre et `out` ceux transmis à la sortie, depuis le démarrage du pipeline. Les durées par plugin permettent d'identifier l'étape la plus coûteuse.
- La DLQ conserve sur disque des événements rejetés pour une erreur non temporaire, comme une erreur de mapping. `helpers.bulk(..., raise_on_error=False)` affiche les erreurs et poursuit le lot, mais ne constitue pas une file de reprise.
- Sans `pipelines.yml`, les fichiers du dossier sont concaténés en un seul pipeline `main`; chaque événement peut traverser les filtres et sorties des deux flux. Les pipelines séparés isolent les flux et ont leurs propres compteurs, workers et files.
- Une file mémoire est perdue si Logstash est tué avant l'envoi. `queue.type: persisted` écrit la file sur disque et offre une livraison « au moins une fois ». Un identifiant stable évite alors les doublons à la destination.

Pour traiter un document de la DLQ : lire la cause et l'événement, corriger les données ou le pipeline, puis rejouer l'événement corrigé et vérifier sa présence dans Elasticsearch.

## Partie 3 — Logs d'accès

Le générateur officiel produit **20 700 lignes** sur sept jours. Le pipeline `web` applique `COMBINEDAPACHELOG`, convertit la date anglaise en `@timestamp`, enrichit le navigateur, extrait l'identifiant des URLs `/offres/OFF-xxxxx` vers `labels.offre_id`, puis écrit dans le data stream `logs-web-default`.

Les logs sont horodatés avec le fuseau `+0200`. Kibana peut les afficher à l'heure locale du navigateur ; Elasticsearch les stocke en UTC.

Résultats attendus après une première ingestion : 20 700 documents, zéro échec Grok. Lors d'une nouvelle lecture, le data stream reçoit de nouveaux documents et le compteur peut doubler, car les événements n'ont pas de `_id` stable. Pour éviter cela, on peut laisser une sincedb persistante pour ne pas relire les anciennes lignes ou calculer un identifiant de contenu reproductible avec `fingerprint` (en respectant les contraintes d'écriture du data stream).

## Partie 4 — Enquête : résultats du générateur officiel

Ces chiffres ont été calculés à partir de `generate_access_logs.py` avec ses paramètres par défaut (`--lignes 20000 --seed 42`). Il faut exécuter Kibana sur le même fichier pour confirmer les résultats d'indexation.

### 4.1 Vue d'ensemble

| Statut HTTP | Nombre |
| --- | ---: |
| 200 | 17 805 |
| 201 | 1 492 |
| 404 | 508 |
| 304 | 488 |
| 503 | 402 |
| 500 | 5 |

| Méthode | Nombre |
| --- | ---: |
| GET | 19 208 |
| POST | 1 492 |

La moyenne est de **2 957 requêtes par jour** (20 700 / 7). Les volumes réels varient selon les jours, car les événements sont répartis aléatoirement.

### 4.2 Incident

- **Jour :** lundi 28 septembre 2026.
- **Créneau :** 14 h 00 à 14 h 45, heure de Paris (12 h 00 à 12 h 45 UTC).
- **Impact :** 402 réponses 503 pendant ces 45 minutes. Les cinq réponses 500 du jeu sont des erreurs isolées hors de cette plage.
- **URL touchée :** l'API `/api/offres` avec différents paramètres de ville et de page. Les autres familles de routes ne reçoivent pas de 5xx pendant l'incident.
- Le générateur ajoute 400 requêtes 503 pour simuler une hausse de trafic liée aux tentatives de répétition. Dans la fenêtre, on compte 478 requêtes au total, dont 402 sont en 503.

Les URL exactes en erreur sont regroupées par `url.original` par la requête fournie dans `enquete.txt`.

### 4.3 Activité suspecte

- **IP :** `203.0.113.66`.
- **Période :** 26 septembre 2026, de 03:12:00 à 03:16:59 (heure de Paris), soit une rafale de cinq minutes.
- **Nombre :** 300 requêtes 404, une par seconde.
- **User-Agent :** `Mozilla/5.0 zgrab/0.x`, signature d'un outil de scan plutôt que d'un navigateur habituel.

| URL recherchée | Nombre |
| --- | ---: |
| `/admin` | 59 |
| `/.git/config` | 55 |
| `/.env` | 53 |
| `/phpmyadmin/` | 46 |
| `/server-status` | 44 |
| `/wp-login.php` | 43 |

Les **208 autres 404** sont dispersées entre différentes adresses et correspondent principalement à des identifiants d'offres inexistants générés aléatoirement. Elles ne forment pas une rafale comparable.

### 4.4 Offres les plus consultées

Les dix identifiants à rechercher dans l'index `offres` sont : `OFF-04662`, `OFF-01153`, `OFF-03141`, `OFF-00901`, `OFF-02899`, `OFF-03524`, `OFF-00289`, `OFF-01275`, `OFF-03145`, `OFF-03126`.

| ID | Consultations | Titre | Ville | Contrat |
| --- | ---: | --- | --- | --- |
| OFF-04662 | 8 | Développeur Front-end Senior | Bordeaux | Freelance |
| OFF-01153 | 7 | Développeur Java Confirmé | Toulouse | Freelance |
| OFF-03141 | 7 | Développeur Python Confirmé | Bordeaux | CDI |
| OFF-00901 | 6 | Développeur Java Junior | Paris | CDI |
| OFF-02899 | 6 | Data Engineer (Alternance) | Lyon | Alternance |
| OFF-03524 | 6 | Développeur Python (Alternance) | Toulouse | Alternance |
| OFF-00289 | 6 | Data Scientist Lead | Lyon | CDI |
| OFF-01275 | 6 | Administrateur Bases de Données Lead | Paris | CDI |
| OFF-03145 | 6 | Data Engineer Lead | Montpellier | CDI |
| OFF-03126 | 6 | Administrateur Bases de Données Junior | Lyon | CDI |

La requête Dev Tools correspondante est dans `enquete.txt`.

### 4.5 Public

En considérant iOS et Android comme appareils mobiles, on obtient 8 155 requêtes, soit **39,4 %** du trafic. Les navigateurs les plus utilisés dans les chaînes générées sont Safari (8 249), Chrome (8 114), puis Firefox (4 037). La valeur `zgrab` est identifiée comme robot, pas comme navigateur grand public.

## Partie 5 — Tableau de bord

Dans Lens, créer le tableau de bord « Site de recrutement — trafic » avec les panneaux suivants :

1. Indicateur du nombre de requêtes.
2. Indicateur taux d'erreur serveur : `count(kql='http.response.status_code >= 500') / count()`, format pourcentage.
3. Barres empilées : `@timestamp` par intervalle, ventilé par `http.response.status_code`.
4. Tableau des dix valeurs principales de `labels.offre_id`.
5. Anneau des cinq valeurs principales de `user_agent.name`.
6. Carte utilisant la data view `offres` et le champ géographique `localisation`.

Activer l'interaction croisée puis tester un clic sur le code 503. La capture doit être prise dans Kibana après avoir importé les logs et choisi la plage absolue du TP.


## Vérifications finales du TP2

### Supervision et rejeu

Lors du premier chargement, les pipelines `offres` et `web` tournaient chacun avec 12 workers et un lot de 125 événements. Les compteurs observés étaient :

| Pipeline | in | filtered | out |
| --- | ---: | ---: | ---: |
| offres | 5 000 | 5 000 | 5 000 |
| web | 20 700 | 20 700 | 20 700 |

La sortie Elasticsearch consommait le plus de temps. Lors de cette mesure, elle a duré environ 32,9 s pour `offres` et 98,9 s pour `web`. Le traitement Grok du pipeline `web` a duré environ 24,7 s.

Le rejeu du fichier de logs a fait passer le compteur à 41 400, car `sincedb_path => "/dev/null"` relit le fichier et le data stream ne possède pas d’identifiant stable pour empêcher les doublons. Après suppression du data stream et un seul nouveau chargement, le total final est revenu à **20 700**. Les offres restent à **5 000**, car le pipeline réutilise leur identifiant métier avec `document_id => "%{id}"`.

### Dead letter queue

L’événement `OFF-99999`, lu depuis `/data/offres_test.ndjson`, contenait le champ supplémentaire `prime: 3000`. Elasticsearch l’a rejeté avec le statut HTTP 400 et l’exception `strict_dynamic_mapping_exception`, car le mapping strict de `offres` n’autorise pas ce champ. La DLQ a conservé l’événement et la cause du rejet dans `[@metadata][dead_letter_queue]`. L’index `offres` est resté à 5 000 documents et `OFF-99999` n’y a pas été trouvé.

Pour traiter cet événement, il faut lire la cause, corriger le document ou le mapping selon le besoin métier, puis rejouer l’événement corrigé et vérifier son indexation. Contrairement à `helpers.bulk(..., raise_on_error=False)`, la DLQ conserve l’événement rejeté pour permettre son analyse et sa reprise.

### Vérifications du data stream

Le data stream `logs-web-default` contient **20 700 événements** après le chargement propre et **0 échec Grok**. Son index caché est `.ds-logs-web-default-2026.10.02-000001`, en mode `logsdb`. Le premier événement est daté du `2026-09-22T22:00:39.000Z`, soit le 23 septembre à 00:00:39 avec le fuseau `+0200`. Le champ `http.response.status_code` est de type `long`, ce qui permet les comparaisons numériques et les agrégations.

### Tableau de bord

Le tableau de bord Kibana comporte les six visualisations demandées. Après le chargement propre, il affiche **20 700 requêtes** et un taux d’erreurs serveur de **1,97 %**. Le clic sur le statut 503 a bien filtré le tableau de bord. La capture finale est enregistrée dans `captures/Tableau de bord.png`.