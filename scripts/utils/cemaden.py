"""
TOPCLIMABC — utils/cemaden.py
=============================
Cliente da API PED do CEMADEN (Centro Nacional de Monitoramento e Alertas
de Desastres Naturais). Fonte PRIMÁRIA de dados reais de precipitação —
pluviômetros físicos instalados em BC, Itajaí e adjacências.

Documentação da API:
  Base:     https://sws.cemaden.gov.br/PED/rest/
  Swagger:  https://sws.cemaden.gov.br/PED/api/ui/

IBGE BC:     4202008
IBGE Itajaí: 4208203

Design do client:
- Nunca levanta exceção para o caller. Retorna estruturas vazias em caso
  de falha e loga o motivo. O pipeline segue para o fallback (Open-Meteo).
- Cacheia a lista de estações por execução para evitar re-fetch.
- Normaliza saída em mm por período (madrugada/manha/tarde/noite).

IMPORTANTE — sobre autenticação:
  A PED é pública para consulta (contrato CEMADEN–MCTI). Alguns endpoints
  podem variar com/sem token — deixamos suporte opcional ao token via
  env CEMADEN_TOKEN. Sem token, o client TENTA direto.
"""

from __future__ import annotations
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

CEMADEN_BASE = "https://sws.cemaden.gov.br/PED/rest"
TOKEN = os.getenv("CEMADEN_TOKEN", "").strip()

TIMEOUT = 20
_ESTACOES_CACHE: Dict[str, list] = {}


def _headers() -> dict:
    h = {"Accept": "application/json"}
    if TOKEN:
        h["token"] = TOKEN
    return h


def _req(path: str, params: Optional[dict] = None) -> Optional[dict]:
    url = f"{CEMADEN_BASE}{path}"
    try:
        resp = requests.get(url, params=params, headers=_headers(), timeout=TIMEOUT)
        if resp.status_code == 401:
            print(f"  [CEMADEN] 401 em {path} — token ausente ou inválido.")
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [CEMADEN] Falhou {path}: {e}")
        return None


def listar_estacoes_municipio(cod_ibge: str) -> List[dict]:
    """
    Lista estações pluviométricas para um município pelo código IBGE.
    Cacheia em memória para a execução atual.
    """
    if cod_ibge in _ESTACOES_CACHE:
        return _ESTACOES_CACHE[cod_ibge]

    # Endpoint típico da PED. A API exige municipio por código IBGE.
    data = _req("/pcds-cadastro/estacoes", params={"municipio": cod_ibge})
    estacoes: List[dict] = []
    if isinstance(data, list):
        estacoes = data
    elif isinstance(data, dict):
        # Em algumas versões do schema a resposta vem envelopada.
        for chave in ("estacoes", "data", "items", "result"):
            if chave in data and isinstance(data[chave], list):
                estacoes = data[chave]
                break

    # Filtra somente pluviômetros (tipo PCD ou sensor de chuva).
    estacoes_filtradas = []
    for e in estacoes:
        tipo = str(e.get("tipoEstacao") or e.get("tipo") or "").upper()
        if "PLU" in tipo or "PCD" in tipo or tipo == "":  # aceita inclusive desconhecido
            estacoes_filtradas.append(e)

    _ESTACOES_CACHE[cod_ibge] = estacoes_filtradas
    print(f"  [CEMADEN] {cod_ibge}: {len(estacoes_filtradas)} estação(ões) encontrada(s).")
    return estacoes_filtradas


def obter_dados_estacao(cod_estacao: str, data_iso: str) -> List[dict]:
    """
    Retorna registros horários (ou sub-horários) da estação para o dia.
    Cada registro deve ter pelo menos {datahora, valor}.
    """
    # Janela: 00:00 BRT → 00:00 BRT do dia seguinte (em UTC é +3h).
    inicio = f"{data_iso}T00:00:00"
    fim    = f"{data_iso}T23:59:59"
    params = {
        "codEstacao": cod_estacao,
        "inicio": inicio,
        "fim": fim,
    }
    data = _req("/pcds/dados_pcd", params=params)
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for chave in ("dados", "data", "items", "result"):
            if chave in data and isinstance(data[chave], list):
                return data[chave]
    return []


