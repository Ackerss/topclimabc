"""
TOPCLIMABC — bootstrap_realidade.py
===================================
Popula os últimos 15 dias de realidade (chuva medida) para que o app não comece vazio.
"""

import json
from datetime import datetime, timedelta
from scripts.config import LOCAIS, REALIDADE_DIR
import scripts.coletar_realidade as coletor

def main():
    print("--- Iniciando Bootstrap de Realidade (Últimos 15 dias) ---")
    
    for i in range(1, 16):
        data_iso = (datetime.now() - timedelta(days=i)).date().isoformat()
        print(f"Buscando realidade para {data_iso}...")
        
        for local_id in LOCAIS:
            raw = coletor.coletar_om_historical(local_id, data_iso)
            realidade = coletor.processar_realidade(raw, data_iso)
            
            if realidade:
                caminho = REALIDADE_DIR / f"realidade_{data_iso}.json"
                
                # Merge local no arquivo da data
                dados_arquivo = {}
                if caminho.exists():
                    with open(caminho, "r", encoding="utf-8") as f:
                        dados_arquivo = json.load(f)
                
                dados_arquivo[local_id] = realidade
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(dados_arquivo, f, indent=2, ensure_ascii=False)
                    
    print("Bootstrap de realidade concluído!")

if __name__ == "__main__":
    main()
