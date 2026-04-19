"""
TOPCLIMABC — migrar_classes.py
===============================
Script ONE-SHOT (executar uma vez após o sprint de correções 2026-04-18):
reclassifica os arquivos de realidade existentes em `data/realidade/`
usando o novo vocabulário de classes (seco/garoa/moderada/forte/intensa).

Arquivos antigos usavam: sem_chuva, fraca, moderada, forte, muito_forte.
Novos nomes vêm do Supabase/UI e são mantidos em scripts/config.py.

A operação é idempotente: rodar múltiplas vezes não estraga nada.

Uso:
    python -m scripts.migrar_classes
"""

import json
from scripts.config import REALIDADE_DIR
from scripts.utils.classificacao import classificar_chuva


def migrar_arquivo(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    mudou = False
    for local_id, info in data.items():
        if not isinstance(info, dict):
            continue
        periodos = info.get("periodos", {})
        for periodo, pdata in periodos.items():
            if not isinstance(pdata, dict):
                continue
            mm = pdata.get("mm")
            classe_antiga = pdata.get("classificacao")
            classe_nova = classificar_chuva(mm)
            if classe_antiga != classe_nova:
                pdata["classificacao"] = classe_nova
                mudou = True

    if mudou:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return mudou


def main():
    arquivos = sorted(REALIDADE_DIR.glob("realidade_*.json"))
    print(f"Migrando {len(arquivos)} arquivo(s) de realidade...")
    alterados = 0
    for fp in arquivos:
        if migrar_arquivo(fp):
            alterados += 1
            print(f"  [OK] {fp.name}")
    print(f"\nTotal: {alterados} arquivo(s) atualizado(s) / {len(arquivos) - alterados} já estavam corretos.")


if __name__ == "__main__":
    main()
