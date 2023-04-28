# ****************************************** COMPLETO FINAL


# Bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from datetime import datetime
#from ydata_profiling import ProfileReport
from geopy.distance import geodesic
from PIL import Image
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Visao Empresa", page_icon=":house:")

#=====================================
# Funcoes
#=====================================

# metricas
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
    

#=====================================
# Carregando df
#=====================================


# Carregando df e renomeando colunas

df = pd.read_csv('train.csv')
df.rename({'Delivery_person_ID':'Delivery_ID', 'Delivery_person_Age':'Delivery_Age', 'Delivery_person_Ratings':'Delivery_Ratings', 
           'Restaurant_latitude':'Rest_lat', 'Restaurant_longitude':'Rest_lon','Delivery_location_latitude':'Delivery_lat',
           'Delivery_location_longitude':'Delivery_lon','Weatherconditions':'Weather', 'Road_traffic_density':'Traffic_density', 
           'Type_of_order':'Type_order', 'Type_of_vehicle':'Type_vehicle', 'multiple_deliveries':'mult_deliveries', 
            'Time_taken(min)':'Time_taken_min'}, axis=1, inplace=True)

# Tirando espacos dos nomes dos elementos das colunas e Remover NaNs

for nome in df.columns:
    if df[nome].dtype == 'object':
        df[nome] = df[nome].str.strip()
    df = df.loc[(df[nome] != 'NaN') & (df[nome] != 'nan')]

# Corrigindo o tipo de cada coluna de acordo com os respectivos elementos e limpando

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

st.sidebar.header('Market Place'.upper())

# imagem do logo 
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

tab_empresa, tab_tatica, tab_geo = st.tabs(['Visão Empresa', 'Visão Tática', 'Visão Geo'])

#--------------------------------------tabe empresa

with tab_empresa:
    with st.container():
        
        st.markdown("#### Pedidos por Dia")

        df_dia = df[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
        df_dia.columns = ['Order_Date', 'Pedidos']
        fig_dia = px.bar(df_dia, x='Order_Date', y='Pedidos', title='PEDIDOS POR DIA')
        st.plotly_chart(fig_dia, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Pedidos por Tipo de Trefago')
            dfaux_entr_traf = df[['ID', 'Traffic_density']].groupby('Traffic_density').count().reset_index()
            fig_entr_traf = px.pie(dfaux_entr_traf, values='ID', names='Traffic_density', hole=0.5)
            st.plotly_chart(fig_entr_traf, use_container_width=True)

        with col2:
            st.markdown('#### Pedido por Cidade e Tipo de Trafego')
            df_cidade_traf = (df[['City', 'Traffic_density', 'ID']].groupby(['City', 'Traffic_density']).count().
                              reset_index())
            fig_city_traf = px.scatter(df_cidade_traf, x='City', y='Traffic_density', size='ID', color='City',
                                       labels={'Traffic_density':'Tipo de Trafego'})
            st.plotly_chart(fig_city_traf, use_container_width=True)


with tab_tatica:
    with st.container():
        st.markdown("#### Pedidos por Semana")

    # Criando coluna Semana
        df['Semana'] = df['Order_Date'].dt.isocalendar().week

    # Agrupando contando ID por Semana do maior para o menor
        df_ped_semana_g = df[['ID', 'Semana']].groupby('Semana').count().reset_index()

    # Renomeando colunas
        df_ped_semana_g.columns = ['Semana', 'Pedidos']
        st.dataframe(df_ped_semana_g.set_index('Semana'), use_container_width=True)

    # Plotando linha e barras
        fig2 = px.line(df_ped_semana_g, x='Semana', y='Pedidos', markers=True)
        fig2.add_bar(x=df_ped_semana_g['Semana'], y=df_ped_semana_g['Pedidos'])
        fig2.update_layout(showlegend=False)
        st.plotly_chart(figure_or_data=fig2, use_container_width=True)

    with st.container():
        # qde de pedidos por semana / qde de entregadores por semana

        # Criando df auxiliar qde de pedidos por semana
        df_ID_week = df[['ID', 'Semana']].groupby('Semana').count().reset_index()

        # Criando df auxiliar qde de entregadores por semana
        df_person_week = df[['Delivery_ID', 'Semana']].groupby('Semana').nunique().reset_index()

        # Juntando os df de agrupamento
        df_merge_week = pd.merge(df_person_week, df_ID_week, how='inner')

        # Calculo qde de pedidos por semana / qde de entregadores por semana
        df_merge_week['order_b_deliver'] = (df_merge_week['ID']/df_merge_week['Delivery_ID'])

        # Coluna de media de order_b_deliver
        df_merge_week['average'] = df_merge_week['order_b_deliver'].mean()
        
        st.markdown('#### Pedidos e Media de Pedidos por Entregador por Semana')

        st.dataframe(df_merge_week.set_index('Semana'), use_container_width=True)

        # Plotando
        fig_entrega_semana = go.Figure()
        fig_entrega_semana.add_trace(go.Bar(x=df_merge_week['Semana'], y=df_merge_week['order_b_deliver'], hovertemplate='Valor: %{y}'))
        fig_entrega_semana.add_trace(go.Line(x=df_merge_week['Semana'], y=df_merge_week['average'], hovertemplate='Media: %{y}'))
        fig_entrega_semana.update_layout(showlegend=False)
        #fig_entrega_semana.show()
        st.plotly_chart(fig_entrega_semana, use_container_width=True)

with tab_geo:
    st.markdown('#### Localizacao dos Restaurantes')

    #      MAPA

    # Criando lista das colunas desejadas
    # Agrupando pela MEDIANA

    df_local = df.query("(City != 'NaN') & (Traffic_density != 'NaN')")[['Delivery_lat','Delivery_lon','Traffic_density', 'City']].groupby(['City', 'Traffic_density'])\
    .median().reset_index()

    #display(df_local)

    # Criando instancia de folium
    map = folium.Map()

    # Fazendo for com zip das colunas a serem usadas
    for i, j, l in zip(df_local['Delivery_lat'], df_local['Delivery_lon'], df_local['Traffic_density']):
        if l == 'High':
            cores = 'red'
        elif  l == 'Jam':
            cores = 'orange'
        else:
            cores = 'blue'
        folium.Marker(location=[i, j], popup=f'location=[{i}, {j}], Density={l}', icon=folium.Icon(color=cores, icon='info-sign')).add_to(map)

    folium_static(map, width=800, height=600)


