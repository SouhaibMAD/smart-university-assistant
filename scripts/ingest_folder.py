import argparse
import sys
from pathlib import Path

from app.db.session import SessionLocal
from app.services.ingestion import (
    DuplicateDocumentError,
    ingest_document,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest PDF and TXT documents from a folder."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default="/data/raw",
        help="Folder containing PDF/TXT files (default: /data/raw).",
    )
    args = parser.parse_args()

    folder = Path(args.folder)

    if not folder.is_dir():
        print(f"ERREUR: Dossier introuvable : {folder}")
        return 1

    files = sorted(
        file
        for file in folder.iterdir()
        if file.is_file() and file.suffix.lower() in {".pdf", ".txt"}
    )

    if not files:
        print(f"Aucun fichier PDF/TXT trouvé dans : {folder}")
        return 0

    total_chunks = 0
    success_count = 0
    duplicate_count = 0
    error_count = 0

    db = SessionLocal()

    try:
        for file in files:
            try:
                data = file.read_bytes()

                document = ingest_document(
                    db=db,
                    data=data,
                    filename=file.name,
                    uploaded_by=None,
                )

                total_chunks += document.num_chunks
                success_count += 1

                print(f"OK: {file.name} ({document.num_chunks} chunks)")

            except DuplicateDocumentError as exc:
                duplicate_count += 1
                print(f"DOUBLON: {file.name} ({exc})")

            except Exception as exc:  # noqa: BLE001
                error_count += 1
                print(f"ERREUR: {file.name} ({exc})")

    finally:
        db.close()

    print("\n Résumé")
    print(f"Fichiers trouvés : {len(files)}")
    print(f"Réussis : {success_count}")
    print(f"Doublons : {duplicate_count}")
    print(f"Erreurs : {error_count}")
    print(f"Chunks créés : {total_chunks}")

    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
