import os
import json
import time
from datetime import datetime, timedelta
from scripts.config import REALIDADE_DIR, LOCAIS
from scripts.coletar_realidade import coletar_archive_best_match

def main():
    print("--- Backfill History Reality ---")
    
    start_date = datetime(2026, 4, 1)
    end_date = datetime(2026, 4, 16)
    
    curr = start_date
    while curr <= end_date:
        data_str = curr.strftime("%Y-%m-%d")
        print(f"Processando {data_str}...")
        
        realidade_dia = {}
        for local_id, info in LOCAIS.items():
            print(f"  Coletando {local_id}...")
            total, per = coletar_archive_best_match(info["lat"], info["lon"], data_str)
            if total is not None:
                realidade_dia[local_id] = {
                    "status": "completo",
                    "fonte": "Open-Meteo Archive (Best Match)",
                    "periodos": per,
                    "total_dia": total
                }
            time.sleep(1) # sleep para nao abusar mt da limitacao da API
        
        if realidade_dia:
            with open(REALIDADE_DIR / f"realidade_{data_str}.json", "w", encoding="utf-8") as f:
                json.dump(realidade_dia, f, indent=2, ensure_ascii=False)
        
        curr += timedelta(days=1)

if __name__ == "__main__":
    main()
