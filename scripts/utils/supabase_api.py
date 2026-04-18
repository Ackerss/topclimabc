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

MM_POR_CLASSIFICACAO = {
    "seco":     0.0,
    "garoa":    2.5,
    "moderada": 10.0,
    "forte":    25.0,
    "intensa":  50.0,
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
    
    params = {
        "override": "eq.true",
        "order": "created_at.desc",
        "select": "data,local,periodo,classificacao,nota,created_at",
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
    for r in registros:
        data_reg = r.get("data")
        local = r.get("local")
        periodo = r.get("periodo")
        classificacao = r.get("classificacao")
        if not all([data_reg, local, periodo, classificacao]):
            continue
            
        # Target dict dependendo se data_iso é None ou específico
        if data_iso:
            target_dict = resultado
        else:
            if data_reg not in resultado:
                resultado[data_reg] = {}
            target_dict = resultado[data_reg]

        if local not in target_dict:
            target_dict[local] = {}
            
        if periodo not in target_dict[local]:
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

