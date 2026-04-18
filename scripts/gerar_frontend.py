"""
TOPCLIMABC — gerar_frontend.py
=================================
Sincroniza os dados processados do backend com a pasta docs/ (frontend).
Transforma os arquivos brutos em dados.json, ranking.json e estacoes.json.

IMPORTANTE para IAs futuras:
- dados.json: realidade de ontem + previsões dos próximos dias
- ranking.json: scores médios por modelo/local/prazo
- estacoes.json: estado atual de dados por local (ERA5 Archive)
  → NÃO contém dados fictícios. Se não há dado, retorna null.
  → O CEMADEN físico está indisponível. Quando integrado, substituir aqui.
"""

import json
from datetime import datetime, timedelta
from scripts.config import (
    LOCAIS, MODELOS, PRAZOS, AUDITORIA_DIR,
    PREVISOES_DIR, REALIDADE_DIR, DOCS_DIR
)


def carregar_json(caminho):
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def gerar_estacoes_json(realidade_ontem, realidade_hoje_parcial=None):
    """
    Gera o estacoes.json com dados reais da ERA5 Archive.
    SEM nenhum dado fictício ou mockado.
    Se não há dados, os campos são null (não 0mm inventado).
    """
    agora = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-03:00")

    estacoes = {
        "meta": {
            "atualizado_em": agora,
            "fonte": "ERA5 Archive (ECMWF) via Open-Meteo",
            "nota": (
                "Dados de reanálise por ponto geográfico central de cada cidade. "
                "Pluviômetros físicos (CEMADEN) indisponíveis no momento — integração futura."
            ),
            "aviso": (
                "⚠️ Estes dados são estimativas de reanálise, não medições de pluviômetros físicos. "
                "ERA5 Archive tem precisão de ~5-25km e delay de 2-5 dias para datas recentes."
            ),
            "status_cemaden": "indisponivel"
        },
        "locais": {}
    }

    for local_id, local_info in LOCAIS.items():
        real_ontem = realidade_ontem.get(local_id, {}) if realidade_ontem else {}

        # Extrai dados de ontem (só se status for confiável)
        ontem_dados = None
        if real_ontem.get("status") in ("completo", "provisorio"):
            periodos = real_ontem.get("periodos", {})
            ontem_dados = {
                "status_fonte": real_ontem.get("status"),
                "fonte": real_ontem.get("fonte", ""),
                "total_dia": real_ontem.get("total_dia"),
                "periodos": {
                    p: {
                        "mm": info.get("mm"),
                        "classificacao": info.get("classificacao")
                    }
                    for p, info in periodos.items()
                }
            }

        estacoes["locais"][local_id] = {
            "nome": local_info["nome"],
            "lat": local_info["lat"],
            "lon": local_info["lon"],
            "fonte_dados": "ERA5 Archive (ECMWF)",
            "status_cemaden": "indisponivel",
            "ontem": ontem_dados,
            "hoje": None  # Dados de hoje nunca disponíveis (ERA5 tem delay)
        }

    return estacoes


def main():
    print(f"--- Gerando dados para Frontend: {datetime.now()} ---")

    # 1. Carregar Histórico de Auditoria
    historico = carregar_json(AUDITORIA_DIR / "historico.json")

    # 2. Gerar ranking.json (Score Médio por Modelo/Local/Prazo)
    ranking = {local_id: {} for local_id in LOCAIS}

    for local_id, datas in historico.items():
        for prazo_id in PRAZOS:
            ranking[local_id][prazo_id] = []

            for m_id, m_info in MODELOS.items():
                if m_info.get("is_baseline") and m_id == "persistencia":
                    continue  # Persistência não entra no ranking de modelos

                scores = []
                for data_iso, prazos_data in datas.items():
                    if prazo_id in prazos_data and m_id in prazos_data[prazo_id]:
                        scores.append(prazos_data[prazo_id][m_id])

                media = round(sum(scores) / len(scores), 1) if scores else 0

                ranking[local_id][prazo_id].append({
                    "modelo": m_id,
                    "nome": m_info["nome_display"],
                    "score": media,
                    "amostras": len(scores)
                })

            # Ordena do maior score para o menor
            ranking[local_id][prazo_id].sort(key=lambda x: x["score"], reverse=True)

    # 3. Gerar dados.json (Realidade de Ontem + Previsões de Hoje e Futuro)
    data_hoje = datetime.now().date().isoformat()
    data_ontem = (datetime.now() - timedelta(days=1)).date().isoformat()

    realidade_ontem = carregar_json(REALIDADE_DIR / f"realidade_{data_ontem}.json")
    snap_hoje = carregar_json(PREVISOES_DIR / f"snapshot_{data_hoje}.json")
    snap_ontem = carregar_json(PREVISOES_DIR / f"snapshot_{data_ontem}.json")

    dados_frontend = {
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "locais": {}
    }

    for local_id in LOCAIS:
        previsoes_hoje = snap_hoje.get("locais", {}).get(local_id, {})
        previsoes_ontem = snap_ontem.get("locais", {}).get(local_id, {})

        previsoes_combinadas = {}

        # Previsões de ontem (inclui o nó do dia ontem com score_1d se disponível)
        if data_ontem in previsoes_ontem:
            previsoes_combinadas[data_ontem] = previsoes_ontem[data_ontem]
            # Injeta score_1d se disponível
            if data_ontem in historico.get(local_id, {}):
                scores_1d = historico[local_id][data_ontem].get("1_dia", {})
                for m_id, model_data in previsoes_combinadas[data_ontem].items():
                    if m_id in scores_1d:
                        model_data["score_1d"] = scores_1d[m_id]

        # Adiciona previsões de hoje e futuro
        previsoes_combinadas.update(previsoes_hoje)

        dados_frontend["locais"][local_id] = {
            "realidade": realidade_ontem.get(local_id, {}),
            "previsoes": previsoes_combinadas
        }

    # 4. Gerar estacoes.json (sem dados mockados)
    estacoes = gerar_estacoes_json(realidade_ontem)

    # 5. Salvar arquivos na pasta docs/
    with open(DOCS_DIR / "ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)

    with open(DOCS_DIR / "dados.json", "w", encoding="utf-8") as f:
        json.dump(dados_frontend, f, indent=2, ensure_ascii=False)

    with open(DOCS_DIR / "estacoes.json", "w", encoding="utf-8") as f:
        json.dump(estacoes, f, indent=2, ensure_ascii=False)

    print(f"[OK] Frontend sincronizado com sucesso em {DOCS_DIR}")
    print(f"   -> dados.json | ranking.json | estacoes.json")


if __name__ == "__main__":
    main()
