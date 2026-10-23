"""Busca a felicidade (valence) e a energia (energy) das músicas no ReccoBeats.

O Spotify parou de fornecer esses dados para apps novos em 2024.
O ReccoBeats é um serviço gratuito que calcula números equivalentes
e aceita o mesmo ID de música do Spotify.
"""

import requests

API_URL = "https://api.reccobeats.com/v1/audio-features"

# Quantos IDs mandamos por pedido, para não fazer um pedido gigante de uma vez
BATCH_SIZE = 40


def get_audio_features(spotify_ids: list[str]) -> dict[str, dict]:
    """Devolve {id_do_spotify: {"valence": ..., "energy": ...}}.

    Músicas que o ReccoBeats não conhece simplesmente não aparecem
    no resultado; quem chama a função decide o que fazer com elas.
    """
    features = {}
    for start in range(0, len(spotify_ids), BATCH_SIZE):
        batch = spotify_ids[start : start + BATCH_SIZE]
        response = requests.get(API_URL, params={"ids": ",".join(batch)}, timeout=15)
        response.raise_for_status()  # se o site responder com erro, para aqui

        for item in response.json()["content"]:
            # O ReccoBeats tem o próprio ID; o do Spotify vem no fim do link "href"
            spotify_id = item["href"].rsplit("/", 1)[-1]
            features[spotify_id] = {"valence": item["valence"], "energy": item["energy"]}
    return features
