# ******************* COMPLETO FINAL

# Bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from datetime import datetime
from geopy.distance import geodesic
from PIL import Image
#from Visao_empresa.py import df

st.set_page_config(page_title="Visao Entregadores", page_icon=":racing_motorcycle:")

#=====================================
# Carregando df e renomeando colunas
#=====================================

df = pd.read_csv('train.csv')
df.rename({'Delivery_person_ID':'Delivery_ID', 'Delivery_person_Age':'Delivery_Age', 
           'Delivery_person_Ratings':'Delivery_Ratings', 'Restaurant_latitude':'Rest_lat', 
           'Restaurant_longitude':'Rest_lon','Delivery_location_latitude':'Delivery_lat', 
           'Delivery_location_longitude':'Delivery_lon','Weatherconditions':'Weather', 
           'Road_traffic_density':'Traffic_density','Type_of_order':'Type_order', 
           'Type_of_vehicle':'Type_vehicle', 'multiple_deliveries':'mult_deliveries',
               'Time_taken(min)':'Time_taken_min'}, axis=1, inplace=True)

# Tirando espacos dos nomes dos elementos das colunas

for nome in df.columns:
    if df[nome].dtype == 'object':
        df[nome] = df[nome].str.strip()

# Remover NaNs

for nome in df.columns:
    df = df.loc[(df[nome] != 'NaN') & (df[nome] != 'nan')]
    
# Corrigindo o tipo das colunas de acordo com o elemento nela

df['Delivery_Age'] = df['Delivery_Age'].astype('int32')
df['Delivery_Ratings'] = df['Delivery_Ratings'].astype('float32')
df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')
df['Time_Orderd'] = df['Time_Orderd'].apply(lambda x: datetime.strptime(x, '%H:%M:%S').time())
df['Time_Order_picked'] = df['Time_Order_picked'].apply(lambda x: datetime.strptime(x, '%H:%M:%S').time())
df['Vehicle_condition'] = df['Vehicle_condition'].astype('str')
df['mult_deliveries'] = df['mult_deliveries'].astype('int16')
df['Time_taken_min'] = (df['Time_taken_min'].str.replace('\\(min\\) ', '')).astype('int16')
df['Weather'] = df['Weather'].str.replace('conditions ', '')

#=====================================
# Funcoes
#=====================================

# Calcula as metricas
def calc_metricas (data, cols, op):
    """
    data = data frame;
    cols = lista colunas (string);
    op = operacao;
    resultado sera um float
    """
    if op == 'max':
        return(data[cols].max())
    elif op == 'min':
        return(data[cols].min())
    else:
        return(data[cols].mean())

# Calcula avg e std de subdf agrupado retornando st.dataframe formatado
def calc_avg_std (data, groupcol, aggcol):
    """
    Funcao calcula avg e std de subdf agrupado.
    input: df, coluna a ser agrupada(groupby), colunas a serem calculadas(agg)
    output: df com media e std
    """
    ret = data.groupby(groupcol).agg({aggcol:['mean', 'std']})
    ret.columns = ['mean', 'std']
    ret.reset_index()
    st.dataframe(ret, use_container_width=True)    

    # entregador mais lento e mais rapido retornando st.dataframe formatado
def calc_desemp_entrega(ascen):
    """
    Funcao faz subset do df em relacao ao desempenho do entregado
    input: ascendente para comecar pelo pior e desc (True/False)
    output: df
    """
    df_des = (df[['Delivery_ID', 'Time_taken_min', 'City']].groupby(['Delivery_ID', 'City']).mean().
              sort_values(['City', 'Time_taken_min'],ascending=ascen).reset_index())
    
    df_loop = [df_des.loc[df_des['City'] == i].head(3) for i in df_des['City'].unique()]
    if not df_loop:
        raise ValueError("Não há dados a serem concatenados.") # mensagem erro caso data zero no slider
    st.dataframe(pd.concat(df_loop).set_index('Delivery_ID'), use_container_width=True)    


