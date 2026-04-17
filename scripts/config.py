"""
TOPCLIMABC — config.py
======================
Configuração Central do Backend.

IMPORTANTE para IAs futuras:
- Este arquivo é a única fonte de configuração dos scripts.
- Não hardcode valores de lat/lon ou API keys nos scripts individuais.
- Chaves secretas são lidas do .env (se existir). Veja docs-projeto/CREDENCIAIS.md.
"""

import os
from pathlib import Path

# ── Diretórios ──────────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parent.parent
DOCS_DIR    = RAIZ / "docs"
DATA_DIR    = RAIZ / "data"
PREVISOES_DIR = DATA_DIR / "previsoes"
REALIDADE_DIR = DATA_DIR / "realidade"
AUDITORIA_DIR = DATA_DIR / "auditoria"

# Garante que as pastas existam
for d in (PREVISOES_DIR, REALIDADE_DIR, AUDITORIA_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Locais Monitorados ───────────────────────────────────────────────────────
LOCAIS = {
    "balneario_camboriu": {
        "nome":    "Balneário Camboriú",
        "abrev":   "BC",
        "lat":     -26.9928,
        "lon":     -48.6354,
        "ibge":    "4202008",
        "inmet_estacao": None,  # INMET sem dados regulares para BC (sem estação automática)
        "uf":      "SC",
    },
    "itajai": {
        "nome":    "Itajaí",
        "abrev":   "Itajaí",
        "lat":     -26.9065,
        "lon":     -48.6700,
        "ibge":    "4208203",
        "inmet_estacao": "A868",  # Estação automática do INMET em Itajaí
        "uf":      "SC",
    },
}

# ── Modelos de Previsão ──────────────────────────────────────────────────────
# Chave = ID interno usado em dados.json e ranking.json
# Cada modelo é mapeado para apps que os usuários comuns usam
MODELOS = {
    "ecmwf_ifs025": {
        "nome_display":   "ECMWF IFS",
        "open_meteo_id":  "ecmwf_ifs025",
        "apps_relacionados": ["Windy (padrão)", "Apple Weather"],
        "is_baseline":    False,
    },
    "gfs_seamless": {
        "nome_display":   "GFS NCEP",
        "open_meteo_id":  "gfs_seamless",
        "apps_relacionados": ["Weather.com", "The Weather Channel"],
        "is_baseline":    False,
    },
    "icon_seamless": {
        "nome_display":   "ICON DWD",
        "open_meteo_id":  "icon_seamless",
        "apps_relacionados": ["Windy (alt)", "Bright Sky"],
        "is_baseline":    False,
    },
    "openweathermap": {
        "nome_display":   "OpenWeatherMap",
        "open_meteo_id":  None,  # Coleta via API OWM diretamente
        "apps_relacionados": ["OpenWeatherMap App"],
        "is_baseline":    False,
    },
    "best_match": {
        "nome_display":   "Open-Meteo Best",
        "open_meteo_id":  "best_match",
        "apps_relacionados": ["Open-Meteo App"],
        "is_baseline":    False,
    },
    "persistencia": {
        "nome_display":   "Persistência",
        "open_meteo_id":  None,  # Gerado internamente (cópia da realidade de ontem)
        "apps_relacionados": [],
        "is_baseline":    True,  # Linha de corte mínima (não pode perder pro acaso)
    },
}

# ── Prazos de Auditoria ──────────────────────────────────────────────────────
# Cada prazo representa "quantos dias antes a previsão foi feita"
PRAZOS = ["1_dia", "3_dias", "7_dias", "15_dias"]
PRAZO_DIAS = {"1_dia": 1, "3_dias": 3, "7_dias": 7, "15_dias": 15}

# ── Períodos do Dia ──────────────────────────────────────────────────────────
# As horas são no horário local UTC-3 (horário de Brasília/SC)
PERIODOS = {
    "madrugada": {"horas": list(range(0, 6)),   "label": "Madrugada"},
    "manha":     {"horas": list(range(6, 12)),   "label": "Manhã"},
    "tarde":     {"horas": list(range(12, 18)),  "label": "Tarde"},
    "noite":     {"horas": list(range(18, 24)),  "label": "Noite"},
}

# ── Classificação de Chuva (mm acumulado no período) ────────────────────────
CLASSIFICACOES = [
    {"nome": "sem_chuva",    "min": 0,    "max": 0.5,  "label": "Sem Chuva"},
    {"nome": "fraca",        "min": 0.5,  "max": 5.0,  "label": "Fraca"},
    {"nome": "moderada",     "min": 5.0,  "max": 15.0, "label": "Moderada"},
    {"nome": "forte",        "min": 15.0, "max": 40.0, "label": "Forte"},
    {"nome": "muito_forte",  "min": 40.0, "max": 999,  "label": "Muito Forte"},
]

# ── APIs Externas ─────────────────────────────────────────────────────────────
OWM_API_KEY = os.getenv("OWM_API_KEY", "d642bd544942199ff3b862927da91923")
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_HIST  = "https://historical-forecast-api.open-meteo.com/v1/forecast"
OWM_BASE         = "https://api.openweathermap.org/data/2.5"

# ── Fonte de Realidade ────────────────────────────────────────────────────────
# DECISÃO (2026-04-16): A API oficial CEMADEN (SWS/PED) exige token institucional
# que não está disponível publicamente. O Mapa Interativo também bloqueou o endpoint PHP.
# SOLUÇÃO ADOTADA: Usar Open-Meteo Historical como fonte primária de precipitação real.
# Open-Meteo Historical usa dados ERA5 (reanálise do ECMWF) + dados observacionais
# combinados — é usado pela comunidade científica como referência de dados climáticos.
# FALLBACK: INMET A868 (Itajaí) quando responder com dados (HTTP 200 vs 204 atual).
# Se ambos falharem, o sistema marcará o dia como "sem_dados_realidade" e emitirá alerta.
FONTE_REALIDADE_PRIMARIA  = "open_meteo_historical"  # ERA5 + observações combinadas
FONTE_REALIDADE_SECUNDARIA = "inmet"                  # INMET A868 Itajaí

# ── Open-Meteo Historical: parâmetros ────────────────────────────────────────
# Precipitação: usa a API de reanálise histórica (dados do passado após processamento)
# Disponível 1-5 dias atrás com boa confiabilidade
OM_HIST_VARIAVEIS = "precipitation"
OM_HIST_TIMEZONE  = "America/Sao_Paulo"

# ── Alertas e Log ─────────────────────────────────────────────────────────────
ALERTA_SCRAPER_QUEBRADO = (
    "⚠️  ALERTA FONTE DE DADOS: A fonte de realidade '{fonte}' retornou dados "
    "inválidos ou vazios para {local} em {data}. "
    "Verificar se a API mudou ou se houve falha de conexão."
)

# ── Supabase (Fase 3) ─────────────────────────────────────────────────────────
# Projeto: Craquepedia (ndqgvqajdjrzbwgsmmoe) — INATIVO, restaurar manualmente
SUPABASE_URL  = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY  = os.getenv("SUPABASE_ANON_KEY", "")
