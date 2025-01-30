import requests
import pandas as pd

from utils import get_sidra_dados, checkData

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
estados = [
    'Rondônia', 'Acre', 'Amazonas', 'Roraima', 'Pará', 'Amapá', 'Tocantins',
    'Maranhão', 'Piauí', 'Ceará', 'Rio Grande do Norte', 'Paraíba',
    'Pernambuco', 'Alagoas', 'Sergipe', 'Bahia', 'Minas Gerais',
    'Espírito Santo', 'Rio de Janeiro', 'São Paulo', 'Paraná',
    'Santa Catarina', 'Rio Grande do Sul', 'Mato Grosso do Sul',
    'Mato Grosso', 'Goiás', 'Distrito Federal'
]
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

# Exibindo as primeiras linhas do DataFrame para verificar a nova coluna
print("Após tratar e unir as tabelas. Temos o seguinte DataFrame:")
print(df_final.head())