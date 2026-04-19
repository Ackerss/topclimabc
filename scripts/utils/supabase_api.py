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


def _fetch_registros_resolvidos(data_iso: str = None):
    """
    Busca registros da tabela topclimabc_validacoes com resolucao de tombstones.

    Retorna tupla (overrides, tombstones) onde para cada chave (data, local, periodo)
    apenas o registro mais recente conta:
    - override=True: vai para overrides
    - override=False: vai para tombstones (foi apagado via soft-delete no frontend,
      ja que a RLS do Supabase bloqueia DELETE para role anon)

    Se data_iso e None, as estruturas sao aninhadas por data: { data: { local: {...} } }
    Se data_iso e especifico, retorna direto: { local: {...} }
    """
    if not SUPABASE_KEY:
        print("  [Supabase] SUPABASE_ANON_KEY nao configurada — pulando overrides manuais.")
        return ({}, {})

    url = f"{SUPABASE_URL}/rest/v1/topclimabc_validacoes"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

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
        print(f"  [Supabase] Erro ao buscar registros para {data_iso}: {e}")
        return ({}, {})

    overrides = {}
    tombstones = {}
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
            # tombstone
            if data_iso:
                tombstones.setdefault(local, set()).add(periodo)
            else:
                tombstones.setdefault(data_reg, {}).setdefault(local, set()).add(periodo)
            continue

        # override ativo
        if data_iso:
            target = overrides
        else:
            target = overrides.setdefault(data_reg, {})

        target.setdefault(local, {})[periodo] = {
            "classificacao": classificacao,
            "mm": MM_POR_CLASSIFICACAO.get(classificacao, 0.0),
            "nota": r.get("nota"),
            "timestamp": r.get("created_at"),
            "fonte": "manual",
            "override": True,
        }

    return (overrides, tombstones)


def buscar_tombstones(data_iso: str = None) -> dict:
    """
    Retorna os periodos 'apagados' via soft-delete no frontend.
    - data_iso especifico: { local: set([periodos]) }
    - data_iso None: { data: { local: set([periodos]) } }
    """
    _, tombstones = _fetch_registros_resolvidos(data_iso)
    return tombstones


def buscar_overrides_manuais(data_iso: str = None) -> dict:
    """
    Se data_iso for passado, retorna dict:
    { "balneario_camboriu": { "madrugada": {...} } }

    Se data_iso = None, busca TODOS e retorna:
    { "YYYY-MM-DD": { "balneario_camboriu": { "madrugada": {...} } } }

    Ja descarta tombstones (soft-deletes) — so retorna periodos ativos.
    """
    overrides, _ = _fetch_registros_resolvidos(data_iso)
    resultado = overrides

    if resultado:
        count = sum(len(v) for v in resultado.values()) if data_iso else sum(sum(len(loc) for loc in dias.values()) for dias in resultado.values())
        print(f"  [Supabase] {count} override(s) manual(is) retornado(s).")

    return resultado

