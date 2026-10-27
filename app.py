"""Página principal do Moodscape.

O Streamlit roda este arquivo de cima a baixo toda vez que o usuário
interage com a página (clica num botão, muda uma opção...).
O que precisa sobreviver entre essas execuções fica em `st.session_state`.
"""

import pandas as pd
import requests
import spotipy
import streamlit as st
from spotipy.cache_handler import MemoryCacheHandler

from moodscape import charts, data, features, spotify
from moodscape.mood import classificar_humor

NOT_FOUND = "❔ Não encontrado"

st.set_page_config(page_title="Moodscape", page_icon="🎧")
st.title("🎧 Moodscape")
st.caption("A paisagem emocional do seu gosto musical")


# Guarda o resultado por 1 dia: se a mesma lista de músicas for pedida de novo,
# o Streamlit devolve a resposta salva em vez de chamar o ReccoBeats outra vez.
@st.cache_data(ttl="1d", show_spinner="Buscando o humor das músicas...")
def fetch_audio_features(spotify_ids: tuple[str, ...]) -> dict[str, dict]:
    return features.get_audio_features(list(spotify_ids))


def show_dashboard(tracks: list[dict]) -> None:
    """Desenha o painel. Serve tanto para as músicas do usuário quanto para a demonstração."""
    df = pd.DataFrame(tracks)
    with_mood = df[df["mood"] != NOT_FOUND]

    col_total, col_found = st.columns(2)
    col_total.metric("Músicas analisadas", len(df))
    col_found.metric("Com humor encontrado", f"{len(with_mood)} ({len(with_mood) / len(df):.0%})")
    st.caption(
        "O humor descreve como a música **soa** (melodia, ritmo, energia), "
        "não o sentimento de quem ouve."
    )

    if with_mood.empty:
        st.info("Nenhuma das suas músicas foi encontrada nas fontes de humor.")
        return

    theme = st.context.theme.type or "light"

    st.subheader("Mapa de humor")
    st.altair_chart(charts.mood_map(with_mood, theme), width="stretch")

    st.subheader("Distribuição")
    st.altair_chart(charts.mood_distribution(with_mood, theme), width="stretch")

    st.subheader("Músicas")
    show_all = len(with_mood) < len(df) and st.toggle("Mostrar também as músicas sem humor encontrado")
    st.dataframe(
        df if show_all else with_mood,
        column_order=["cover", "name", "artists", "mood", "album"],
        column_config={
            "cover": st.column_config.ImageColumn(""),
            "name": "Música",
            "artists": "Artista",
            "mood": "Humor",
            "album": "Álbum",
        },
        hide_index=True,
    )


# Modo demonstração: músicas aleatórias da planilha pública, sem precisar de login
demo_tracks = data.load_demo_tracks()
if st.session_state.get("demo"):
    st.info(
        f"**Demonstração** com {len(demo_tracks)} músicas aleatórias de uma base pública. "
        "Com login, o Moodscape analisa as suas músicas do Spotify."
    )
    if st.button("Sair da demonstração"):
        st.session_state.demo = False
        st.rerun()
    for track in demo_tracks:
        track["mood"] = classificar_humor(track["valence"], track["energy"])
    show_dashboard(demo_tracks)
    st.stop()

# Cada visitante ganha o seu próprio "cofre" de token, guardado na sessão dele
if "token_cache" not in st.session_state:
    st.session_state.token_cache = MemoryCacheHandler()

oauth = spotify.create_oauth(
    **st.secrets["spotify"], cache_handler=st.session_state.token_cache
)

# Depois do login, o Spotify devolve o usuário para cá com "?code=..." na URL.
# Trocamos esse código temporário por um token de acesso de verdade.
if "code" in st.query_params:
    oauth.get_access_token(st.query_params["code"], as_dict=False, check_cache=False)
    st.query_params.clear()  # tira o código da URL: ele só vale uma vez
elif "error" in st.query_params:
    st.error("O login com o Spotify foi cancelado ou falhou. Tente de novo.")
    st.query_params.clear()

token = oauth.validate_token(st.session_state.token_cache.get_cached_token())

if not token:
    st.write("Entre com a sua conta do Spotify para ver a paisagem do seu humor musical.")
    col_login, col_demo = st.columns(2)
    col_login.link_button("Entrar com Spotify", oauth.get_authorize_url(), type="primary")
    if demo_tracks and col_demo.button("Ver demonstração"):
        st.session_state.demo = True
        st.rerun()
    st.stop()  # sem login, a página para aqui

client = spotipy.Spotify(auth_manager=oauth)

with st.spinner("Buscando as suas músicas no Spotify..."):
    tracks = spotify.get_library(client)

track_ids = tuple(track["id"] for track in tracks)
try:
    reccobeats_features = fetch_audio_features(track_ids)
except requests.RequestException:
    st.warning("Não foi possível buscar o humor das músicas agora. Tente de novo mais tarde.")
    reccobeats_features = {}

# Plano reserva: a planilha só é consultada para as músicas que o ReccoBeats não conhecia
missing_ids = [track_id for track_id in track_ids if track_id not in reccobeats_features]
dataset_features = data.lookup_audio_features(missing_ids)

for track in tracks:
    track_features = reccobeats_features.get(track["id"]) or dataset_features.get(track["id"])
    if track_features:
        track.update(track_features)
        track["mood"] = classificar_humor(track_features["valence"], track_features["energy"])
    else:
        track["mood"] = NOT_FOUND

show_dashboard(tracks)
st.caption(f"Fontes do humor: ReccoBeats {len(reccobeats_features)} · Planilha {len(dataset_features)}")

if st.button("Sair"):
    st.session_state.token_cache = MemoryCacheHandler()
    st.rerun()
