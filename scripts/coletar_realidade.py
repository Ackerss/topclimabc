"""
TOPCLIMABC — coletar_realidade.py
==================================
Coleta os dados reais de precipitação (juiz oficial do sistema).

HIERARQUIA DE FONTES (atualizado 2026-04-18, sprint de correções):

1. CEMADEN PED API  ← FONTE PRIMÁRIA (pluviômetros físicos)
   URL: sws.cemaden.gov.br/PED/rest
   Consolida mediana das estações de BC/Itajaí por período.
   Status: "completo" — é o dado mais fidedigno possível.

2. Open-Meteo Archive (best_match) — FALLBACK
   URL: archive-api.open-meteo.com
   Usa ERA5-Land (~9km) + obs. locais. Disponível com 2-5 dias de atraso.
   Status: "provisorio_reanalise" — reanálise, não medição direta.

3. Open-Meteo Historical Forecast — FALLBACK de último recurso
   URL: historical-forecast-api.open-meteo.com
   Status: "provisorio" — previsão recalculada, não medição.

4. sem_dados — Se todas as APIs falharem.
   NUNCA inserir 0mm sem confirmação explícita.

IMPORTANTE para IAs futuras:
- Prioridade ABSOLUTA ao override manual (Supabase → tabela topclimabc_validacoes).
- Os overrides sobrescrevem qualquer fonte automática por período.
- O total diário é recalculado após aplicar overrides.
"""

import json
import requests
from datetime import datetime, timedelta
from scripts.config import (
    LOCAIS, PERIODOS, REALIDADE_DIR,
    OPEN_METEO_ARCHIVE, OPEN_METEO_HIST, OM_ARCHIVE_MODEL
)
from scripts.utils.classificacao import classificar_chuva
from scripts.utils.supabase_api import buscar_overrides_manuais
from scripts.utils.cemaden import obter_realidade_municipio as cemaden_obter


def get_periodo(hora_int):
    for p_id, p_info in PERIODOS.items():
        if hora_int in p_info["horas"]:
            return p_id
    return None


