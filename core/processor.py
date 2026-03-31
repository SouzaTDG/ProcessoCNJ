import pandas as pd
import json

from core.cnj_parser import extrair_dados_cnj
from core.detector import detectar_coluna_processo
from core.comarca_loader import carregar_comarcas


# =========================
# CARREGAR MAPA TR → UF
# =========================
def carregar_mapa_tribunal(caminho_json: str) -> dict:
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================
def processar_arquivo(
    caminho_input: str,
    caminho_comarcas: str,
    caminho_tribunal: str,
    caminho_saida: str = None,
    callback_progresso=None
) -> str:
    """
    Processa um arquivo Excel e adiciona colunas:
    - Estado_Calculado
    - Comarca_Calculada
    - Localidade
    """

    # =========================
    # 1. LEITURA
    # =========================
    df = pd.read_excel(caminho_input)

    comarcas = carregar_comarcas(caminho_comarcas)
    tribunal_uf = carregar_mapa_tribunal(caminho_tribunal)

    # =========================
    # 2. DETECTAR COLUNA
    # =========================
    coluna_processo = detectar_coluna_processo(df)

    if not coluna_processo:
        raise Exception("Não foi possível identificar a coluna de processos.")

    # =========================
    # 3. PROCESSAMENTO COM PROGRESSO
    # =========================
    total = len(df)

    ufs = []
    comarcas_calc = []
    localidades = []

    for i, numero in enumerate(df[coluna_processo].astype(str), start=1):
        tr, origem = extrair_dados_cnj(numero)

        if not tr:
            uf = None
            comarca = None
            localidade = "CNJ inválido"
        else:
            uf = tribunal_uf.get(tr)

            if not uf:
                comarca = None
                localidade = "TR não mapeado"
            else:
                comarca = comarcas.get(uf, {}).get(origem)

                if not comarca:
                    localidade = "Comarca não encontrada"
                else:
                    localidade = f"{comarca}/{uf}"

        ufs.append(uf)
        comarcas_calc.append(comarca)
        localidades.append(localidade)

        # 🔥 Atualização de progresso
        if callback_progresso:
            callback_progresso(i, total)

    # =========================
    # 4. ATRIBUIR COLUNAS
    # =========================
    df["Estado_Calculado"] = ufs
    df["Comarca_Calculada"] = comarcas_calc
    df["Localidade"] = localidades

    # =========================
    # 5. DEFINIR SAÍDA
    # =========================
    if not caminho_saida:
        caminho_saida = caminho_input.replace(".xlsx", "_corrigido.xlsx")

    # =========================
    # 6. SALVAR
    # =========================
    df.to_excel(caminho_saida, index=False)

    return caminho_saida