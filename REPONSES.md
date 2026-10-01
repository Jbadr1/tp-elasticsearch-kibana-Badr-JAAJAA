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

Le bloc `should` augmente le score des documents dont les compétences contiennent `Elasticsearch`, sans rendre cette compétence obligatoire. Sans ce bloc, le classement dépend uniquement du texte placé dans `must`. Les critères exacts sont placés dans `filter` car ils ne nécessitent pas de calcul de score et peuvent être mis en cache, ce qui améliore les performances. Dans le filtre d’exemple du fichier de requêtes, le mot `data` est utilisé pour cibler les postes Data Engineer/Data Scientist : le jeu généré ne contient pas le terme `données` dans les titres ou descriptions concernés.

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


