"""Tudo que conversa com a API do Spotify: login (OAuth) e busca de músicas.

Usamos a biblioteca `spotipy`, que já sabe falar com a API do Spotify,
para não termos que montar cada requisição HTTP na mão.
"""

import spotipy
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

# Permissões que pedimos ao usuário na tela de login do Spotify.
# Pedimos só o que usamos ("princípio do menor privilégio"):
# as mais ouvidas e as músicas curtidas.
SCOPES = "user-top-read user-library-read"

# Períodos que o Spotify aceita para "mais ouvidas"
TIME_RANGES = ["short_term", "medium_term", "long_term"]

# Limite de músicas curtidas que buscamos (o Spotify entrega 50 por vez)
MAX_SAVED_TRACKS = 500


def create_oauth(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    cache_handler: CacheHandler,
) -> SpotifyOAuth:
    """Cria o objeto que cuida do login com o Spotify.

    O `cache_handler` é onde o token de acesso fica guardado. Cada visitante
    do site recebe o seu próprio, para que o login de uma pessoa nunca
    seja usado por outra.
    """
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPES,
        cache_handler=cache_handler,
        open_browser=False,
    )


def _parse_track(track: dict | None) -> dict | None:
    """Guarda só os campos que usamos. Arquivos locais (sem ID) são ignorados."""
    if not track or not track.get("id"):
        return None
    images = track["album"]["images"]
    return {
        "id": track["id"],
        "name": track["name"],
        "artists": ", ".join(artist["name"] for artist in track["artists"]),
        "album": track["album"]["name"],
        "cover": images[-1]["url"] if images else None,
    }


def get_library(client: spotipy.Spotify) -> list[dict]:
    """Junta as mais ouvidas (nos 3 períodos) com as músicas curtidas, sem repetir.

    Quanto mais músicas analisamos, mais músicas com humor encontrado
    conseguimos mostrar.
    """
    raw_tracks = []
    for time_range in TIME_RANGES:
        raw_tracks += client.current_user_top_tracks(limit=50, time_range=time_range)["items"]

    for offset in range(0, MAX_SAVED_TRACKS, 50):
        page = client.current_user_saved_tracks(limit=50, offset=offset)
        raw_tracks += [item["track"] for item in page["items"]]
        if not page["next"]:  # acabaram as curtidas
            break

    library = {}
    for raw_track in raw_tracks:
        track = _parse_track(raw_track)
        if track and track["id"] not in library:
            library[track["id"]] = track
    return list(library.values())
