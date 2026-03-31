import re
from typing import Tuple, Optional

# Regex padrão CNJ
CNJ_PATTERN = re.compile(
    r"\d{7}-\d{2}\.\d{4}\.\d\.(\d{2})\.(\d{4})"
)

def extrair_dados_cnj(numero: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrai TR (tribunal) e código de origem (comarca) de um número CNJ.

    Args:
        numero (str): Número do processo CNJ

    Returns:
        Tuple (tr, origem)
        - tr: código do tribunal (2 dígitos)
        - origem: código da comarca (4 dígitos)
        - retorna (None, None) se inválido
    """

    if not numero:
        return None, None

    numero = str(numero).strip()

    match = CNJ_PATTERN.match(numero)

    if not match:
        return None, None

    tr = match.group(1)
    origem = match.group(2)

    return tr, origem