# =================================================
# Barra lateral
# =================================================

# imagem do logo 
st.sidebar.image(Image.open('Best_Food2.png'), width=250)
st.sidebar.markdown('## Controle')

# Botao deslizador seleciona a data
date_slider = st.sidebar.slider(
                                'Selecione a data',
                                value=pd.datetime(2022,4,13),
                                min_value=pd.datetime(2022,2,11),
                                max_value=pd.datetime(2022,4,6),
                                format='DD-MM-YYYY'
                                )

# Controlando o slider vinculando ao Botao deslizador seleciona a data
df = df.loc[df['Order_Date'] < date_slider] #df.query("Order_Date < date_slider")

st.sidebar.markdown("""___""")

# Menu Botao selecao trafeco
traffic_options = st.sidebar.multiselect(
                        'Condicoes de transito',
                        df['Traffic_density'].unique(),
                        default=df['Traffic_density'].unique()
                        )
# Controlando o Botao seletor condicao de trafeco
df = df.loc[df['Traffic_density'].isin(traffic_options)]

st.sidebar.markdown("""___""")

# Menu Botao selecao clima
clima_options = st.sidebar.multiselect(
                        'Condicoes clima',
                        df['Weather'].unique(),
                        default=df['Weather'].unique()
                        )
# Controlando o Botao seletor condicao de trafeco
df = df.loc[df['Weather'].isin(clima_options)]

st.sidebar.markdown("""___""")
st.sidebar.markdown('##### Powered By FREDAO:nerd_face:')

# =================================================
# Layout
# =================================================

# Criando containers medidas individuais
with st.container():
    st.subheader('Overall Metrics')
    
    colmi1, colmi2, colmi3, colmi4 = st.columns(4)

    with colmi1:
                # Chamando funcao metricas
        st.metric(label="Maior idade", value=f"{calc_metricas(df,'Delivery_Age', 'max')}")

    with colmi2:
                # Chamando funcao metricas
        st.metric(label="Menor idade", value=f"{calc_metricas(df,'Delivery_Age', 'min')}")

    with colmi3:
                # Chamando funcao metricas
        st.metric(label="Melhor veículo", value=f"{calc_metricas(df,'Vehicle_condition', 'max')}")

    with colmi4:
                # Chamando funcao metricas
        st.metric(label="Pior veículo", value=f"{calc_metricas(df,'Vehicle_condition', 'min')}")


st.markdown("""___""")
        
# Criando containers avaliacoes medias por entregador
with st.container():
    st.subheader('Avaliacoes')
    
    colme1, colme2= st.columns(2)

    with colme1:
        st.markdown("##### Avaliacão media por entregador")
        df_mrat = df[['Delivery_ID', 'Delivery_Ratings']].groupby('Delivery_ID').mean().sort_values(by='Delivery_Ratings', ascending=False).reset_index()
        df_mrat.columns = ['Entregador ID', 'media']
        st.dataframe(df_mrat.set_index('Entregador ID'), use_container_width=True)

    with colme2:
        st.markdown("##### Avaliacão por transito")
        # Chamando funcao
        calc_avg_std (df[['Traffic_density', 'Delivery_Ratings']], 'Traffic_density', 'Delivery_Ratings')
        
        st.markdown("##### Avaliacão por clima")
        # Chamando funcao
        calc_avg_std (df[['Weather', 'Delivery_Ratings']], 'Weather', 'Delivery_Ratings')
        
st.markdown("""___""")
        
# Criando containers top
with st.container():
    
    coltop1, coltop2 = st.columns(2)

    with coltop1:
        st.markdown("##### Entregadores mais rápidos por City")
                        # Chamando funcao
        calc_desemp_entrega(True)

        
    with coltop2:
        st.markdown("##### Entregadores mais lentos por City")
                        # Chamando funcao
        calc_desemp_entrega(False)



        