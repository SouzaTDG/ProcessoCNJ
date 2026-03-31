import re
import pandas as pd

# mesma regex do parser (poderíamos centralizar depois)
CNJ_REGEX = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")


def detectar_coluna_processo(df: pd.DataFrame) -> str | None:
    """
    Detecta automaticamente a coluna que contém números de processo CNJ.
    """

    # =========================
    # 1. PRIORIDADE: NOME DA COLUNA
    # =========================
    palavras_chave = [
        "processo",
        "processo cnj",
        "nº processo",
        "numero processo",
        "num processo"
    ]

    for col in df.columns:
        nome = col.lower().strip()

        if any(p in nome for p in palavras_chave):
            return col

    # =========================
    # 2. FALLBACK: CONTEÚDO
    # =========================
    for col in df.columns:
        serie = df[col].dropna().astype(str)

        if serie.empty:
            continue

        amostra = serie.head(20)

        matches = amostra.str.contains(CNJ_REGEX)

        taxa_match = matches.mean()

        if taxa_match > 0.7:
            return col

    return None
