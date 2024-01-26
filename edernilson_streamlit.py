import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import streamlit as st

import plotly.express as px

dfIBYTE=pd.read_csv('RECLAMEAQUI_IBYTE.csv')
dfHAPVIDA=pd.read_csv('RECLAMEAQUI_HAPVIDA.csv')
dfNAGEM=pd.read_csv('RECLAMEAQUI_NAGEM.csv')

dfIBYTE['EMPRESA'] = 'IBYTE'
dfHAPVIDA['EMPRESA'] = 'HAPVIDA'
dfNAGEM['EMPRESA'] = 'NAGEM'

df = pd.concat([dfIBYTE, dfHAPVIDA, dfNAGEM]).reset_index()

# Transforma a coluna TEMPO no formato de data e hora
df['TEMPO']=pd.to_datetime(df['TEMPO'])

# Cria coluna ESTADOS a partir da coluna LOCAL
estados_lista =  []
df['MUNICIPIO'] = df['LOCAL']
for i, x in df.iterrows():
  split = x['LOCAL'].split('-')
  df.loc[i, 'MUNICIPIO'] = "-".join(split[:-1])
  estados_lista.append(split[len(split)-1].strip())

# Cria coluna com o total de palavras da coluna DESCRICAO
df['TOTAL_PALAVRAS'] = df['DESCRICAO'].apply(lambda x: len(x.split(" ")))

df['ESTADO'] = estados_lista

# Remove linha com ESTADO vazio
df = df[(df['ESTADO'] != '')  & (df['ESTADO'] != 'naoconsta')]

empresas = ['IBYTE', 'HAPVIDA', 'NAGEM']
columns = ['EMPRESA', 'MUNICIPIO', 'ESTADO', 'STATUS', 'TEMA', 'TEMPO', 'CATEGORIA','DESCRICAO', 'URL', 'ANO', 'MES', 'DIA', 'DIA_DO_ANO', 'SEMANA_DO_ANO', 'DIA_DA_SEMANA', 'TRIMETRES', 'CASOS', 'TOTAL_PALAVRAS']
st.session_state.columns = columns
for col in columns:
    st.session_state[col] = True

status_list = pd.unique(df["STATUS"])    
status_list = np.insert(status_list, 0, "Todas")

estado_list = pd.unique(df["ESTADO"])    
estado_list = np.insert(estado_list, 0, "Todos")

# palavras_list = pd.unique(df["TOTAL_PALAVRAS"])    
# palavras_list = np.insert(palavras_list, 0, "Todos")

#
# Start streamlist config page
#
st.set_page_config(
   page_title = "Real-Time Reclame Aqui Dashboard",
   layout="wide"
)

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


data = df

# Cria componentes
# st.header('This is a header with a divider', divider='rainbow')
# st.header('_Streamlit_ is :blue[cool] :sunglasses:')

with st.sidebar:
    empresas_selected = st.multiselect(
        "Seleção das Empresas", empresas, empresas
    )

    # 
    estado_filter = st.selectbox("Selecione o Estado", estado_list)
    status_filter = st.selectbox("Selecione o Status", status_list)
    # tamanho_max_texto = data['TOTAL_PALAVRAS'].max()
    # palavras_filter = st.slider('Número de palavras', 1,
    #                         value = tamanho_max_texto,
    #                         max_value = tamanho_max_texto)
                                                              
    included = st.expander('Seleção de Colunas', expanded=True)
    with included:
        st.write('')

    for col in columns:
        with included:
            st.session_state[col] = st.checkbox(col, value=True)    

if not empresas_selected:
    data = df
else:
    data = df[df['EMPRESA'].isin(empresas_selected)]

if status_filter != "Todas":
    data = df[df["STATUS"] == status_filter]

if estado_filter != "Todos":
    data = df[df["ESTADO"] == estado_filter]

container = st.container(border=True)
numero_linhas = container.slider('Número de experimentos', 1, 
                            value = len(data),
                            max_value = len(data))

