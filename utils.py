import requests
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
from sklearn.cluster import KMeans

def get_sidra_dados():
    """
    Função para buscar os dados da API SIDRA para a tabela 1757 (empresas de construção).
    A variável 'Faixas de pessoal ocupado' em 'Número de empresas ativas' por estado foi
    filtrada para '5 ou mais pessoas', pois empresas com menos de 5 ocupados estão estratificadas
    por regiões, enquanto as com 5 ou mais estão separadas por Unidade da Federação (UF).
    """
    url = "https://apisidra.ibge.gov.br/values/t/1757/n3/all/v/410/p/first%2014/c319/104030"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção para erros HTTP
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao acessar a API do SIDRA: {e}")

def checkData(data, name):
    if data.isnull().values.any():
        print(f'O DataFrame {name} contém valores nulos.')
    else:
        print(f'O DataFrame {name} não contém valores nulos.')


def cleanData(df_sidra_bruto, df_populacao_bruto, estados):
    print("Checando os tipos das variáveis e se há valores nulos")
    #print(df_sidra_bruto.info())
    checkData(df_sidra_bruto, "SIDRA")
    checkData(df_populacao_bruto, "IBGE")

    # Filtrar os estados de interesse
    #valores_unicos_local = df_populacao_bruto['LOCAL'].unique()
    #print(valores_unicos_local)

    IDADE_MIN = 38
    IDADE_MAX = 58
    print(f"Filtrando faixa etária de interesse ({IDADE_MIN} - {IDADE_MAX})")
    df_idade_filtrada = df_populacao_bruto[
        (df_populacao_bruto['IDADE'] >= IDADE_MIN) & (df_populacao_bruto['IDADE'] <= IDADE_MAX)
    ]

    print(f"Filtrando estados")
    df_estados = df_idade_filtrada[df_idade_filtrada['LOCAL'].isin(estados)]

    print("Selecionando população total (sexo = 'Ambos')")
    df_filtrado_sexo = df_estados[df_estados['SEXO'] == 'Ambos']

    print("Selecionando colunas de interesse: 'LOCAL' e os anos de 2007 a 2020")
    anos_desejados = list(range(2007, 2021))
    colunas_selecionadas = ['LOCAL'] + anos_desejados

    # Criar um DataFrame apenas com as colunas selecionadas
    df_selecionado = df_filtrado_sexo[colunas_selecionadas]

    # Agregar a população por estado e ano, somando as idades de 38 a 58
    df_pop_agregado = df_selecionado.groupby('LOCAL', as_index=False)[anos_desejados].sum()

    # Reorganizar o DataFrame no formato longo (long format)
    df_pop_agregado = df_pop_agregado.melt(id_vars=['LOCAL'], var_name='ANO', value_name='POPULACAO')

    # Ordenar o DataFrame para facilitar a visualização
    df_pop_agregado = df_pop_agregado.sort_values(by=['LOCAL', 'ANO']).reset_index(drop=True)

    # Exibir o resultado consolidado
    #print(df_pop_agregado.head())

    print("Unificando base de dados (SIDRA e IBGE)")
    # Agora, vamos obter os valores únicos de cada coluna referente ao estado
    # de ambas as planilhas para checar se estão idênticas para poder
    # seguir com o merge
    estados_sidra = set(df_sidra_bruto['Unidade da Federação'].unique())
    estados_pop = set(df_pop_agregado['LOCAL'].unique())

    # Verificar se os conjuntos são iguais
    if estados_sidra != estados_pop:
        print("Há diferenças nos nomes dos estados entre as duas colunas.")

        # Mostrar diferenças, se houver
        if estados_sidra - estados_pop:
            print("Estados presentes em SIDRA mas não em IBGE:", estados_sidra - estados_pop)
        if estados_pop - estados_sidra:
            print("Estados presentes em IBGE mas não em SIDRA:", estados_pop - estados_sidra)

    # Agora vamos selecionar as colunas de interesse da planilha da SIDRA
    df_sidra_long = df_sidra_bruto[['Unidade da Federação', 'Ano', 'Valor']]

    # Renomear as colunas da SIDRA para facilitar o merge com a do IBGE
    # e renomear a coluna de interesse sobre número de empresas ativas
    df_sidra_long = df_sidra_long.rename(columns={
        'Unidade da Federação': 'LOCAL',
        'Ano': 'ANO',
        'Valor': 'EMPRESAS_ATIVAS'
    })

    # Verificar o resultado
    # df_sidra_long.head()

    print("Ajustando os tipos das variáveis")
    # Converter 'EMPRESAS_ATIVAS' para int
    df_sidra_long['EMPRESAS_ATIVAS'] = df_sidra_long['EMPRESAS_ATIVAS'].astype(int)

    # Converter 'ANO' para datetime em ambas as tabelas
    df_sidra_long['ANO'] = pd.to_datetime(df_sidra_long['ANO'], format='%Y')
    df_pop_agregado['ANO'] = pd.to_datetime(df_pop_agregado['ANO'], format='%Y')

    # Checar se os tipos das variáveis estão equivalentes antes do merge
    #print(df_sidra_long.info()_
    #print("\n")
    #print(df_pop_agregado.info())

    # Realizar o merge tendo como base a coluna LOCAL (estado) e ANO (ano)
    df_final = pd.merge(df_pop_agregado, df_sidra_long, on=['LOCAL', 'ANO'], how='inner')

    # Selecionar as colunas de interesse
    df_final = df_final[['LOCAL', 'ANO', 'POPULACAO', 'EMPRESAS_ATIVAS']]

    # Verificar o resultado
    # df_final.head()

    print("Criando uma nova coluna 'RAZAO' que é a razão entre POPULACAO e EMPRESAS_ATIVAS")
    df_final['RAZAO'] = (df_final['POPULACAO'] / df_final['EMPRESAS_ATIVAS']).round(2)

    # Dropar as colunas 'POPULACAO' e 'EMPRESAS_ATIVAS', para deixar só as colunas de interesse
    df_final = df_final.drop(['POPULACAO', 'EMPRESAS_ATIVAS'], axis=1)

    # Converter a coluna ANO para datetime e associá-la ao índice do DataFrame
    df_final = df_final.set_index('ANO')

    return df_final

