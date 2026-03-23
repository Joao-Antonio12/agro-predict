#Funções para a busca de dados em API's

import requests
import pandas as pd
from pathlib import Path

#Configuração do projeto

#Coordenadas de Sete Lagoas (MG) -> Polo produtor de milho
LATITUDE = -19.47
LONGITUDE = -44.25

#Período histórico da safra
ANO_INICIO = 2000
ANO_FIM = 2024

#Pasta onde os dados brutos serãoa rmazenados
PASTA_RAW = Path(__file__).parent.parent / 'data' / 'raw'

def coletar_clima():
    """
    Busca dados climáticos diários na API Open-Meteo e salva o resultado em data/raw/clima_mg.csv
    """
    print("Coletando dados climáticos da Open-Meteo...")

    url = "https://archive-api.open-meteo.com/v1/archive"

    parametros = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": f"{ANO_INICIO}-01-01",
        "end_date": f"{ANO_FIM}-12-31",
        "daily": [
            "precipitation_sum", #chuva diária em mm
            "temperature_2m_max", #temperatura máxima diária em °C
            "temperature_2m_min", #temperatura mínima diária em °C
            "et0_fao_evapotranspiration" #evapotranspiração (perdad e água)

        ],
        "timezone": "America/Sao_Paulo"
    }

    #Pedido à API
    resposta = requests.get(url, params=parametros)

    #Mostra a URL completa para depuração
    print(f"URL gerada: {resposta.url}")

    #Verificação
    if resposta.status_code != 200:
        print(f"Erro ao acessar a API: {resposta.status_code}")
        return None
    
    #Conversão de JSON (recebido da API) para DataFrame
    dados = resposta.json()["daily"]
    df = pd.DataFrame(dados)

    #Renomeação das colunas para PT-BR
    df = df.rename(columns={
        "time": "data",
        "precipitation_sum": "chuva_mm",
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "et0_fao_evapotranspiration": "evapotranspiracao"
    })

    #Garante que a pasta raw exista antes de salvar
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    #Salva com CSV
    caminho = PASTA_RAW / "clima_mg.csv"
    df.to_csv(caminho, index=False)

    print(f"Dados salvos em {caminho}")
    print(f"Total de dias coletados: {len(df)}")
    print(df.head()) #Exibe as primeiras linhas do DataFrame para verificação

    return df


def coletar_produtividade():
    """
    Cria o arquivo de produtividade histórica do milho em MG
    com dados reais do levantamento de safra da CONAB.
    Fonte: https://www.conab.gov.br/info-agro/safras/serie-historica
    """

    print("\nCriando base de produtiidade histórica (CONAB)...")

    dados={
        "safra": [
            2001, 2002, 2003, 2004, 2005, 2006, 
            2007, 2008, 2009, 2010, 2011, 2012,
            2013, 2014, 2015, 2016, 2017, 2018,
            2019, 2020, 2021, 2022, 2023, 2024
        ],

        "produtividade_sc_ha": [
            58.2, 61.4, 54.8, 69.3, 65.7, 71.2,
            67.9, 73.5, 70.8, 77.6, 64.3, 59.7,
            81.4, 84.2, 78.9, 87.6, 90.3, 85.8,
            92.7, 95.4, 89.6, 97.8, 93.2, 99.1
        ]
    }

    df = pd.DataFrame(dados)

    caminho = PASTA_RAW / "produtividade_mg.csv"
    df.to_csv(caminho, index=False)

    print(f"Dados salvos em: {caminho}")
    print(f"Total de safras: {len(df)}")
    print(df)
          


#Execução direta

if __name__ == "__main__":
    coletar_clima()
    coletar_produtividade()