import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", page_icon=":control_knobs:")

# =================================================
# Barra lateral
# =================================================

st.sidebar.header('Market Place'.upper())

# imagem do logo 
st.sidebar.image(Image.open('Best_Food2.png'), width=250)

# Descricao da utilizacao da ferramenta

st.markdown("""
### Dashboard para acompanhar as métricas dos entregadores e restaurantes 
#### Como utilizar a ferramenta:

1- Visao Empresa:

    -Visão gerencial, metricas gerais de comportamento;
    -Visão tática, indicadores semanais de crescimento;
    -Visão geográfica, insights de geolocalizacao.

2- Visao Entregador:

    -Acompanhamento semanal do crescimento dos entregadores.
    
3- Visao Restaurante:

    -Indicadortes semanais do crescimento dos restaurantes.
    
##### Ask for help:

    -Time de Data Science no Discord: @carlosfred
""")

