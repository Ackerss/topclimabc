"""
TOPCLIMABC — auditar.py
==========================
O "Cérebro" auditor.
Compara as previsões feitas no passado com a realidade medida.
Gera os scores de acerto e atualiza o histórico.

LÓGICA RETROATIVA (importante para IAs futuras):
- Varre TODOS os snapshots disponíveis (não apenas "ontem").
- Para cada snapshot, verifica todos os dias que ele cobre.
- Se houver arquivo de realidade disponível para esse dia → audita.
- O prazo é calculado como (data_alvo - data_coleta_do_snapshot).
- Prazos aceitos: 1, 2, 3, 4, 5, 6, 7, 14, 15 dias.
- Isso permite acumular histórico mesmo com poucos snapshots.

SOBRE REALIDADE:
- Só audita se o status da realidade for "completo" ou "provisorio".
- Se status for "sem_dados", pula (não gera score com dado inexistente).
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from scripts.config import (
    LOCAIS, MODELOS, PRAZOS, PRAZO_DIAS, AUDITORIA_DIR,
    PREVISOES_DIR, REALIDADE_DIR
)
from scripts.utils.score import calcular_score_dia
from scripts.utils.supabase_api import buscar_tombstones


def carregar_arquivo(caminho):
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def aplicar_tombstones_na_realidade(realidade_data, data_alvo_str, tombstones_por_data):
    """
    Modifica realidade_data IN-PLACE removendo periodos marcados como tombstone
    (soft-delete) no Supabase. Assim auditoria nao usa valor manual que o usuario
    apagou depois, mesmo que o arquivo realidade_{data}.json ainda tenha o dado.
    """
    if not realidade_data:
        return realidade_data
    tomb_data = tombstones_por_data.get(data_alvo_str) or {}
    if not tomb_data:
        return realidade_data
    for local_id, periodos_apagados in tomb_data.items():
        if local_id not in realidade_data:
            continue
        periodos = realidade_data[local_id].get("periodos") or {}
        for p in list(periodos_apagados):
            if p in periodos and periodos[p].get("fonte_periodo") == "manual":
                del periodos[p]
    return realidade_data


def mapear_prazo(dias_diff):
    """
    Converte diferença de dias em ID de prazo.
    Aceita prazos fixos (1, 3, 7, 15) e prazos próximos com tolerância de ±0.
    """
    if dias_diff == 1:  return "1_dia"
    if dias_diff == 3:  return "3_dias"
    if dias_diff == 7:  return "7_dias"
    if dias_diff == 15: return "15_dias"
    return None  # Prazo não mapeado a um dos 4 fixos — ignora


def main():
    print(f"--- Início da Auditoria (Retroativa): {datetime.now()} ---")

    # Carrega histórico de auditoria existente
    caminho_hist = AUDITORIA_DIR / "historico.json"
    historico = carregar_arquivo(caminho_hist) or {}

    # Garante estrutura base para todos os locais
    for local_id in LOCAIS:
        if local_id not in historico:
            historico[local_id] = {}

    # Pre-busca todos os tombstones do Supabase uma unica vez.
    # Tombstones = periodos manuais que o usuario apagou via frontend e que podem
    # ter ficado "gravados" em arquivos realidade_{data}.json antigos.
    try:
        tombstones_por_data = buscar_tombstones(data_iso=None)
        total_tomb = sum(sum(len(p) for p in locs.values()) for locs in tombstones_por_data.values())
        if total_tomb:
            print(f"  [Tombstones] {total_tomb} periodo(s) apagado(s) via soft-delete serao respeitados.")
    except Exception as e:
        print(f"  [Tombstones] Falha ao buscar: {e}. Seguindo sem.")
        tombstones_por_data = {}

    # Varre TODOS os snapshots disponíveis
    snapshots = sorted(PREVISOES_DIR.glob("snapshot_*.json"))
    if not snapshots:
        print("Nenhum snapshot encontrado. Abortando.")
        return

    total_auditorias = 0

    for snap_path in snapshots:
        data_coleta_str = snap_path.stem.replace("snapshot_", "")
        snapshot = carregar_arquivo(snap_path)
        if not snapshot:
            continue

        print(f"\nProcessando snapshot de {data_coleta_str}...")

        locais_snap = snapshot.get("locais", {})

        for local_id in LOCAIS:
            if local_id not in locais_snap:
                continue

            datas_previstas = locais_snap[local_id]  # { 'YYYY-MM-DD': { 'modelo': {periodos} } }

            for data_alvo_str, forecast_alvo in datas_previstas.items():
                if not forecast_alvo:
                    continue

                # Calcula o prazo em dias
                try:
                    dt_coleta = datetime.fromisoformat(data_coleta_str)
                    dt_alvo = datetime.fromisoformat(data_alvo_str)
                    dias_diff = (dt_alvo - dt_coleta).days
                except ValueError:
                    continue

                prazo_id = mapear_prazo(dias_diff)
                if not prazo_id:
                    continue  # Prazo não é um dos 4 alvos — pula

                # Verifica se há realidade disponível para este dia
                caminho_real = REALIDADE_DIR / f"realidade_{data_alvo_str}.json"
                realidade_data = carregar_arquivo(caminho_real)
                if not realidade_data or local_id not in realidade_data:
                    continue

                # Respeita tombstones: remove periodos manuais apagados via frontend.
                realidade_data = aplicar_tombstones_na_realidade(
                    realidade_data, data_alvo_str, tombstones_por_data
                )

                real_local = realidade_data[local_id]

                # ⚠️ Só audita se o status for confiável (não sem_dados)
                status_real = real_local.get("status", "sem_dados")
                if status_real == "sem_dados":
                    print(f"  Pulando {local_id}/{data_alvo_str}: realidade marcada como sem_dados")
                    continue

                # Extrai mm por período da realidade
                real_periodos_raw = real_local.get("periodos", {})
                real_periodos = {}
                for p, info in real_periodos_raw.items():
                    mm = info.get("mm")
                    if mm is None:
                        real_periodos[p] = 0.0  # sem_dados de período individual → 0 para score
                    else:
                        real_periodos[p] = mm

                # Garante estrutura no histórico
                if data_alvo_str not in historico[local_id]:
                    historico[local_id][data_alvo_str] = {}
                if prazo_id not in historico[local_id][data_alvo_str]:
                    historico[local_id][data_alvo_str][prazo_id] = {}

                # Calcula score para cada modelo
                for m_id in MODELOS:
                    # Persistência: não vem do snapshot, é construída a partir da
                    # REALIDADE de D-1. "Amanhã = hoje" → se o modelo não bate
                    # essa baseline trivial, é inútil.
                    if MODELOS[m_id].get("is_baseline") and m_id == "persistencia":
                        dt_baseline = dt_alvo - timedelta(days=1)
                        data_base_str = dt_baseline.date().isoformat()
                        cam_base = REALIDADE_DIR / f"realidade_{data_base_str}.json"
                        base_json = carregar_arquivo(cam_base)
                        if not base_json or local_id not in base_json:
                            continue
                        base_json = aplicar_tombstones_na_realidade(
                            base_json, data_base_str, tombstones_por_data
                        )
                        base_per = base_json[local_id].get("periodos", {})
                        prev_persist = {
                            p: (info.get("mm") or 0.0) for p, info in base_per.items()
                        }
                        if not prev_persist:
                            continue
                        score = calcular_score_dia(prev_persist, real_periodos)
                        historico[local_id][data_alvo_str][prazo_id]["persistencia"] = score
                        total_auditorias += 1
                        continue

                    if m_id not in forecast_alvo:
                        continue

                    prev_periodos = forecast_alvo[m_id]
                    # prev_periodos pode ser {'madrugada': mm, 'manha': mm, ...}
                    if not isinstance(prev_periodos, dict):
                        continue

                    score = calcular_score_dia(prev_periodos, real_periodos)
                    historico[local_id][data_alvo_str][prazo_id][m_id] = score
                    total_auditorias += 1

                fonte_label = real_local.get("fonte", "?")[:40]
                print(f"  [OK] [{local_id}] {data_alvo_str} ({prazo_id}) auditado - fonte: {fonte_label}...")

    # Salva o histórico atualizado
    with open(caminho_hist, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

    print(f"\n--- Auditoria finalizada. {total_auditorias} comparações registradas. ---")
    print(f"Histórico salvo em: {caminho_hist}")


if __name__ == "__main__":
    main()
