"""Baixa a planilha pública com o humor de ~114 mil músicas e guarda só o que o Moodscape usa.

Rode uma vez, de dentro da pasta do projeto:

    python scripts/prepare_dataset.py

Fonte: https://huggingface.co/datasets/maharshipandya/spotify-tracks-dataset
"""

import tempfile
from pathlib import Path

import duckdb
import requests

SOURCE_URL = (
    "https://huggingface.co/datasets/maharshipandya/"
    "spotify-tracks-dataset/resolve/main/dataset.csv"
)
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "tracks_mood.csv"


def slim_dataset(raw_path: Path, output_path: Path) -> int:
    """Guarda só id, felicidade e energia, com uma linha por música.

    A planilha original repete a mesma música uma vez para cada gênero
    em que ela aparece; o GROUP BY junta as repetidas numa linha só.
    """
    output_path.parent.mkdir(exist_ok=True)
    duckdb.sql(f"""
        COPY (
            SELECT track_id, ANY_VALUE(valence) AS valence, ANY_VALUE(energy) AS energy
            FROM read_csv('{raw_path}')
            GROUP BY track_id
            ORDER BY track_id
        ) TO '{output_path}' (HEADER)
    """)
    return duckdb.sql(f"SELECT COUNT(*) FROM read_csv('{output_path}')").fetchall()[0][0]


def main() -> None:
    print("Baixando a planilha (~20 MB)...")
    response = requests.get(SOURCE_URL, timeout=120)
    response.raise_for_status()

    with tempfile.TemporaryDirectory() as tmp:
        raw_path = Path(tmp) / "dataset.csv"
        raw_path.write_bytes(response.content)
        total = slim_dataset(raw_path, OUTPUT_PATH)

    print(f"Pronto! {total} músicas salvas em {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
