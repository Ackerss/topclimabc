"""
TOPCLIMABC — 01_coletar_previsoes.py
====================================
Coleta as previsões do dia atual para os próximos 16 dias.
Usa Open-Meteo (ECMWF, ICON, GFS, Best Match) e OpenWeatherMap.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from scripts.config import (
    LOCAIS, MODELOS, PERIODOS, PREVISOES_DIR, 
    OPEN_METEO_BASE, OWM_BASE, OWM_API_KEY
)

load_dotenv()

def get_periodo(hora_int):
    """Retorna a chave do período (madrugada, manha, etc) baseada na hora."""
    for p_id, p_info in PERIODOS.items():
        if hora_int in p_info["horas"]:
            return p_id
    return None

def coletar_open_meteo(local_id):
    """Coleta múltiplos modelos do Open-Meteo em uma única chamada."""
    local = LOCAIS[local_id]
    modelos_om = [m["open_meteo_id"] for m in MODELOS.values() if m["open_meteo_id"]]
    
    params = {
        "latitude": local["lat"],
        "longitude": local["lon"],
        "hourly": "precipitation",
        "models": ",".join(modelos_om),
        "timezone": "America/Sao_Paulo",
        "forecast_days": 16
    }
    
    try:
        response = requests.get(OPEN_METEO_BASE, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao coletar Open-Meteo para {local_id}: {e}")
        return None

def coletar_owm(local_id):
    """Coleta previsão do OpenWeatherMap (5 dias / 3 horas)."""
    local = LOCAIS[local_id]
    params = {
        "lat": local["lat"],
        "lon": local["lon"],
        "appid": OWM_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(f"{OWM_BASE}/forecast", params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao coletar OWM para {local_id}: {e}")
        return None

def processar_dados_om(dados_om):
    """Organiza os dados do Open-Meteo por data, modelo e período."""
    if not dados_om: return {}
    
    processado = {} # { 'YYYY-MM-DD': { 'modelo': { 'periodo': mm } } }
    hourly = dados_om.get("hourly", {})
    tempos = hourly.get("time", [])
    
    # Identifica quais colunas pertencem a quais modelos
    # O Open-Meteo retorna precipitation_modelo_id
    for m_id, m_info in MODELOS.items():
        om_id = m_info["open_meteo_id"]
        if not om_id: continue
        
        col_name = f"precipitation_{om_id}"
        if om_id == "best_match": col_name = "precipitation"
        
        chuvas = hourly.get(col_name, [])
        
        for i, t_str in enumerate(tempos):
            dt = datetime.fromisoformat(t_str)
            data_iso = dt.date().isoformat()
            periodo = get_periodo(dt.hour)
            v = chuvas[i] if i < len(chuvas) else 0.0
            mm = v if v is not None else 0.0
            
            if data_iso not in processado: processado[data_iso] = {}
            if m_id not in processado[data_iso]: 
                processado[data_iso][m_id] = {p: 0.0 for p in PERIODOS}
            
            if periodo:
                processado[data_iso][m_id][periodo] += mm

    return processado

def processar_dados_owm(dados_owm):
    """Organiza os dados do OWM (3h) por data e período."""
    if not dados_owm: return {}
    
    processado = {}
    for item in dados_owm.get("list", []):
        dt = datetime.fromtimestamp(item["dt"])
        data_iso = dt.date().isoformat()
        periodo = get_periodo(dt.hour)
        # OWM retorna 'rain' se houver chuva nos últimos 3h
        mm = item.get("rain", {}).get("3h", 0)
        
        if data_iso not in processado: processado[data_iso] = {}
        if "openweathermap" not in processado[data_iso]:
            processado[data_iso]["openweathermap"] = {p: 0.0 for p in PERIODOS}
        
        if periodo:
            # Como a leitura é 3h, distribuímos nos períodos correspondentes
            processado[data_iso]["openweathermap"][periodo] += mm
            
    return processado

def main():
    print(f"--- Início da coleta de previsões: {datetime.now()} ---")
    data_hoje = datetime.now().date().isoformat()
    snapshot = {
        "data_coleta": data_hoje,
        "locais": {}
    }
    
    for local_id in LOCAIS:
        print(f"Coletando para {local_id}...")
        
        # Coleta
        raw_om = coletar_open_meteo(local_id)
        raw_owm = coletar_owm(local_id)
        
        # Processamento
        om_proc = processar_dados_om(raw_om)
        owm_proc = processar_dados_owm(raw_owm)
        
        # Merge
        result = om_proc
        for data_iso, mod_dados in owm_proc.items():
            if data_iso not in result: result[data_iso] = {}
            result[data_iso].update(mod_dados)
            
        snapshot["locais"][local_id] = result

    # Salva o arquivo de snapshot
    caminho = PREVISOES_DIR / f"snapshot_{data_hoje}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
    print(f"Snapshot salvo em: {caminho}")
    print("--- Fim da coleta ---")

if __name__ == "__main__":
    main()