def _distribuir_em_periodos(registros: List[dict]) -> Dict[str, float]:
    """
    Agrupa registros em períodos (madrugada/manha/tarde/noite).
    Cada registro deve ter 'datahora' (ISO UTC) e 'valor' (mm).
    """
    PERIODOS = {
        "madrugada": range(0, 6),
        "manha":     range(6, 12),
        "tarde":     range(12, 18),
        "noite":     range(18, 24),
    }
    acum = {p: 0.0 for p in PERIODOS}
    for r in registros:
        valor = r.get("valor") or r.get("chuva") or r.get("mm") or 0.0
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            continue
        if valor < 0 or valor > 500:  # sanity check: 500mm/10min é impossível
            continue

        dh = r.get("datahora") or r.get("dataHora") or r.get("dt") or ""
        try:
            # CEMADEN entrega em UTC. Convertemos para BRT.
            dt_utc = datetime.fromisoformat(dh.replace("Z", "+00:00"))
            if dt_utc.tzinfo is None:
                dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            dt_brt = dt_utc - timedelta(hours=3)
            hora = dt_brt.hour
        except Exception:
            continue

        for nome, horas in PERIODOS.items():
            if hora in horas:
                acum[nome] += valor
                break
    return {k: round(v, 2) for k, v in acum.items()}


def obter_realidade_municipio(cod_ibge: str, data_iso: str) -> Optional[dict]:
    """
    Consolida dados de TODAS as estações do município para o dia.
    Usa MEDIANA entre estações para resistir a pluviômetros com defeito.

    Retorna:
      {
        "fonte": "CEMADEN",
        "periodos": {"madrugada": mm, "manha": mm, "tarde": mm, "noite": mm},
        "total_dia": mm,
        "estacoes_usadas": ["G2-...", ...],
      }
    Ou None se não houver NENHUMA estação com dado.
    """
    estacoes = listar_estacoes_municipio(cod_ibge)
    if not estacoes:
        return None

    medicoes_por_estacao: List[Dict[str, float]] = []
    usadas: List[str] = []

    for est in estacoes:
        cod = est.get("codEstacao") or est.get("codigo") or est.get("cod")
        if not cod:
            continue
        regs = obter_dados_estacao(cod, data_iso)
        if not regs:
            continue
        periodos = _distribuir_em_periodos(regs)
        if sum(periodos.values()) == 0 and not regs:
            # estação ativa mas sem registro — ignora
            continue
        medicoes_por_estacao.append(periodos)
        usadas.append(cod)

    if not medicoes_por_estacao:
        return None

    # Consenso = mediana por período (robusto a estações defeituosas).
    import statistics
    consenso = {}
    for p in ("madrugada", "manha", "tarde", "noite"):
        valores = [m[p] for m in medicoes_por_estacao if p in m]
        consenso[p] = round(statistics.median(valores), 2) if valores else 0.0

    total = round(sum(consenso.values()), 1)
    return {
        "fonte": f"CEMADEN ({len(usadas)} estação(ões))",
        "periodos": consenso,
        "total_dia": total,
        "estacoes_usadas": usadas,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI de teste — execute diretamente para validar a conexão com a API:
#   python -m scripts.utils.cemaden
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from datetime import date
    ontem = (date.today() - timedelta(days=1)).isoformat()
    for nome, ibge in [("BC", "4202008"), ("Itajaí", "4208203")]:
        print(f"\n=== {nome} ({ibge}) — {ontem} ===")
        r = obter_realidade_municipio(ibge, ontem)
        if r:
            print(r)
        else:
            print("(sem dados retornados pela API)")
