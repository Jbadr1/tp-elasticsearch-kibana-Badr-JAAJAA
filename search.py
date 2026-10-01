"""Mini-défi : moteur de recherche d'offres en ligne de commande."""

from __future__ import annotations

import argparse

from es_client import INDEX, get_client


def construire_requete(args: argparse.Namespace) -> dict:
    filtres: list[dict] = []

    if args.ville:
        filtres.append({"term": {"ville": args.ville}})
    if args.contrat:
        filtres.append({"term": {"contrat": args.contrat}})
    if args.teletravail:
        filtres.append({"term": {"teletravail": args.teletravail}})
    if args.salaire_min is not None:
        filtres.append({"range": {"salaire_max": {"gte": args.salaire_min}}})
    if args.autour:
        try:
            latitude, longitude = (float(valeur.strip()) for valeur in args.autour.split(",", 1))
        except (ValueError, AttributeError) as exc:
            raise ValueError("--autour doit respecter le format lat,lon") from exc

        filtres.append(
            {
                "geo_distance": {
                    "distance": args.rayon,
                    "localisation": {"lat": latitude, "lon": longitude},
                }
            }
        )

    return {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": args.texte,
                        "fields": ["titre^3", "competences.texte^2", "description"],
                        "fuzziness": "AUTO",
                    }
                }
            ],
            "filter": filtres,
        }
    }


def afficher_facette(nom: str, agregations: dict) -> None:
    print(f"\n{nom} :")
    for bucket in agregations["buckets"]:
        print(f"  {bucket['key']} : {bucket['doc_count']}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("texte")
    p.add_argument("--ville")
    p.add_argument("--contrat", choices=["CDI", "CDD", "Alternance", "Freelance", "Stage"])
    p.add_argument("--teletravail", choices=["aucun", "partiel", "total"])
    p.add_argument("--salaire-min", type=int)
    p.add_argument("--autour", help="lat,lon")
    p.add_argument("--rayon", default="30km")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--taille", type=int, default=10)
    args = p.parse_args()

    if args.page < 1 or args.taille < 1:
        p.error("--page et --taille doivent être supérieurs ou égaux à 1")

    try:
        requete = construire_requete(args)
    except ValueError as exc:
        p.error(str(exc))

    es = get_client()
    debut = (args.page - 1) * args.taille

    resultat = es.search(
        index=INDEX,
        query=requete,
        from_=debut,
        size=args.taille,
        track_total_hits=True,
        highlight={"fields": {"description": {}}},
        aggs={
            "villes": {"terms": {"field": "ville", "size": 10}},
            "contrats": {"terms": {"field": "contrat", "size": 5}},
            "competences": {"terms": {"field": "competences", "size": 10}},
        },
    )

    total = resultat["hits"]["total"]["value"]
    print(f"\n{total} offre(s) trouvée(s) - page {args.page}\n")

    for numero, hit in enumerate(resultat["hits"]["hits"], start=debut + 1):
        offre = hit["_source"]
        salaire_min = offre.get("salaire_min")
        salaire_max = offre.get("salaire_max")
        salaire = (
            f"{salaire_min} à {salaire_max} euros"
            if salaire_min is not None and salaire_max is not None
            else "non communiqué"
        )
        extrait = " … ".join(
            hit.get("highlight", {}).get("description", [offre.get("description", "")])
        )

        print(f"{numero}. {offre['titre']} - score {hit['_score']:.2f}")
        print(f"   {offre['entreprise']} | {offre['ville']} | {offre['contrat']} | {salaire}")
        print(f"   {extrait}\n")

    aggregations = resultat["aggregations"]
    afficher_facette("Villes", aggregations["villes"])
    afficher_facette("Contrats", aggregations["contrats"])
    afficher_facette("Compétences", aggregations["competences"])


if __name__ == "__main__":
    main()
