"""
TOPCLIMABC — coletar_realidade.py
==================================
Coleta os dados reais de precipitação do dia de ontem (juiz oficial).

HIERARQUIA DE FONTES (ordem de prioridade):
1. ERA5 Archive (archive-api.open-meteo.com) — reanálise ECMWF definitiva.
   Disponível com 2-5 dias de delay. Para datas > 5 dias: 100% confiável.
2. Open-Meteo Historical Forecast (historical-forecast-api) — fallback provisório.
   Mais rápido, mas menos definitivo (dados de previsão recalculada, não ERA5 puro).
3. sem_dados — Se ambas as APIs falharem, marca como sem_dados.
   NUNCA inserir 0mm sem confirmação explícita da API.

IMPORTANTE para IAs futuras:
- O total ERA5 é usado como "verdade" do dia.
- Os dados horários do hist_forecast são usados APENAS para distribuir por período.
- Se o hist_forecast também falhar, distribui o total ERA5 uniformemente.
- O status "sem_dados" deve ser exibido como "Dados não disponíveis" no frontend.
"""

import json
import requests
from datetime import datetime, timedelta
from scripts.config import (
    LOCAIS, PERIODOS, REALIDADE_DIR,
    OPEN_METEO_ARCHIVE, OPEN_METEO_HIST
)
from scripts.utils.classificacao import classificar_chuva


def get_periodo(hora_int):
    for p_id, p_info in PERIODOS.items():
        if hora_int in p_info["horas"]:
            return p_id
    return None


