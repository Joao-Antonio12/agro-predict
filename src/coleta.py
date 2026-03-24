import requests
import pandas as pd
import time
from pathlib import Path

# dicionário de municípios produtores de milho em MG (mais relevantes em dados)

MUNICIPIOS = {

    # Triângulo Mineiro
    "uberaba"            : {"lat": -19.74, "lon": -47.93, "regiao": "Triangulo"},
    "uberlandia"         : {"lat": -18.91, "lon": -48.27, "regiao": "Triangulo"},
    "araxa"              : {"lat": -19.59, "lon": -46.94, "regiao": "Triangulo"},
    "ituiutaba"          : {"lat": -18.96, "lon": -49.46, "regiao": "Triangulo"},

    # Alto Paranaíba
    "patos_de_minas"     : {"lat": -18.57, "lon": -46.51, "regiao": "Alto Paranaiba"},
    "presidente_olegario": {"lat": -18.41, "lon": -46.41, "regiao": "Alto Paranaiba"},
    "rio_paranaiba"      : {"lat": -19.18, "lon": -46.24, "regiao": "Alto Paranaiba"},
    "carmo_paranaiba"    : {"lat": -18.99, "lon": -46.31, "regiao": "Alto Paranaiba"},

    # Sul de Minas
    "lavras"             : {"lat": -21.24, "lon": -44.99, "regiao": "Sul de Minas"},
    "passos"             : {"lat": -20.71, "lon": -46.60, "regiao": "Sul de Minas"},
    "alfenas"            : {"lat": -21.42, "lon": -45.94, "regiao": "Sul de Minas"},
    "pocos_de_caldas"    : {"lat": -21.78, "lon": -46.56, "regiao": "Sul de Minas"},

    # Região Central
    "sete_lagoas"        : {"lat": -19.47, "lon": -44.25, "regiao": "Central"},
    "para_de_minas"      : {"lat": -19.86, "lon": -44.60, "regiao": "Central"},
    "pompeu"             : {"lat": -19.22, "lon": -45.00, "regiao": "Central"},

    # Noroeste
    "paracatu"           : {"lat": -17.22, "lon": -46.87, "regiao": "Noroeste"},
    "joao_pinheiro"      : {"lat": -17.74, "lon": -46.17, "regiao": "Noroeste"},
    "brasilania_minas"   : {"lat": -16.98, "lon": -45.60, "regiao": "Noroeste"},

    # Zona da Mata
    "vicosa"             : {"lat": -20.75, "lon": -42.87, "regiao": "Zona da Mata"},
    "muriae"             : {"lat": -21.13, "lon": -42.36, "regiao": "Zona da Mata"},
}

#configurações 

ANO_INICIO = 2000
ANO_FIM    = 2024
PASTA_RAW  = Path(__file__).parent.parent / "data" / "raw"


#funções

def coletar_clima_municipio(nome, info):
    """
    Coleta dados climáticos diários de um município
    via Open-Meteo e retorna um DataFrame.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    variaveis = ",".join([
        "precipitation_sum",
        "temperature_2m_max",
        "temperature_2m_min",
        "et0_fao_evapotranspiration"
    ])

    parametros = {
        "latitude"  : info["lat"],
        "longitude" : info["lon"],
        "start_date": f"{ANO_INICIO}-01-01",
        "end_date"  : f"{ANO_FIM}-12-31",
        "daily"     : variaveis,
        "timezone"  : "America/Sao_Paulo"
    }

    resposta = requests.get(url, params=parametros)

    if resposta.status_code != 200:
        print(f"  Erro {resposta.status_code} em {nome}: {resposta.text}")
        return None

    dados = resposta.json()["daily"]
    df = pd.DataFrame(dados)

    df = df.rename(columns={
        "time"                      : "data",
        "precipitation_sum"         : "chuva_mm",
        "temperature_2m_max"        : "temp_max",
        "temperature_2m_min"        : "temp_min",
        "et0_fao_evapotranspiration": "evapotranspiracao"
    })

    # adiciona identificação do município e região pertencente
    df["municipio"] = nome
    df["regiao"]    = info["regiao"]

    return df


def coletar_todos_municipios():
    """
    Coleta dados climáticos de todos os municípios
    e salva em data/raw/clima_municipios_mg.csv
    """

    print(f"Coletando dados de {len(MUNICIPIOS)} municípios...\n")

    frames = []

    for nome, info in MUNICIPIOS.items():
        print(f"  Coletando {nome} ({info['regiao']})...")
        df = coletar_clima_municipio(nome, info)

        if df is not None:
            frames.append(df)
            print(f"  OK — {len(df)} dias coletados")
        

            time.sleep(60) #API não atende tantas requisições ao mesmo tempo

    #junta todos os municípios em um DataFrame
    df_total = pd.concat(frames, ignore_index=True)

    PASTA_RAW.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_RAW / "clima_municipios_mg.csv"
    df_total.to_csv(caminho, index=False)

    print(f"\nConcluído!")
    print(f"Total de linhas: {len(df_total)}")
    print(f"Municípios: {df_total['municipio'].nunique()}")
    print(f"Arquivo salvo em: {caminho}")

    return df_total


def coletar_produtividade():
    """
    Cria o arquivo de produtividade histórica do milho em MG
    com dados reais da CONAB.
    Fonte: https://www.conab.gov.br/info-agro/safras/serie-historica
    """

    print("\nCriando base de produtividade histórica (CONAB)...")

    dados = {
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

    return df


#execução

if __name__ == "__main__":
    coletar_todos_municipios()
    coletar_produtividade()