def coletar_archive_best_match(local_id, data_iso):
    """
    Coleta precipitação do Open-Meteo Archive com modelo best_match.
    Busca AMBOS: total diário E dados horários — mesma fonte, sem inconsistência.

    Retorna: (total_mm: float|None, horarios: list[float]|None)
    - total_mm: total do dia em mm
    - horarios: lista de 24 valores (hora 0..23) em mm
    """
    local = LOCAIS[local_id]
    params = {
        "latitude": local["lat"],
        "longitude": local["lon"],
        "start_date": data_iso,
        "end_date": data_iso,
        "daily": "precipitation_sum",
        "hourly": "precipitation",
        "models": OM_ARCHIVE_MODEL,
        "timezone": "America/Sao_Paulo"
    }
    try:
        response = requests.get(OPEN_METEO_ARCHIVE, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        # Total diário
        daily = data.get("daily", {})
        totais = daily.get("precipitation_sum", [])
        total_mm = round(float(totais[0]), 1) if totais and totais[0] is not None else None

        # Dados horários (24 horas)
        hourly = data.get("hourly", {})
        chuvas_hora = hourly.get("precipitation", [])
        if chuvas_hora and any(v is not None for v in chuvas_hora):
            horarios = [float(v) if v is not None else 0.0 for v in chuvas_hora[:24]]
        else:
            horarios = None

        if total_mm is None and horarios is None:
            return None, None

        return total_mm, horarios

    except Exception as e:
        print(f"  [Archive best_match] Falhou para {local_id} em {data_iso}: {e}")
        return None, None


def coletar_hist_forecast_fallback(local_id, data_iso):
    """
    Fallback: Open-Meteo Historical Forecast (sem modelo best_match — apenas previsão recalculada).
    Usado apenas quando Archive ainda não tem dados (datas muito recentes, < 2 dias).

    Retorna: (total_mm: float|None, horarios: list[float]|None)
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
        data = response.json()

        hourly = data.get("hourly", {})
        chuvas_hora = hourly.get("precipitation", [])
        if not chuvas_hora or all(v is None for v in chuvas_hora):
            return None, None

        horarios = [float(v) if v is not None else 0.0 for v in chuvas_hora[:24]]
        total_mm = round(sum(horarios), 1)
        return total_mm, horarios

    except Exception as e:
        print(f"  [Hist Forecast] Falhou para {local_id} em {data_iso}: {e}")
        return None, None


def distribuir_por_periodos(total_mm, horarios):
    """
    Distribui a precipitação total por período (madrugada/manhã/tarde/noite)
    usando os 24 valores horários.

    - Se horarios disponíveis: usa proporção dos horários para distribuir o total.
    - Se horarios indisponíveis mas total > 0: divide igualmente pelos 4 períodos.
    - Se total = 0: todos os períodos ficam 0.
    """
    periodos_result = {p: 0.0 for p in PERIODOS}

    if horarios:
        # Distribui proporcionalmente ao padrão horário
        total_horario = sum(horarios)

        if total_horario > 0 and total_mm is not None and total_mm > 0:
            # Normaliza para bater com o total oficial
            fator = total_mm / total_horario
            for i, mm in enumerate(horarios):
                periodo = get_periodo(i)
                if periodo:
                    periodos_result[periodo] += round(mm * fator, 2)
        elif total_mm is not None and total_mm > 0 and total_horario == 0:
            # Total diz que choveu mas horários dizem 0 — distribui igualmente
            por_periodo = round(total_mm / len(PERIODOS), 1)
            for p in periodos_result:
                periodos_result[p] = por_periodo
        else:
            # total = 0 ou None — distribui direto dos horários sem normalizar
            for i, mm in enumerate(horarios):
                periodo = get_periodo(i)
                if periodo:
                    periodos_result[periodo] += mm

    elif total_mm and total_mm > 0:
        # Sem horários, com total — distribui igualmente
        por_periodo = round(total_mm / len(PERIODOS), 1)
        for p in periodos_result:
            periodos_result[p] = por_periodo

    # Arredonda tudo para 1 decimal
    for p in periodos_result:
        periodos_result[p] = round(periodos_result[p], 1)

    return periodos_result


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


def criar_realidade_sem_dados(motivo=""):
    """Retorna estrutura marcada como sem_dados. NUNCA usar como equivalente a 0mm."""
    return {
        "status": "sem_dados",
        "fonte": f"Nenhuma fonte disponível{' — ' + motivo if motivo else ''}",
        "periodos": {
            p: {"mm": None, "classificacao": "sem_dados"}
            for p in PERIODOS
        },
        "total_dia": None
    }


def coletar_e_salvar(local_id, data_iso):
    """Coleta e salva a realidade para um local e data específicos.
    Hierarquia: CEMADEN → Open-Meteo Archive → Open-Meteo Hist Forecast → sem_dados.
    """
    print(f"  Coletando realidade de {data_iso} para {local_id}...")
    local_cfg = LOCAIS[local_id]
    ibge = local_cfg.get("ibge")
    realidade = None

    # 1. FONTE PRIMÁRIA: CEMADEN (pluviômetro físico)
    if ibge:
        try:
            dados_cem = cemaden_obter(ibge, data_iso)
        except Exception as e:
            print(f"    [CEMADEN] Erro inesperado: {e}")
            dados_cem = None
        if dados_cem and dados_cem.get("periodos"):
            realidade = montar_realidade(
                dados_cem["periodos"],
                dados_cem["total_dia"],
                dados_cem["fonte"],
                "completo"
            )
            realidade["estacoes_cemaden"] = dados_cem.get("estacoes_usadas", [])
            print(f"    [OK] CEMADEN: {dados_cem['total_dia']}mm | estações={len(dados_cem.get('estacoes_usadas', []))}")

    # 2. FALLBACK: Open-Meteo Archive (reanálise)
    if realidade is None:
        total_archive, horarios_archive = coletar_archive_best_match(local_id, data_iso)
        if total_archive is not None:
            periodos_mm = distribuir_por_periodos(total_archive, horarios_archive)
            fonte = f"Open-Meteo Archive (best_match, reanálise) — {data_iso}"
            realidade = montar_realidade(periodos_mm, total_archive, fonte, "provisorio_reanalise")
            print(f"    [FALLBACK] Archive best_match: {total_archive}mm | reanálise (CEMADEN indisponível)")

    # 3. FALLBACK 2: Historical Forecast
    if realidade is None:
        print(f"    Archive indisponivel, tentando Historical Forecast...")
        total_hist, horarios_hist = coletar_hist_forecast_fallback(local_id, data_iso)
        if total_hist is not None:
            periodos_mm = distribuir_por_periodos(total_hist, horarios_hist)
            fonte = "Open-Meteo Historical Forecast (provisorio — previsão recalculada)"
            realidade = montar_realidade(periodos_mm, total_hist, fonte, "provisorio")
            print(f"    [PROV] Hist Forecast: {total_hist}mm | Status: provisorio")

    # 4. Sem dados
    if realidade is None:
        print(f"    [ERRO] Sem dados de realidade para {local_id} em {data_iso}")
        realidade = criar_realidade_sem_dados(motivo="CEMADEN, Archive e Hist Forecast falharam")

    # --- Aplica overrides manuais (prioridade absoluta) ---
    overrides = buscar_overrides_manuais(data_iso)
    override_local = overrides.get(local_id, {})
    if override_local:
        for periodo, override_data in override_local.items():
            realidade["periodos"][periodo] = {
                "mm": override_data["mm"],
                "classificacao": override_data["classificacao"],
                "fonte_periodo": "manual",
                "override": True,
                "nota": override_data.get("nota"),
            }
        # Recalcula total_dia após sobrescrever períodos
        realidade["total_dia"] = round(
            sum(v.get("mm", 0) for v in realidade["periodos"].values() if v.get("mm") is not None), 1
        )
        # Marca o status do dia como contendo dado manual
        realidade["tem_override_manual"] = True
        print(f"  [Override] {len(override_local)} período(s) sobrescrito(s) manualmente para {local_id}/{data_iso}.")

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
    print(f"--- Inicio da coleta de realidade: {datetime.now()} ---")
    ontem = (datetime.now() - timedelta(days=1)).date().isoformat()
    print(f"Data alvo: {ontem}")

    for local_id in LOCAIS:
        coletar_e_salvar(local_id, ontem)

    print("--- Fim da coleta de realidade ---")


if __name__ == "__main__":
    main()