def coletar_era5_archive(local_id, data_iso):
    """
    Coleta precipitação do ERA5 Archive (fonte primária definitiva).
    Retorna o total em mm do dia (float) ou None se não disponível.
    A API retorna daily.precipitation_sum diretamente — 1 valor por dia.
    """
    local = LOCAIS[local_id]
    params = {
        "latitude": local["lat"],
        "longitude": local["lon"],
        "start_date": data_iso,
        "end_date": data_iso,
        "daily": "precipitation_sum",
        "timezone": "America/Sao_Paulo"
    }
    try:
        response = requests.get(OPEN_METEO_ARCHIVE, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        daily = data.get("daily", {})
        valores = daily.get("precipitation_sum", [])
        if not valores or valores[0] is None:
            return None
        return round(float(valores[0]), 1)
    except Exception as e:
        print(f"  [ERA5 Archive] Falhou para {local_id} em {data_iso}: {e}")
        return None


def coletar_om_hist_forecast(local_id, data_iso):
    """
    Fallback: dados horários da historical-forecast API.
    Retorna o JSON bruto da API ou None se falhar.
    """
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
        print(f"  [OM Hist Forecast] Falhou para {local_id} em {data_iso}: {e}")
        return None


def calcular_periodos_horarios(raw_om, total_era5=None):
    """
    Distribui a precipitação por período (madrugada/manhã/tarde/noite)
    usando os dados horários do Open-Meteo Hist Forecast.

    Se total_era5 for fornecido, normaliza os valores para bater com o total ERA5
    (ERA5 é o total oficial, os horários definem a distribuição).

    Retorna: dict com periodos e total_dia.
    """
    periodos_result = {p: 0.0 for p in PERIODOS}

    if raw_om:
        hourly = raw_om.get("hourly", {})
        chuvas = hourly.get("precipitation", [])
        tempos = hourly.get("time", [])

        total_hist = 0.0
        for i, t_str in enumerate(tempos):
            mm = chuvas[i] if i < len(chuvas) and chuvas[i] is not None else 0.0
            dt = datetime.fromisoformat(t_str)
            periodo = get_periodo(dt.hour)
            if periodo:
                periodos_result[periodo] += mm
            total_hist += mm

        # Normaliza para o total ERA5 se disponível e os horários têm alguma chuva
        if total_era5 is not None and total_hist > 0:
            fator = total_era5 / total_hist
            for p in periodos_result:
                periodos_result[p] = round(periodos_result[p] * fator, 1)
            total_dia = total_era5
        elif total_era5 is not None:
            # hist_forecast diz 0mm mas ERA5 diz outro valor — usa ERA5 como total
            # Distribui uniformemente (se ERA5 também for 0, tudo fica 0)
            for p in periodos_result:
                periodos_result[p] = round(total_era5 / len(PERIODOS), 1) if total_era5 > 0 else 0.0
            total_dia = total_era5
        else:
            # Apenas hist_forecast disponível
            total_dia = round(sum(periodos_result.values()), 1)
            for p in periodos_result:
                periodos_result[p] = round(periodos_result[p], 1)
    elif total_era5 is not None:
        # Sem dados horários — distribui ERA5 uniformemente só se > 0
        por_periodo = round(total_era5 / len(PERIODOS), 1) if total_era5 > 0 else 0.0
        for p in periodos_result:
            periodos_result[p] = por_periodo
        total_dia = total_era5
    else:
        total_dia = None

    return periodos_result, total_dia


def criar_realidade_sem_dados():
    """Retorna estrutura de realidade marcada como sem_dados. NUNCA usar como 0mm."""
    return {
        "status": "sem_dados",
        "fonte": "Nenhuma fonte disponível",
        "periodos": {
            p: {"mm": None, "classificacao": "sem_dados"}
            for p in PERIODOS
        },
        "total_dia": None
    }


def montar_realidade(periodos_mm, total_dia, fonte, status):
    """Monta o dict final de realidade com classificações por período."""
    periodos_final = {}
    for p, mm in periodos_mm.items():
        periodos_final[p] = {
            "mm": mm,
            "classificacao": classificar_chuva(mm) if mm is not None else "sem_dados"
        }
    return {
        "status": status,
        "fonte": fonte,
        "periodos": periodos_final,
        "total_dia": total_dia
    }


def coletar_e_salvar(local_id, data_iso):
    """Coleta e salva a realidade para um local e data específicos."""
    print(f"  Coletando realidade de {data_iso} para {local_id}...")

    # 1. Tenta ERA5 Archive (fonte definitiva)
    mm_era5 = coletar_era5_archive(local_id, data_iso)

    # 2. Tenta hist_forecast para dados horários (distribuição por período)
    raw_horario = coletar_om_hist_forecast(local_id, data_iso)

    if mm_era5 is not None:
        # ERA5 disponível: usa ERA5 como total oficial, hist para distribuição
        periodos_mm, total_dia = calcular_periodos_horarios(raw_horario, mm_era5)
        if raw_horario:
            fonte = "ERA5 Archive (ECMWF) + Open-Meteo Historical (distribuição horária)"
        else:
            fonte = "ERA5 Archive (ECMWF) — distribuição estimada por período"
        status = "completo"
        realidade = montar_realidade(periodos_mm, total_dia, fonte, status)
    elif raw_horario:
        # ERA5 ainda não disponível (< 5 dias) — usa hist_forecast como provisório
        periodos_mm, total_dia = calcular_periodos_horarios(raw_horario)
        fonte = "Open-Meteo Historical Forecast (provisório — ERA5 ainda processando)"
        status = "provisorio"
        realidade = montar_realidade(periodos_mm, total_dia, fonte, status)
    else:
        # Nenhuma fonte respondeu
        print(f"  ⚠️  ATENÇÃO: Sem dados de realidade para {local_id} em {data_iso}. Marcando como sem_dados.")
        realidade = criar_realidade_sem_dados()
        realidade["fonte"] = "Falha em ambas as APIs (ERA5 Archive e Open-Meteo Historical)"

    # Salva no arquivo diário
    caminho = REALIDADE_DIR / f"realidade_{data_iso}.json"
    dados_arquivo = {}
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            dados_arquivo = json.load(f)
    dados_arquivo[local_id] = realidade
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados_arquivo, f, indent=2, ensure_ascii=False)

    return realidade


def main():
    print(f"--- Início da coleta de realidade: {datetime.now()} ---")
    ontem = (datetime.now() - timedelta(days=1)).date().isoformat()
    print(f"Data alvo: {ontem}")

    for local_id in LOCAIS:
        coletar_e_salvar(local_id, ontem)

    print("--- Fim da coleta de realidade ---")


if __name__ == "__main__":
    main()
