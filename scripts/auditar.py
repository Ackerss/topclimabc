"""
TOPCLIMABC — 03_auditar.py
==========================
O "Cérebro" auditor.
Compara as previsões feitas no passado com a realidade medida.
Gera os scores de acerto e atualiza o histórico.
"""

import json
from datetime import datetime, timedelta
from scripts.config import (
    LOCAIS, MODELOS, PRAZO_DIAS, AUDITORIA_DIR, 
    PREVISOES_DIR, REALIDADE_DIR
)
from scripts.utils.score import calcular_score_dia

def carregar_arquivo(caminho):
    if caminho.exists():
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def main():
    print(f"--- Início da Auditoria: {datetime.now()} ---")
    
    # O alvo da auditoria é ontém (dia que já temos realidade completa)
    data_alvo = (datetime.now() - timedelta(days=1)).date().isoformat()
    # data_alvo = "2026-04-15" # Para teste manual fixo se necessário
    
    # 1. Carregar Realidade do Alvo
    caminho_real = REALIDADE_DIR / f"realidade_{data_alvo}.json"
    realidade_data = carregar_arquivo(caminho_real)
    
    if not realidade_data:
        print(f"ERRO: Nenhuma realidade encontrada para {data_alvo}. Abortando.")
        return

    # 2. Carregar Histórico de Auditoria existente
    caminho_hist = AUDITORIA_DIR / "historico.json"
    historico = carregar_arquivo(caminho_hist) or {}

    # 3. Auditar cada local
    for local_id in LOCAIS:
        if local_id not in realidade_data: continue
        
        real_local = realidade_data[local_id]
        real_periodos = {p: info["mm"] for p, info in real_local["periodos"].items()}
        
        if local_id not in historico: historico[local_id] = {}
        if data_alvo not in historico[local_id]: historico[local_id][data_alvo] = {}

        # 4. Verificar cada prazo (1d, 3d, 7d, 15d)
        for prazo_id, dias in PRAZO_DIAS.items():
            # Data em que a previsão foi coletada
            dt_coleta = (datetime.fromisoformat(data_alvo) - timedelta(days=dias)).date().isoformat()
            
            # Tenta carregar o snapshot daquela data
            caminho_snap = PREVISOES_DIR / f"snapshot_{dt_coleta}.json"
            snapshot = carregar_arquivo(caminho_snap)
            
            if not snapshot:
                # print(f"Aviso: Snapshot de {dt_coleta} não encontrado para auditoria de {prazo_id}.")
                continue
                
            # Extrai as previsões do snapshot para a data alvo
            # snapshot["locais"][local_id][data_alvo]
            forecasts_local = snapshot.get("locais", {}).get(local_id, {})
            forecast_alvo = forecasts_local.get(data_alvo, {})
            
            if not forecast_alvo:
                continue

            if prazo_id not in historico[local_id][data_alvo]:
                historico[local_id][data_alvo][prazo_id] = {}

            # 5. Calcular Score para cada Modelo
            for m_id in MODELOS:
                if m_id in forecast_alvo:
                    prev_periodos = forecast_alvo[m_id]
                    score = calcular_score_dia(prev_periodos, real_periodos)
                    
                    historico[local_id][data_alvo][prazo_id][m_id] = score
                    # print(f"[{local_id}] Auditoria {prazo_id} - {m_id}: {score}%")

    # Salva o histórico atualizado
    with open(caminho_hist, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)
        
    print(f"Auditoria finalizada. Histórico atualizado em {caminho_hist}")

if __name__ == "__main__":
    main()
