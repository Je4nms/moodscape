"""Tudo que conversa com a API do Spotify: login (OAuth) e busca de músicas.

Usamos a biblioteca `spotipy`, que já sabe falar com a API do Spotify,
para não termos que montar cada requisição HTTP na mão.
"""

import spotipy
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth

# Permissões que pedimos ao usuário na tela de login do Spotify.
# Pedimos só o que usamos agora ("princípio do menor privilégio");
# novas permissões entram quando uma funcionalidade precisar delas.
SCOPES = "user-top-read"

# Períodos que o Spotify aceita para "mais ouvidas"
TIME_RANGES = {
    "Últimas 4 semanas": "short_term",
    "Últimos 6 meses": "medium_term",
    "Último ano": "long_term",
}


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


def get_top_tracks(
    client: spotipy.Spotify, time_range: str = "medium_term", limit: int = 20
) -> list[dict]:
    """Busca as músicas mais ouvidas do usuário.

    A resposta do Spotify é enorme; aqui guardamos só os campos que usamos.
    """
    response = client.current_user_top_tracks(limit=limit, time_range=time_range)
    return [
        {
            "id": track["id"],
            "name": track["name"],
            "artists": ", ".join(artist["name"] for artist in track["artists"]),
            "album": track["album"]["name"],
            "cover": track["album"]["images"][-1]["url"] if track["album"]["images"] else None,
        }
        for track in response["items"]
    ]
