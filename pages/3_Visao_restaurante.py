# ****************************** FINAL OK


# Carregando bibliotecas

import pandas as pd
import plotly.express as px
from datetime import datetime
from geopy.distance import geodesic
from PIL import Image
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Visao Restaurantes", page_icon=":knife_fork_plate:")


# Carregando e renomeando colunas

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

# =================================================
# Barra lateral
# =================================================

# Imagem logo

st.sidebar.image(Image.open('Best_Food2.png'), width=250)

#st.sidebar.markdown('### Controle')

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
                        ['Low', 'Medium', 'High', 'Jam'],
                        default=['Low', 'Medium', 'High', 'Jam']
                        )
# Controlando o Botao seletor condicao de trafeco
df = df.loc[df['Traffic_density'].isin(traffic_options)]

st.sidebar.markdown("""___""")
st.sidebar.markdown('##### Powered By FREDAO:nerd_face:')
st.sidebar.markdown("""___""")

# =================================================
# Layout
# =================================================

with st.container():
    st.markdown('#### Overal Metrics')
    coleu, coldm, coltef = st.columns(3)
    with coleu:
        #st.markdown('##### Entregadores unicos')
        st.metric(label='Entreg_Únicos', value=f"{df['Delivery_ID'].nunique():,d}")

    with coldm:
        #st.markdown('##### Distancia media')
        coord1 = [(lat, lon) for lat, lon in zip(df['Rest_lat'], df['Rest_lon'])]
        coord2 = [(lat, lon) for lat, lon in zip(df['Delivery_lat'], df['Delivery_lon'])]
        distancia = [geodesic(m, n).km for m, n in zip(coord1, coord2)]
        st.metric(label='Distância média', value=f'{sum(distancia)/len(distancia):,.0f} Km')

    with coltef:
        st.metric(label='T Medio Festival' , 
                  value=round(df.query('Festival == "Yes"')['Time_taken_min'].mean(),0))

with st.container():
    colstdf, colte, colstd = st.columns(3)

    with colstdf:
        st.metric(label='STD Festival' , 
                  value=round(df.query('Festival == "Yes"')['Time_taken_min'].std(),0))

    with colte:
        st.metric(label='Tempo médio' , 
                  value=round(df.query('Festival != "Yes"')['Time_taken_min'].mean(),0))

    with colstd:
        st.metric(label='Tempo STD' , value=round(df.query('Festival != "Yes"')['Time_taken_min'].std(),0))
        
st.markdown("""___""")

with st.container():
    st.markdown('##### Distância Média por Cidade')
    coord1 = [(lat, lon) for lat, lon in zip(df['Rest_lat'], df['Rest_lon'])]
    coord2 = [(lat, lon) for lat, lon in zip(df['Delivery_lat'], df['Delivery_lon'])]
    df['distancia'] = [geodesic(m, n).km for m, n in zip(coord1, coord2)]
    df_dist = df[['City', 'distancia']].groupby('City').mean().reset_index()
    fig_dist=go.Figure(data=[go.Pie(labels=df_dist['City'], values=df_dist['distancia'], pull=[0,0.1,0]) ] )
    st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("""___""")

with st.container():
    colgrafcid, colentr = st.columns(2)
    with colgrafcid:
        st.markdown('##### Tempo Médio por Cidade')
        st.dataframe(df[['City', 'Time_taken_min']].groupby('City').mean(), use_container_width=True)
        
    with colentr:
        st.markdown(' ##### Tempo Médio por Tipo de Entrega')
        # grafico com media e std
        df_tc = df[['City', 'Time_taken_min']].groupby('City').agg({'Time_taken_min':['mean', 'std']})
        df_tc.columns = ['tempo_avg', 'tempo_std']
        df_tc = df_tc.reset_index()
        fig_tc = go.Figure()
        fig_tc.add_trace( go.Bar(name='Control', x=df_tc['City'], y=df_tc['tempo_avg'], error_y=dict(type='data', array=df_tc['tempo_std']) ) )
        fig_tc.update_layout(barmode='group')
        st.plotly_chart(fig_tc, use_container_width=True)
    

st.markdown("""___""")

with st.container():
    st.markdown('##### Tempo médio por cidade e tipo de trafego')


    dfaux_wet1 = df[['City', 'Traffic_density', 'Time_taken_min']].groupby(['City', 'Traffic_density']).agg({'Time_taken_min':['mean', 'std']})
    dfaux_wet1.columns = ['avg_time', 'std_time']
    dfaux_wet1 = dfaux_wet1.reset_index()

    fig_sun1 = (px.sunburst(dfaux_wet1, path=['City', 'Traffic_density'], values='avg_time', color='std_time',color_continuous_scale='RdBu', 
                            color_continuous_midpoint=np.average(dfaux_wet1['std_time'])))
    st.plotly_chart(fig_sun1, use_container_width=True)
        
    
with st.container():
    st.markdown('##### Tempo médio por cidade e tipo de pedido')


    dfaux_wet1 = df[['City', 'Type_order', 'Time_taken_min']].groupby(['City', 'Type_order']).agg({'Time_taken_min':['mean', 'std']})
    dfaux_wet1.columns = ['avg_time', 'std_time']
    dfaux_wet1 = dfaux_wet1.reset_index()
    st.dataframe(dfaux_wet1, use_container_width=True)
 