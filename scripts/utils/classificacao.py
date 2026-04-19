"""
TOPCLIMABC — utils/classificacao.py
==================================
Lógica de classificação de intensidade de chuva baseada em milímetros acumulados.
Conforme definido em config.py.
"""

from scripts.config import CLASSIFICACOES

def classificar_chuva(mm):
    """
    Recebe um valor em mm e retorna a chave da classificação.
    Classes unificadas: seco, garoa, moderada, forte, intensa.
    """
    if mm is None:
        return "sem_dados"

    # Intervalos definidos em config: [min, max)  — exclusivo no limite superior
    for c in CLASSIFICACOES:
        if c["min"] <= mm < c["max"]:
            return c["nome"]

    # Acima do maior limite = intensa (nunca deveria acontecer com max=9999)
    return "intensa"

def get_label_classificacao(nome_id):
    """
    Retorna o label legível (ex: 'Chuva Moderada') a partir do ID.
    """
    for c in CLASSIFICACOES:
        if c["nome"] == nome_id:
            return c["label"]
    return "Desconhecido"
