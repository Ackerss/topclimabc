"""
TOPCLIMABC — 04_gerar_frontend.py
=================================
Sincroniza os dados processados do backend com a pasta docs/ (frontend).
Transforma os arquivos brutos em dadas.json e ranking.json.
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

def main():
    print(f"--- Gerando dados para Frontend: {datetime.now()} ---")
    
    # 1. Carregar Histórico de Auditoria
    historico = carregar_json(AUDITORIA_DIR / "historico.json")
    
    # 2. Gerar ranking.json (Cálculo de Score Médio por Modelo/Local/Prazo)
    ranking = {local_id: {} for local_id in LOCAIS}
    
    for local_id, datas in historico.items():
        for prazo_id in PRAZOS:
            ranking[local_id][prazo_id] = []
            
            # Para cada modelo, calcula a média de todos os dias auditados
            for m_id, m_info in MODELOS.items():
                if m_info["is_baseline"] and m_id == "persistencia":
                    continue # Persistência não entra no ranking de modelos
                
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

    # 3. Gerar dados.json (Realidade de Ontem + Previsões de Hoje)
    data_hoje = datetime.now().date().isoformat()
    data_ontem = (datetime.now() - timedelta(days=1)).date().isoformat()
    
    # Busca realidade de ontem
    realidade_ontem = carregar_json(REALIDADE_DIR / f"realidade_{data_ontem}.json")
    
    # Busca snapshot de hoje para as previsões futuras
    snap_hoje = carregar_json(PREVISOES_DIR / f"snapshot_{data_hoje}.json")
    # Busca snapshot de ontem para as previsões antigas (as que foram auditadas hoje)
    snap_ontem = carregar_json(PREVISOES_DIR / f"snapshot_{data_ontem}.json")
    
    dados_frontend = {
        "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "locais": {}
    }
    
    for local_id in LOCAIS:
        previsoes_hoje = snap_hoje.get("locais", {}).get(local_id, {})
        previsoes_ontem = snap_ontem.get("locais", {}).get(local_id, {})
        
        previsoes_combinadas = {}
        # Previsões de ontem (apenas o node de ontem)
        if data_ontem in previsoes_ontem:
            previsoes_combinadas[data_ontem] = previsoes_ontem[data_ontem]
            
            # Injeta score_1d
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

    # 4. Salvar arquivos na pasta docs/
    with open(DOCS_DIR / "ranking.json", "w", encoding="utf-8") as f:
        json.dump(ranking, f, indent=2, ensure_ascii=False)
        
    with open(DOCS_DIR / "dados.json", "w", encoding="utf-8") as f:
        json.dump(dados_frontend, f, indent=2, ensure_ascii=False)
        
    print(f"Frontend sincronizado com sucesso em {DOCS_DIR}")

if __name__ == "__main__":
    main()
