"""Página principal do Moodscape.

O Streamlit roda este arquivo de cima a baixo toda vez que o usuário
interage com a página (clica num botão, muda uma opção...).
O que precisa sobreviver entre essas execuções fica em `st.session_state`.
"""

import spotipy
import streamlit as st
from spotipy.cache_handler import MemoryCacheHandler

from moodscape import spotify

st.set_page_config(page_title="Moodscape", page_icon="🎧")
st.title("🎧 Moodscape")
st.caption("A paisagem emocional do seu gosto musical")

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
    st.link_button("Entrar com Spotify", oauth.get_authorize_url(), type="primary")
    st.stop()  # sem login, a página para aqui

client = spotipy.Spotify(auth_manager=oauth)

period = st.segmented_control(
    "Período", options=list(spotify.TIME_RANGES), default="Últimos 6 meses"
)
tracks = spotify.get_top_tracks(client, time_range=spotify.TIME_RANGES[period or "Últimos 6 meses"])

st.subheader("Suas músicas mais ouvidas")
st.dataframe(
    tracks,
    column_order=["cover", "name", "artists", "album"],
    column_config={
        "cover": st.column_config.ImageColumn(""),
        "name": "Música",
        "artists": "Artista",
        "album": "Álbum",
    },
    hide_index=True,
)

if st.button("Sair"):
    st.session_state.token_cache = MemoryCacheHandler()
    st.rerun()