def runDescriptiveAnalysis(data):
    # Gráfico interativo para ver o comportamento geral dos dados
    fig = px.line(
        data,
        x=data.index,
        y='RAZAO',
        color='LOCAL',
        labels={'RAZAO': 'RAZAO', 'index': 'Ano'},
        title='Razão entre o número de consumidores e o número de empresas ativas ao longo dos anos, por estado',
        hover_name='LOCAL'
    )

    # Personalizando o layout
    fig.update_layout(
        xaxis_title='Passagem do tempo em anos',
        yaxis_title='Razão entre número de consumidores por empresas ativas',
        legend_title='Estado',
        hovermode='closest'
    )

    fig.write_image("output/descriptiveAnalysis.png")
#   fig.show()

def runDescriptiveAnalysisByState(data):
    # Usar a coluna 'LOCAL' para identificar os estados
    estados = data['LOCAL'].unique()

    # Criar uma figura com subplots
    fig, axes = plt.subplots(len(estados), 1, figsize=(10, 5 * len(estados)))

    # Iterar sobre os estados e plotar cada gráfico
    for i, estado in enumerate(estados):
        df_estado = data[data['LOCAL'] == estado]  # Filtrar o DataFrame para o estado atual
        axes[i].plot(df_estado.index, df_estado['RAZAO'], label=estado)
        axes[i].set_title(f'Razão entre número de consumidores por empresas ativas em {estado}')
        axes[i].set_xlabel('Passagem do tempo em anos')
        axes[i].set_ylabel('Razão entre número de consumidores por empresas ativas')
        axes[i].legend()

    # Ajustar o layout para evitar sobreposição
    plt.tight_layout()
    plt.savefig("output/descriptiveAnalysisByState.png")
    #plt.show()

def runSazonalDecomposedByState(data):
    # Usando a coluna 'LOCAL' para identificar os estados
    estados = data['LOCAL'].unique()

    # Iterar sobre cada estado
    for estado in estados:
        # Filtrar o DataFrame para o estado atual
        df_estado = data[data['LOCAL'] == estado]

        # Aplicar a decomposição sazonal (sem sazonalidade, pois os dados são anuais)
        try:
            result = seasonal_decompose(df_estado['RAZAO'], model='additive', period=1)  # Periodo 1 para dados anuais
        except ValueError as e:
            print(f"Erro ao processar {estado}: {e}")
            continue

        # Criar uma figura com 3 subplots (sem sazonalidade)
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 8))

        # Plotar os componentes da decomposição
        result.observed.plot(ax=ax1, title=f'{estado} - Observado')
        result.trend.plot(ax=ax2, title=f'{estado} - Tendência')
        result.resid.plot(ax=ax3, title=f'{estado} - Resíduo')

        # Ajustar o layout
        plt.tight_layout()

        # Salvar a figura em um arquivo (opcional)
        plt.savefig(f'output/decomposicao/decomposicao_{estado}.png')

        # Mostrar a figura
        #plt.show()

