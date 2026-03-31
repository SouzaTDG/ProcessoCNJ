import pandas as pd


def carregar_comarcas(caminho_arquivo: str) -> dict:
    """
    Carrega a planilha de comarcas e retorna um dicionário no formato:
    {
        "RS": {
            "0002": "Alegrete"
        }
    }
    """

    df = pd.read_excel(caminho_arquivo, dtype={"CÓDIGO": str})

    # limpeza básica
    df.columns = df.columns.str.strip()

    # garantir formato correto
    df["CÓDIGO"] = df["CÓDIGO"].astype(str).str.zfill(4)
    df["ESTADO"] = df["ESTADO"].astype(str).str.strip()
    df["COMARCA"] = df["COMARCA"].astype(str).str.strip()

    comarcas = {}

    for _, row in df.iterrows():
        uf = row["ESTADO"]
        codigo = row["CÓDIGO"]
        nome = row["COMARCA"]

        if not uf or not codigo or not nome:
            continue

        comarcas.setdefault(uf, {})[codigo] = nome

    return comarcas

