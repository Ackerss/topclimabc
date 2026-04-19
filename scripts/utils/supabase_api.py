"""
TOPCLIMABC — utils/supabase_api.py
====================================
Busca registros manuais da tabela topclimabc_validacoes no Supabase.
Usado pelo backend Python para consolidar dados antes de gerar JSONs.
"""

import requests
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jfjrzkjzfxnyhexwhoby.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Valor-padrão em mm para cada classe manual.
# Usado quando o usuário valida pela UI (sem saber o mm exato).
# Os valores ficam no meio do intervalo de cada classe (ver CLASSIFICACOES em config.py).
MM_POR_CLASSIFICACAO = {
    "seco":     0.0,
    "garoa":    1.0,    # meio de [0.1, 2.6)
    "moderada": 6.0,    # meio de [2.6, 10.1)
    "forte":    17.0,   # meio de [10.1, 25.1)
    "intensa":  40.0,   # limiar mínimo de "intensa" (≥ 25.1mm)
}


def buscar_overrides_manuais(data_iso: str = None) -> dict:
    """
    Se data_iso for passado, retorna dict:
    { "balneario_camboriu": { "madrugada": {...} } }

    Se data_iso = None, busca TODOS e retorna:
    { "YYYY-MM-DD": { "balneario_camboriu": { "madrugada": {...} } } }
    """
    if not SUPABASE_KEY:
        print("  [Supabase] SUPABASE_ANON_KEY não configurada — pulando overrides manuais.")
        return {}

    url = f"{SUPABASE_URL}/rest/v1/topclimabc_validacoes"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    # Busca TODOS os registros (inclusive tombstones com override=false).
    # Logica de resolucao: para cada chave (data, local, periodo) o mais recente vence.
    # Se o vencedor for override=false, o periodo foi apagado pelo usuario via frontend.
    # Isso existe porque a RLS do Supabase nao permite DELETE para role anon, entao
    # o frontend usa "soft-delete" inserindo uma linha tombstone.
    params = {
        "order": "created_at.desc",
        "select": "data,local,periodo,classificacao,nota,created_at,override",
    }
    if data_iso:
        params["data"] = f"eq.{data_iso}"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        registros = resp.json()
    except Exception as e:
        print(f"  [Supabase] Erro ao buscar overrides manuais para {data_iso}: {e}")
        return {}

    resultado = {}
    vistos = set()
    for r in registros:
        data_reg = r.get("data")
        local = r.get("local")
        periodo = r.get("periodo")
        classificacao = r.get("classificacao")
        override = r.get("override")
        if not all([data_reg, local, periodo, classificacao]):
            continue

        chave = (data_reg, local, periodo)
        if chave in vistos:
            continue  # ja processamos uma versao mais recente desta chave
        vistos.add(chave)

        if override is False:
            continue  # tombstone — periodo foi apagado

        # Target dict dependendo se data_iso e None ou especifico
        if data_iso:
            target_dict = resultado
        else:
            if data_reg not in resultado:
                resultado[data_reg] = {}
            target_dict = resultado[data_reg]

        if local not in target_dict:
            target_dict[local] = {}

        mm = MM_POR_CLASSIFICACAO.get(classificacao, 0.0)
        target_dict[local][periodo] = {
            "classificacao": classificacao,
            "mm": mm,
            "nota": r.get("nota"),
            "timestamp": r.get("created_at"),
            "fonte": "manual",
            "override": True,
        }

    if resultado:
        count = sum(len(v) for v in resultado.values()) if data_iso else sum(sum(len(loc) for loc in dias.values()) for dias in resultado.values())
        print(f"  [Supabase] {count} override(s) manual(is) retornado(s).")

    return resultado

