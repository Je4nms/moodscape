"""Procura a felicidade e a energia das músicas na planilha pública (o plano reserva).

A planilha é gerada por `scripts/prepare_dataset.py` e consultada com SQL pelo DuckDB,
um banco de dados que roda dentro do próprio app, sem servidor.
"""

from pathlib import Path

import duckdb

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tracks_mood.csv"


def lookup_audio_features(spotify_ids: list[str]) -> dict[str, dict]:
    """Devolve {id_do_spotify: {"valence": ..., "energy": ...}} das músicas que estão na planilha."""
    if not DATA_PATH.exists():
        return {}

    # O "?" é preenchido pelo DuckDB com a lista de IDs, de forma segura
    rows = duckdb.execute(
        f"""
        SELECT track_id, valence, energy
        FROM read_csv('{DATA_PATH}')
        WHERE list_contains(?, track_id)
        """,
        [spotify_ids],
    ).fetchall()
    return {track_id: {"valence": valence, "energy": energy} for track_id, valence, energy in rows}
