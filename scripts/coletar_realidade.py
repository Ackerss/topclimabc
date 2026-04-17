"""
TOPCLIMABC — 02_coletar_realidade.py
====================================
Coleta os dados reais do dia de ontem (juiz oficial) e dados parciais de hoje.
Usa Open-Meteo Historical como fonte primária.
"""

import json
import requests
from datetime import datetime, timedelta
from scripts.config import (
    LOCAIS, PERIODOS, REALIDADE_DIR, OPEN_METEO_HIST,
    FONTE_REALIDADE_PRIMARIA
)

def get_periodo(hora_int):
    for p_id, p_info in PERIODOS.items():
        if hora_int in p_info["horas"]:
            return p_id
    return None

def coletar_om_historical(local_id, data_iso):
    """Coleta precipitação histórica do Open-Meteo."""
    local = LOCAIS[local_id]
    params = {
        "latitude": local["lat"],
        "longitude": local["lon"],
        "start_date": data_iso,
        "end_date": data_iso,
        "hourly": "precipitation",
        "timezone": "America/Sao_Paulo"
    }
    
    try:
        response = requests.get(OPEN_METEO_HIST, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao coletar Open-Meteo Hist para {local_id} em {data_iso}: {e}")
        return None

def processar_realidade(raw_om, data_iso):
    """Calcula acumulados por período e total do dia."""
    if not raw_om: return None
    
    hourly = raw_om.get("hourly", {})
    chuvas = hourly.get("precipitation", [])
    tempos = hourly.get("time", [])
    
    res = {
        "status": "completo",
        "fonte": "Open-Meteo Historical (Reanálise)",
        "periodos": {p: {"mm": 0.0, "classificacao": ""} for p in PERIODOS},
        "total_dia": 0.0
    }
    
    from scripts.utils.classificacao import classificar_chuva

    total = 0.0
    for i, t_str in enumerate(tempos):
        mm = chuvas[i] if i < len(chuvas) and chuvas[i] is not None else 0.0
        dt = datetime.fromisoformat(t_str)
        periodo = get_periodo(dt.hour)
        
        if periodo:
            res["periodos"][periodo]["mm"] += mm
        total += mm
    
    res["total_dia"] = round(total, 1)
    
    # Classifica cada período
    for p in res["periodos"]:
        res["periodos"][p]["mm"] = round(res["periodos"][p]["mm"], 1)
        res["periodos"][p]["classificacao"] = classificar_chuva(res["periodos"][p]["mm"])
        
    return res

def main():
    print(f"--- Início da coleta de realidade: {datetime.now()} ---")
    
    # Vamos coletar para ontém (auditoria final)
    ontem = (datetime.now() - timedelta(days=1)).date().isoformat()
    
    # Estrutura de saída por data
    # data_snap = { 'local_id': { realidade_data } }
    
    for local_id in LOCAIS:
        print(f"Coletando realidade de {ontem} para {local_id}...")
        raw = coletar_om_historical(local_id, ontem)
        realidade = processar_realidade(raw, ontem)
        
        if realidade:
            # Salva em arquivo individual por data
            # Para facilitar, salvamos no formato que o frontend espera no final
            caminho = REALIDADE_DIR / f"realidade_{ontem}.json"
            
            # Carrega arquivo existente ou cria novo
            dados_arquivo = {}
            if caminho.exists():
                with open(caminho, "r", encoding="utf-8") as f:
                    dados_arquivo = json.load(f)
            
            dados_arquivo[local_id] = realidade
            
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(dados_arquivo, f, indent=2, ensure_ascii=False)
                
    print("--- Fim da coleta de realidade ---")

if __name__ == "__main__":
    main()
