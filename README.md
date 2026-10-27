# 🎧 Moodscape

> A paisagem emocional do seu gosto musical.

O Moodscape conecta na sua conta do Spotify, descobre como soam as músicas que você ouve e desenha um **mapa de humor** do seu gosto musical.

🔗 **Acesse:** _link em breve_ (clique em **Ver demonstração** para usar sem login)

## O que ele faz

- **Login com o Spotify** para ler as suas músicas curtidas e as mais ouvidas.
- **Classifica cada música** em um de 4 humores, a partir de dois números: **felicidade** (*valence*) e **energia** (*energy*).
- **Mapa de humor:** cada música vira um ponto no mapa.
- **Distribuição:** quanto do seu gosto cai em cada humor.
- **Modo demonstração:** 60 músicas sorteadas de uma base pública, para ver o app funcionando sem login.

```
             energia alta
     😠 Tenso    |   😄 Eufórico
  triste --------+-------- feliz
  😢 Melancólico |   😌 Tranquilo
             energia baixa
```

## Como funciona

1. O app busca as músicas da pessoa na **API do Spotify** (login via OAuth).
2. Para cada música, procura a felicidade e a energia no **ReccoBeats**, uma API gratuita.
3. O que o ReccoBeats não conhece é procurado numa **base pública de ~90 mil músicas**, consultada com **SQL** usando **DuckDB**.
4. A função `classificar_humor` coloca cada música num dos 4 quadrantes.

## O que eu descobri

**1. As fontes públicas conhecem pouco a música brasileira de nicho.**
O Spotify deixou de fornecer esses dados para apps novos em 2024, então testei duas fontes alternativas. No meu perfil (gospel e rap nacional), só **~26%** das músicas tinham dados de humor. A solução foi analisar **mais músicas** (curtidas + mais ouvidas, 250+ no total), para que a quantidade com humor encontrado fosse suficiente. O app sempre mostra essa **cobertura**, para deixar claro o quanto dá para confiar no resultado.

**2. O humor mede o som, não o sentimento.**
Os louvores que eu ouço apareceram como "Melancólico". O número de felicidade não mede o que a letra diz nem o que a pessoa sente: ele descreve **como a música soa** (tom, ritmo, brilho). Uma música lenta e suave soa contida, mesmo que, para quem ouve, ela signifique paz.

## Tecnologias

| Tecnologia | Para quê |
|---|---|
| Python | Linguagem principal |
| Streamlit | Transforma o código Python em site |
| Spotipy | Conversa com a API do Spotify |
| ReccoBeats | Felicidade e energia das músicas |
| DuckDB + SQL | Consulta à base pública de músicas |
| Altair | Gráficos |

## Como rodar

### 1. Crie um app no Spotify

1. Entre em <https://developer.spotify.com/dashboard> e clique em **Create app**.
2. Em **Redirect URI**, cadastre o endereço onde o app vai rodar (veja o passo 3).
3. Marque **Web API** e salve.

Em modo de desenvolvimento, o Spotify só deixa entrar as contas cadastradas em **User Management**. Por isso o site público tem o modo demonstração.

### 2. Abra o projeto

O jeito mais fácil é o **GitHub Codespaces**: no GitHub, clique em **Code → Codespaces → Create codespace on main**.
O ambiente já abre com Python e as bibliotecas instaladas.

### 3. Configure as credenciais

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Preencha com os dados do seu app do Spotify. O `redirect_uri` precisa ser **idêntico** ao cadastrado no Spotify:

- no seu computador: `http://127.0.0.1:8501/`
- no Codespaces: o endereço da aba **Ports** para a porta 8501, terminando em `/`

### 4. Rode

```bash
streamlit run app.py
```

Para gerar de novo a base pública e as músicas da demonstração: `python scripts/prepare_dataset.py`.

## Sobre

Projeto feito por **[Je4nms](https://github.com/Je4nms)** enquanto aprendia programação: meu primeiro projeto em Python, SQL e Git.
