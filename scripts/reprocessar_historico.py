"""
TOPCLIMABC — reprocessar_historico.py
======================================
Script de bootstrap: reprocessa dados de realidade históricos
usando Open-Meteo Archive com modelo best_match (melhor fonte disponível
para o Sul do Brasil — combina ERA5-Land + estações físicas observacionais).

QUANDO USAR:
- Ao iniciar o projeto (primeira vez)
- Após mudança de fonte de realidade (ex: de hist_forecast para ERA5 Archive)
- Quando suspeitar que arquivos de realidade estão incorretos

Este script SOBRESCREVE os arquivos de realidade existentes.
Execute manualmente, não pelo GitHub Actions.

Uso:
    python -m scripts.reprocessar_historico
    python -m scripts.reprocessar_historico --data-inicio 2026-04-01 --data-fim 2026-04-15
"""

import sys
import json
from datetime import datetime, timedelta
from scripts.config import LOCAIS, REALIDADE_DIR
from scripts.coletar_realidade import coletar_e_salvar


def gerar_range_datas(data_inicio, data_fim):
    """Gera lista de datas ISO entre data_inicio e data_fim (inclusive)."""
    datas = []
    atual = data_inicio
    while atual <= data_fim:
        datas.append(atual.isoformat())
        atual += timedelta(days=1)
    return datas


def main():
    # Parse de argumentos simples (--data-inicio, --data-fim)
    args = sys.argv[1:]
    data_inicio = None
    data_fim = None

    for i, arg in enumerate(args):
        if arg == "--data-inicio" and i + 1 < len(args):
            data_inicio = datetime.fromisoformat(args[i + 1]).date()
        elif arg == "--data-fim" and i + 1 < len(args):
            data_fim = datetime.fromisoformat(args[i + 1]).date()

    # Padrões: do início do projeto até 5 dias atrás (ERA5 precisa de delay)
    if not data_inicio:
        data_inicio = datetime(2026, 4, 1).date()
    if not data_fim:
        # Não reprocessar os últimos 3 dias (ERA5 pode não estar pronto)
        data_fim = (datetime.now() - timedelta(days=3)).date()

    datas = gerar_range_datas(data_inicio, data_fim)
    print(f"=== Reprocessamento Histórico ===")
    print(f"Periodo: {data_inicio} ate {data_fim} ({len(datas)} dias)")
    print(f"Locais: {list(LOCAIS.keys())}")
    print(f"Fonte primaria: Open-Meteo Archive (best_match)")
    print()

    sucesso = 0
    provisorio = 0
    sem_dados = 0

    for data_iso in datas:
        print(f"\n[{data_iso}]")
        for local_id in LOCAIS:
            realidade = coletar_e_salvar(local_id, data_iso)
            status = realidade.get("status", "sem_dados")
            total = realidade.get("total_dia")
            total_str = f"{total:.1f}mm" if total is not None else "N/A"
            print(f"  {local_id}: {status} | total={total_str}", end="")

            if status == "completo":
                sucesso += 1
                print(" [OK]")
            elif status == "provisorio":
                provisorio += 1
                print(" [PROVISORIO]")
            else:
                sem_dados += 1
                print(" [SEM DADOS]")

    print(f"\n=== Resumo Final ===")
    print(f"[OK] Completos (Archive best_match): {sucesso}")
    print(f"[PROVISORIO] Provisorios (hist_forecast): {provisorio}")
    print(f"[SEM DADOS] Sem dados: {sem_dados}")
    print(f"Arquivos salvos em: {REALIDADE_DIR}")


if __name__ == "__main__":
    main()
