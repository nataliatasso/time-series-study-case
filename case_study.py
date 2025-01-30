import requests
import pandas as pd

from utils import get_sidra_dados 

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

print("End of case study")