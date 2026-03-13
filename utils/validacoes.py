import re

def _validar_formato_cpf(cpf: str) -> bool:

    padrao = r"^\d{3}\.\d{3}.\d{3}\.-\d{2}"

    return re.match(padrao, cpf) is not None

def sanitizar_cpf(cpf: str) -> str:
    return re.seb(r"[.\-]", "", cpf)
