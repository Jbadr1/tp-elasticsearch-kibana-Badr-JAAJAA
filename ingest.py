"""Crée l'index offres avec un mapping strict puis ingère le fichier NDJSON."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from pathlib import Path

from elasticsearch import helpers

from es_client import INDEX, get_client

SETTINGS = {"number_of_shards": 1, "number_of_replicas": 0}

MAPPINGS = {
    "dynamic": "strict",
    "properties": {
        "id": {"type": "keyword"},
        "titre": {
            "type": "text",
            "analyzer": "french",
            "fields": {"brut": {"type": "keyword"}},
        },
        "entreprise": {"type": "keyword"},
        "description": {"type": "text", "analyzer": "french"},
        "competences": {
            "type": "keyword",
            "fields": {"texte": {"type": "text", "analyzer": "french"}},
        },
        "ville": {"type": "keyword"},
        "localisation": {"type": "geo_point"},
        "contrat": {"type": "keyword"},
        "teletravail": {"type": "keyword"},
        "experience_annees": {"type": "integer"},
        "salaire_min": {"type": "integer"},
        "salaire_max": {"type": "integer"},
        "date_publication": {"type": "date"},
    },
}


def lire_actions(fichier: Path) -> Iterator[dict]:
    """Produit une action bulk par ligne sans charger tout le fichier en mémoire."""
    with fichier.open("r", encoding="utf-8") as flux:
        for numero, ligne in enumerate(flux, start=1):
            ligne = ligne.strip()
            if not ligne:
                continue

            document = json.loads(ligne)
            if "id" not in document:
                raise ValueError(f"Champ 'id' absent à la ligne {numero} de {fichier}")

            yield {"_index": INDEX, "_id": document["id"], "_source": document}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fichier", type=Path, default=Path("data/offres.ndjson"))
    parser.add_argument("--reset", action="store_true", help="supprime puis recrée l'index")
    args = parser.parse_args()

    es = get_client()
    print("Cluster :", es.info()["version"]["number"])

    if args.reset:
        es.indices.delete(index=INDEX, ignore_unavailable=True)
        print(f"Ancien index '{INDEX}' supprimé")

    if not es.indices.exists(index=INDEX):
        es.indices.create(index=INDEX, settings=SETTINGS, mappings=MAPPINGS)
        print(f"Index '{INDEX}' créé")

    nombre_reussites, erreurs = helpers.bulk(
        es,
        lire_actions(args.fichier),
        chunk_size=1000,
        raise_on_error=False,
    )
    print(f"{nombre_reussites} documents indexés")
    print(f"{len(erreurs)} erreur(s)")
    for erreur in erreurs:
        print(json.dumps(erreur, ensure_ascii=False, indent=2))

    es.indices.refresh(index=INDEX)
    nombre_documents = es.count(index=INDEX)["count"]
    print(f"{nombre_documents} documents dans '{INDEX}'")


if __name__ == "__main__":
    main()
