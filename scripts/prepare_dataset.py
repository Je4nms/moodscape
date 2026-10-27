"""Baixa a planilha pública com o humor de ~114 mil músicas e guarda só o que o Moodscape usa.

Gera dois arquivos:
- data/tracks_mood.csv: id, felicidade e energia de todas as músicas (o plano reserva);
- data/demo_tracks.csv: 60 músicas sorteadas, usadas no modo demonstração.

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
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "tracks_mood.csv"
DEMO_PATH = DATA_DIR / "demo_tracks.csv"
DEMO_SIZE = 60


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


def sample_demo(raw_path: Path, output_path: Path, size: int = DEMO_SIZE) -> int:
    """Sorteia músicas para a demonstração.

    Ordenar pelo "hash" do ID embaralha as músicas de um jeito fixo:
    rodar o script de novo sorteia sempre as mesmas.
    """
    output_path.parent.mkdir(exist_ok=True)
    duckdb.sql(f"""
        COPY (
            SELECT
                track_id AS id,
                ANY_VALUE(track_name) AS name,
                replace(ANY_VALUE(artists), ';', ', ') AS artists,
                ANY_VALUE(album_name) AS album,
                ANY_VALUE(valence) AS valence,
                ANY_VALUE(energy) AS energy
            FROM read_csv('{raw_path}')
            GROUP BY track_id
            ORDER BY hash(track_id)
            LIMIT {size}
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
        demo_total = sample_demo(raw_path, DEMO_PATH)

    print(f"Pronto! {total} músicas salvas em {OUTPUT_PATH}")
    print(f"Pronto! {demo_total} músicas de demonstração salvas em {DEMO_PATH}")


if __name__ == "__main__":
    main()
