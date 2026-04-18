import time
from datetime import datetime, timedelta
from scripts.config import LOCAIS
from scripts.coletar_realidade import coletar_e_salvar

def main():
    print("--- Backfill History Reality ---")
    start_date = datetime(2026, 4, 1)
    end_date = datetime(2026, 4, 16)
    
    curr = start_date
    while curr <= end_date:
        data_str = curr.strftime("%Y-%m-%d")
        print(f"Processando {data_str}...")
        for local_id in LOCAIS:
            coletar_e_salvar(local_id, data_str)
            time.sleep(1)
        curr += timedelta(days=1)

if __name__ == "__main__":
    main()
