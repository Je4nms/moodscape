# 🎧 Moodscape

> A paisagem emocional do seu gosto musical.

O Moodscape conecta na sua conta do Spotify, analisa o humor das músicas que você mais ouve e:

- mostra um **painel** com o seu humor musical (feliz, melancólico, tenso, tranquilo);
- **gera playlists** a partir do humor que você escolher.

🚧 **Em construção.** Status atual: login com Spotify e lista das músicas mais ouvidas.

## Tecnologias

| Tecnologia | Para quê |
|---|---|
| Python | Linguagem principal |
| Streamlit | Transforma o código Python em site |
| Spotipy | Conversa com a API do Spotify |

## Como rodar

### 1. Crie um app no Spotify

1. Entre em <https://developer.spotify.com/dashboard> e clique em **Create app**.
2. Em **Redirect URI**, cadastre o endereço onde o app vai rodar (veja o passo 3).
3. Marque **Web API** e salve.

### 2. Abra o projeto

O jeito mais fácil é o **GitHub Codespaces**: no GitHub, clique em **Code → Codespaces → Create codespace on main**.
O ambiente já abre com Python e as bibliotecas instaladas.

### 3. Configure as credenciais

Copie o arquivo de exemplo e preencha com os dados do seu app do Spotify:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

O `redirect_uri` precisa ser **idêntico** ao cadastrado no Spotify:

- rodando no seu computador: `http://127.0.0.1:8501/`
- rodando no Codespaces: o endereço da aba **Ports** para a porta 8501, terminando em `/`
  (algo como `https://seu-codespace-8501.app.github.dev/`)

### 4. Rode

```bash
streamlit run app.py
```
