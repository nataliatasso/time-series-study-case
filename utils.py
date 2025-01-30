import requests

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