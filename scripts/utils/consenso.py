"""
TOPCLIMABC — utils/consenso.py
==============================
Lógica para calcular a mediana entre múltiplas estações de um mesmo município.
Evita que uma estação com defeito (leitura errada) estrague a média.
"""

import statistics

def calcular_consenso(lista_valores):
    """
    Recebe uma lista de milímetros [1.2, 0.0, 10.5, 1.1]
    Retorna a mediana.
    """
    # Filtra valores None
    valores = [v for v in lista_valores if v is not None]
    
    if not valores:
        return 0.0
    
    # Mediana é mais robusta que média para pluviômetros
    return round(statistics.median(valores), 1)

def calcular_consenso_periodos(lista_periodos_estacoes):
    """
    Recebe uma lista de dicionários de períodos de várias estações.
    Ex: [ {'manha': 2, 'tarde': 0}, {'manha': 2.2, 'tarde': 0.1} ]
    Retorna um dicionário com o consenso por período.
    """
    periodos = ['madrugada', 'manha', 'tarde', 'noite']
    consenso = {}
    
    for p in periodos:
        valores = [e.get(p) for e in lista_periodos_estacoes if p in e]
        consenso[p] = calcular_consenso(valores)
        
    return consenso