def runPrevisions(data, estados):
    # Dicionário para armazenar as previsões
    previsoes_prophet = {}

    # Iterar sobre cada estado
    for estado in estados:
        # Filtrar o DataFrame para o estado atual
        df_estado = data[data['LOCAL'] == estado]

        # Resetar o índice para transformar 'ANO' em uma coluna regular
        df_estado = df_estado.reset_index()

        # Verificar se a coluna 'ANO' está presente
        if 'ANO' not in df_estado.columns:
            raise KeyError(f"A coluna 'ANO' não foi encontrada no DataFrame após o reset do índice.")

        # Preparar os dados para o Prophet
        df_prophet = df_estado[['ANO', 'RAZAO']].rename(columns={'ANO': 'ds', 'RAZAO': 'y'})

        # Converter a coluna 'ds' para datetime (se necessário)
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'], format='%Y')

        # Ajustar o modelo Prophet
        modelo = Prophet(n_changepoints=5, weekly_seasonality=False, daily_seasonality=False)
        modelo.fit(df_prophet)

        # Criar um DataFrame para previsões futuras (2021 e 2022)
        futuro = modelo.make_future_dataframe(periods=2, freq='YE')

        # Fazer previsões
        previsao = modelo.predict(futuro)

        # Armazenar as previsões
        previsoes_prophet[estado] = previsao[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(2)

        # Plotar os dados históricos e as previsões
        modelo.plot(previsao, uncertainty=True)
        plt.title(f'Previsão para {estado} (2021-2022)')
        plt.xlabel('Ano')
        plt.ylabel('RAZAO')
        #plt.show()
        plt.savefig(f'output/previsao/previsao_{estado}.png')

    # Exibir as previsões
    for estado, dados in previsoes_prophet.items():
        print(f"Previsão para {estado}:")
        print(dados)
        print("\n")
    
    return previsoes_prophet

def createClusterAnalysis(df_previsoes):
    # Juntar as previsões de todos os estados em um único DataFrame
    df_previsoes = pd.concat(df_previsoes.values(), keys=df_previsoes.keys())
    df_previsoes = df_previsoes.reset_index().rename(columns={'level_0': 'Estado'})

    # Calcular a média da razão prevista para cada estado
    df_media_razao = df_previsoes.groupby('Estado')['yhat'].mean().reset_index()

    # Clusterização com K-Means (3 clusters)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_media_razao['Cluster'] = kmeans.fit_predict(df_media_razao[['yhat']])

    # Classificar os clusters com base na média da razão
    cluster_ordenado = df_media_razao.groupby('Cluster')['yhat'].mean().sort_values().index
    df_media_razao['Cluster'] = df_media_razao['Cluster'].replace({
        cluster_ordenado[0]: 'Razão baixa (Oportunidades)',
        cluster_ordenado[1]: 'Razão neutra',
        cluster_ordenado[2]: 'Razão alta (Saturados)'
    })

    # Exibir a tabela de clusterização
    print("Tabela de Clusterização:")
    print(df_media_razao)

    """
    Faremos também um gráfico para ajudar na visualização dos resultado dos estados
    agrupados por clusters, destacando aqueles com maior ou menor RAZAO.
    """

    # Criar o scatter plot
    fig = px.scatter(
        df_media_razao,
        x='Estado',
        y='yhat',
        color='Cluster',
        title='Clusterização dos Estados por Razão (2021-2022)',
        labels={'yhat': 'Média da Razão Prevista', 'Estado': 'Estado'},
        hover_name='Estado',
        color_discrete_map={
            'Razão baixa (Oportunidades)': 'blue',
            'Razão neutra': 'green',
            'Razão alta (Saturados)': 'red'
        }
    )

    # Personalizar o layout
    fig.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(
        xaxis_title='Estado',
        yaxis_title='Média da Razão Prevista',
        showlegend=True
    )

    # Mostrar o gráfico
    #fig.show()
    fig.write_image("output/cluster.png")
