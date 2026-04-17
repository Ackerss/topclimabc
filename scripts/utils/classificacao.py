"""
TOPCLIMABC — utils/classificacao.py
==================================
Lógica de classificação de intensidade de chuva baseada em milímetros acumulados.
Conforme definido em config.py.
"""

from scripts.config import CLASSIFICACOES

def classificar_chuva(mm):
    """
    Recebe um valor em mm e retorna a chave da classificação (ex: 'fraca', 'moderada').
    """
    if mm is None:
        return "sem_dados"
    
    # Itera sobre as classificações definidas na config
    for c in CLASSIFICACOES:
        if c["min"] <= mm <= c["max"]:
            return c["nome"]
            
    # Fallback caso algo dê errado
    return "sem_chuva"

def get_label_classificacao(nome_id):
    """
    Retorna o label legível (ex: 'Chuva Moderada') a partir do ID.
    """
    for c in CLASSIFICACOES:
        if c["nome"] == nome_id:
            return c["label"]
    return "Desconhecido"
