"""Gráficos do painel, feitos com Altair (a biblioteca de gráficos que vem com o Streamlit).

O humor de cada música é identificado pela POSIÇÃO no mapa e pelos rótulos
escritos nos quadrantes, e não por cores: 4 cores parecidas num gráfico de
pontos ficariam difíceis de distinguir, principalmente para quem tem daltonismo.
"""

import altair as alt
import pandas as pd

# Cor dos pontos e barras, com uma versão para tema claro e outra para escuro
MARK_COLOR = {"light": "#2a78d6", "dark": "#3987e5"}
SURFACE_COLOR = {"light": "#ffffff", "dark": "#0e1117"}
GUIDE_COLOR = "#8a8a85"

MOODS = ["😄 Eufórico", "😠 Tenso", "😌 Tranquilo", "😢 Melancólico"]

# Onde escrever o nome de cada humor no mapa (felicidade, energia)
QUADRANT_LABELS = pd.DataFrame(
    [
        {"valence": 0.98, "energy": 0.98, "label": "😄 Eufórico", "align": "right"},
        {"valence": 0.02, "energy": 0.98, "label": "😠 Tenso", "align": "left"},
        {"valence": 0.98, "energy": 0.02, "label": "😌 Tranquilo", "align": "right"},
        {"valence": 0.02, "energy": 0.02, "label": "😢 Melancólico", "align": "left"},
    ]
)


def mood_map(tracks: pd.DataFrame, theme: str) -> alt.Chart:
    """Cada música vira um ponto: felicidade no eixo X, energia no eixo Y."""
    axis_scale = alt.Scale(domain=[0, 1], nice=False)
    axis = alt.Axis(tickCount=5, grid=False)

    points = (
        alt.Chart(tracks)
        .mark_circle(size=90, opacity=0.85, stroke=SURFACE_COLOR[theme], strokeWidth=2)
        .encode(
            x=alt.X("valence:Q", title="Felicidade (como a música soa) →", scale=axis_scale, axis=axis),
            y=alt.Y("energy:Q", title="Energia →", scale=axis_scale, axis=axis),
            color=alt.value(MARK_COLOR[theme]),
            tooltip=[
                alt.Tooltip("name:N", title="Música"),
                alt.Tooltip("artists:N", title="Artista"),
                alt.Tooltip("mood:N", title="Humor"),
                alt.Tooltip("valence:Q", title="Felicidade", format=".2f"),
                alt.Tooltip("energy:Q", title="Energia", format=".2f"),
            ],
        )
    )

    # As duas linhas no meio (0.5) que dividem o mapa nos 4 quadrantes
    middle = pd.DataFrame({"value": [0.5]})
    vertical = alt.Chart(middle).mark_rule(color=GUIDE_COLOR, strokeDash=[4, 4]).encode(x="value:Q")
    horizontal = alt.Chart(middle).mark_rule(color=GUIDE_COLOR, strokeDash=[4, 4]).encode(y="value:Q")

    labels = []
    for align in ["left", "right"]:
        side = QUADRANT_LABELS[QUADRANT_LABELS["align"] == align]
        for baseline, rows in [("top", side[side["energy"] > 0.5]), ("bottom", side[side["energy"] < 0.5])]:
            labels.append(
                alt.Chart(rows)
                .mark_text(align=align, baseline=baseline, fontSize=13, fontWeight="bold", color=GUIDE_COLOR)
                .encode(x="valence:Q", y="energy:Q", text="label:N")
            )

    # Os nomes dos quadrantes vêm por último para ficarem por cima dos pontos
    return alt.layer(vertical, horizontal, points, *labels).properties(height=420)


def mood_distribution(tracks: pd.DataFrame, theme: str) -> alt.Chart:
    """Barra com a porcentagem de músicas em cada humor."""
    counts = tracks["mood"].value_counts().reindex(MOODS, fill_value=0)
    summary = pd.DataFrame(
        {"mood": counts.index, "count": counts.values, "share": counts.values / counts.sum()}
    )

    base = alt.Chart(summary).encode(
        y=alt.Y("mood:N", sort=MOODS, title=None),
        x=alt.X(
            "share:Q",
            title=None,
            axis=alt.Axis(format="%", grid=False, tickCount=5),
            scale=alt.Scale(domain=[0, 1]),
        ),
        tooltip=[
            alt.Tooltip("mood:N", title="Humor"),
            alt.Tooltip("count:Q", title="Músicas"),
            alt.Tooltip("share:Q", title="Porcentagem", format=".0%"),
        ],
    )
    bars = base.mark_bar(color=MARK_COLOR[theme], cornerRadiusEnd=4, height=22)
    values = base.mark_text(align="left", dx=6).encode(text=alt.Text("share:Q", format=".0%"))
    return (bars + values).properties(height=180)
