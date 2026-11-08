"""Script d'évaluation du RAG.

Périmètre : Houda (feature/eval-tests).

Usage visé :
    docker compose exec backend python -m evaluation.run_eval --chunk-size 1000 --top-k 5

Sorties attendues dans evaluation/results/ :
    - results_<config>.csv   (une ligne par question)
    - summary.csv            (une ligne par configuration)
    - summary.json
    - graphiques .png
"""


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
