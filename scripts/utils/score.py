"""
TOPCLIMABC — utils/score.py
===========================
Algoritmo de auditoria de acerto (0 a 100%).
Compara o previsto (forecast) com o real (CEMADEN/Open-Meteo Hist).
"""

from scripts.utils.classificacao import classificar_chuva

def calcular_score_periodo(prev_mm, real_mm):
    """
    Calcula o score de um período específico (ex: Tarde).
    Retorna um valor de 0 a 100.
    """
    if prev_mm is None or real_mm is None:
        return 0

    prev_class = classificar_chuva(prev_mm)
    real_class = classificar_chuva(real_mm)

    # 1. Acerto de Classe (Peso 60%)
    score_classe = 0
    if prev_class == real_class:
        score_classe = 100
    elif (prev_class == "sem_chuva" and real_class == "fraca") or (prev_class == "fraca" and real_class == "sem_chuva"):
        score_classe = 50 # Erro leve (quase acertou)
    
    # 2. Proximidade de Volume (Peso 40%)
    # Diferença absoluta. Se a diferença for > 10mm em 6h, o score de volume é zero.
    dif = abs(prev_mm - real_mm)
    score_volume = max(0, 100 - (dif * 10)) # Cada 1mm de diferença tira 10 pontos

    final = (score_classe * 0.6) + (score_volume * 0.4)
    return round(final, 1)

def calcular_score_dia(prev_periodos, real_periodos):
    """
    prev_periodos: {'madrugada': mm, 'manha': mm, ...}
    real_periodos: {'madrugada': mm, 'manha': mm, ...}
    Retorna uma média ponderada ou simples dos acertos.
    """
    scores = []
    for p in ['madrugada', 'manha', 'tarde', 'noite']:
        p_prev = prev_periodos.get(p, 0)
        p_real = real_periodos.get(p, 0)
        scores.append(calcular_score_periodo(p_prev, p_real))
    
    # Média simples dos 4 períodos
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 1)
