"""
TOPCLIMABC — utils/score.py
===========================
Algoritmo de auditoria de acerto (0 a 100).

Alinhado com ARCHITECTURE.md — seção "Algoritmo de Score Gradual":

  Fator 1 — Acerto de Classificação (peso 60%)
    Matriz 5x5 com penalidades graduais: quanto mais distante a classe
    prevista da real, maior a penalidade.

  Fator 2 — Erro em Milímetros (peso 40%)
    score_mm = max(0, 100 - erro_mm * 5)     # cada 1mm de erro = -5 pts

  Score do Período = (score_classe * 0.60) + (score_mm * 0.40)

  Score do Dia = média PONDERADA (madrugada pesa 0.5; demais, 1.0).
"""

from scripts.utils.classificacao import classificar_chuva


# ---------------------------------------------------------------------------
# MATRIZ DE CLASSIFICAÇÃO (previsto → real)
# ---------------------------------------------------------------------------
# Linha = classe que o modelo PREVIU
# Coluna = classe que realmente aconteceu
# Valor = pontuação 0-100 daquele acerto/erro
#
# Classes: seco, garoa, moderada, forte, intensa
# (nomes unificados — idênticos aos do Supabase/Frontend)
MATRIZ_CLASSE = {
    "seco":     {"seco": 100, "garoa": 75,  "moderada": 30,  "forte": 0,   "intensa": 0},
    "garoa":    {"seco": 75,  "garoa": 100, "moderada": 80,  "forte": 40,  "intensa": 20},
    "moderada": {"seco": 30,  "garoa": 80,  "moderada": 100, "forte": 75,  "intensa": 50},
    "forte":    {"seco": 0,   "garoa": 40,  "moderada": 75,  "forte": 100, "intensa": 80},
    "intensa":  {"seco": 0,   "garoa": 20,  "moderada": 50,  "forte": 80,  "intensa": 100},
}


PESOS_PERIODO = {
    "madrugada": 0.5,  # Menos relevante para decisões de dia-a-dia
    "manha":     1.0,
    "tarde":     1.0,
    "noite":     1.0,
}


def calcular_score_periodo(prev_mm, real_mm):
    """
    Score 0-100 de um período específico (6 horas).
    Composto por:
      60% acerto de classe (matriz 5x5)
      40% proximidade de volume (-5 pts por mm de erro)
    """
    if prev_mm is None or real_mm is None:
        return 0.0

    prev_class = classificar_chuva(prev_mm)
    real_class = classificar_chuva(real_mm)

    # --- Fator 1: classe (60%) ---
    # Se alguma classe cair fora da matriz (ex: "sem_dados"), pontua 0.
    score_classe = MATRIZ_CLASSE.get(prev_class, {}).get(real_class, 0)

    # --- Fator 2: volume (40%) ---
    dif = abs(prev_mm - real_mm)
    score_volume = max(0, 100 - (dif * 5))  # ARCHITECTURE.md: 5 pts por mm

    final = (score_classe * 0.60) + (score_volume * 0.40)
    return round(final, 1)


def calcular_score_dia(prev_periodos, real_periodos):
    """
    Score diário = média PONDERADA dos 4 períodos.
    Madrugada pesa 0.5, demais períodos pesam 1.0.

    Args:
        prev_periodos: {'madrugada': mm, 'manha': mm, 'tarde': mm, 'noite': mm}
        real_periodos: idem
    Returns:
        float 0-100, arredondado a 1 casa
    """
    soma_ponderada = 0.0
    soma_pesos = 0.0
    for p in ("madrugada", "manha", "tarde", "noite"):
        p_prev = prev_periodos.get(p, 0) or 0
        p_real = real_periodos.get(p, 0) or 0
        score = calcular_score_periodo(p_prev, p_real)
        peso = PESOS_PERIODO.get(p, 1.0)
        soma_ponderada += score * peso
        soma_pesos += peso

    if soma_pesos == 0:
        return 0.0
    return round(soma_ponderada / soma_pesos, 1)