data = data.iloc[0:numero_linhas]

col1, col2, col3 = st.columns(3)
with col1:
    if 'IBYTE' in empresas_selected:
        info_total_experimentos = len(data[data['EMPRESA'] == 'IBYTE'])
        st.metric('IBYTE', info_total_experimentos)
with col2:
    if 'HAPVIDA' in empresas_selected:
        info_total_experimentos = len(data[data['EMPRESA'] == 'HAPVIDA'])
        st.metric('HAPVIDA', info_total_experimentos)
with col3:
    if 'NAGEM' in empresas_selected:
        info_total_experimentos = len(data[data['EMPRESA'] == 'NAGEM'])
        st.metric('NAGEM', info_total_experimentos)        

# Filtro selecao de colunas
columns_selected = []
for col in columns:
    if st.session_state[col]:
        columns_selected.append(col)
if len(columns_selected) == 0:
    columns_selected = columns        
dataGrid = data[columns_selected]

tab1, tab2 = st.tabs(["Dados", "Gráficos"])

with tab1:
    st.write("### Tabela de Dados do Reclame Aqui", dataGrid.sort_index())
    csv = convert_df(dataGrid)
    st.download_button(
        "Download da Tabela no formato CSV",
        csv,
        "reclamacoes_ibyte_hapvida_nagem.csv",
        "text/csv",
        key='download-csv'
    )

with tab2:    
    df_serie1 = data[['EMPRESA', 'TEMPO', 'TOTAL_PALAVRAS']].set_index(['EMPRESA', 'TEMPO']).groupby(['EMPRESA', 'TEMPO'])['TOTAL_PALAVRAS'].count().reset_index()
    fig1 = px.line(df_serie1,
                            x = 'TEMPO',
                            y = 'TOTAL_PALAVRAS',
                            line_group = 'EMPRESA',
                            markers=True,
                            range_y=(0, df_serie1.max()),
                            color = 'EMPRESA',
                            title= 'Série temporal do número de reclamações'
                    ).update_layout(
                       xaxis_title="Tempo", yaxis_title="Total"
                    )                            
    st.plotly_chart(fig1, use_container_width=True)    

    df_serie2 = data[['EMPRESA', 'TEMPO', 'TOTAL_PALAVRAS']].set_index(['EMPRESA', 'TEMPO']).groupby(['EMPRESA', 'TEMPO'])['TOTAL_PALAVRAS'].sum().reset_index()
    fig2 = px.line(df_serie2,
                            x = 'TEMPO',
                            y = 'TOTAL_PALAVRAS',
                            line_group = 'EMPRESA',
                            markers=True,
                            range_y=(0, df_serie2.max()),
                            color = 'EMPRESA',
                            title= 'Distribuição do tamanho do texto'
                    ).update_layout(
                       xaxis_title="Tempo", yaxis_title="Total"
                    )
    st.plotly_chart(fig2, use_container_width=True)    


    fig, ax = plt.subplots(figsize=(16,9))
    df_estado = data[['EMPRESA', 'ESTADO', 'TOTAL_PALAVRAS']].sort_values(by = ['ESTADO']).groupby(['ESTADO', 'EMPRESA'])['TOTAL_PALAVRAS'].count().reset_index()

    sns.lineplot(data=df_estado, x='ESTADO', y='TOTAL_PALAVRAS', hue='EMPRESA')
    # plt.tick_params(top='off', bottom='off', left='off', right='off')
    plt.yticks(color='white')
    plt.xticks(rotation=75, color='white')
    # ax.set(xlabel='Estado', ylabel='Reclamações')
    ax.set_xlabel('Estado', color='white')
    ax.set_ylabel('Reclamações', color='white')
    # plt.grid()
    ax.yaxis.grid()
    ax.set(frame_on=False) 
    for item in [fig, ax]:
        item.patch.set_visible(False) 
    st.pyplot(ax.figure)
 
   