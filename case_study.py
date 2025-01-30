import requests
import pandas as pd

from utils import get_sidra_dados, checkData, cleanData, runDescriptiveAnalysis, runDescriptiveAnalysisByState, runSazonalDecomposedByState, runPrevisions, createClusterAnalysis

ESTADOS = [
        'Rondônia', 'Acre', 'Amazonas', 'Roraima', 'Pará', 'Amapá', 'Tocantins',
        'Maranhão', 'Piauí', 'Ceará', 'Rio Grande do Norte', 'Paraíba',
        'Pernambuco', 'Alagoas', 'Sergipe', 'Bahia', 'Minas Gerais',
        'Espírito Santo', 'Rio de Janeiro', 'São Paulo', 'Paraná',
        'Santa Catarina', 'Rio Grande do Sul', 'Mato Grosso do Sul',
        'Mato Grosso', 'Goiás', 'Distrito Federal'
    ]

print("Lendo as bases de dados")
# Buscar dados e transformar em DataFrame
dados = get_sidra_dados()
df_sidra_bruto = pd.DataFrame(dados)

# Ajustar a primeira linha como cabeçalho e remover a primeira linha extra
df_sidra_bruto.columns = df_sidra_bruto.iloc[0]
df_sidra_bruto = df_sidra_bruto.drop(0).reset_index(drop=True)

# Exibir os primeiros registros
#print(df_sidra_bruto.head())

# Carregar dados do Excel
df_populacao_bruto = pd.read_excel("data/projecoes_2024_tab1_idade_simples.xlsx", skiprows=5)
# Exibir os primeiros registros
#print(df_populacao_bruto.head())

print("Processando base de dados")
df_final = cleanData(df_sidra_bruto, df_populacao_bruto, ESTADOS)
# Exibindo as primeiras linhas do DataFrame para verificar a nova coluna
print("Após tratar e unir as tabelas. Temos o seguinte DataFrame:")
print(df_final.head())

print("Iniciando análise")
runDescriptiveAnalysis(df_final)
runDescriptiveAnalysisByState(df_final)
runSazonalDecomposedByState(df_final)
df_previsoes = runPrevisions(df_final, ESTADOS)
createClusterAnalysis(df_previsoes)

print("Fim análise")
