# 📊 STATUS DO PROJETO TOPCLIMABC

> **Para toda IA:** Este arquivo é a fonte de verdade sobre o estado atual do projeto.
> Atualize-o SEMPRE ao começar e terminar qualquer tarefa.
> Veja `PROTOCOLO-IA.md` para instruções detalhadas.

---

## 🗓️ ÚLTIMA ATUALIZAÇÃO

**Data:** 2026-04-18 — Sprint de Correções concluído
**IA:** Claude Opus 4.7
**Sessão:** Auditoria profunda + correção de 13 inconsistências (ver `PLANO-CORRECOES.md`)

### Roteiro Atual:
- **Fase 1 (Aesthetic Frontend):** Finalizada ✅
- **Fase 2 (Python Backend):** Finalizada ✅
- **Fase 3 (Cloud Storage/Supabase):** Integrado ✅, GHA rodando 🟢
- **Sprint de Correções 2026-04-18:** CONCLUÍDO ✅ (C1–C13)

---

### 📍 ONDE A IA PAROU

Sprint de correções técnicas **concluído** (2026-04-18). Todas as 13 issues da
auditoria resolvidas — ver `PLANO-CORRECOES.md`. O sistema agora:

1. Tenta CEMADEN PED primeiro (pluviômetro físico)
2. Faz fallback para Open-Meteo Archive best_match (reanálise ERA5-Land)
3. Último recurso: Open-Meteo Historical Forecast

Validações manuais do usuário (Supabase) **sobrescrevem qualquer fonte
automática** — agora com `override=true` corretamente inserido pelo frontend.

Score foi realinhado com `ARCHITECTURE.md`:
- Matriz 5×5 gradual (não mais binária)
- Volume −5 pts/mm (não mais −10)
- Peso madrugada 0.5× (outras faixas 1.0×)
- Persistência agora é **baseline obrigatória** no ranking

**Próxima tarefa sugerida:** Rodar `python -m scripts.migrar_classes` e depois
`python -m scripts.reprocessar_historico` para regenerar históricos consistentes
com o novo schema. (Scripts idempotentes.)

---

## ✅ O QUE JÁ FOI FEITO

### Documentação (100%)
- ✅ `ARCHITECTURE.md` — Plano mestre v2
- ✅ `README.md` — Visão geral
- ✅ `PROTOCOLO-IA.md` — Como outras IAs devem trabalhar aqui
- ✅ `STATUS.md` — Este arquivo
- ✅ `PLANO-CORRECOES.md` — Sprint 2026-04-18 (concluído)
- ✅ `docs-projeto/COMO-EXECUTAR-LOCAL.md` — Guia atualizado com o `.bat`

### Fase 1: Frontend SPA (100%)
- ✅ `docs/index.html` — Site completo com labels honestos sobre a fonte
- ✅ `docs/manifest.json` — Configuração de PWA
- ✅ `docs/icons/` — Ícones de alta resolução

### Fase 2: Backend Python (100%)
- ✅ `scripts/config.py` — Configuração central + classes unificadas
- ✅ `scripts/utils/score.py` — Matriz 5×5, volume −5/mm, peso madrugada 0.5×
- ✅ `scripts/utils/classificacao.py` — `[min, max)` com classes unificadas
- ✅ `scripts/utils/cemaden.py` — **NOVO:** cliente CEMADEN PED (fonte primária)
- ✅ `scripts/utils/supabase_api.py` — mm por classificação com mid-range
- ✅ `scripts/coletar_previsoes.py` — Timezone OWM corrigido (UTC→BRT)
- ✅ `scripts/coletar_realidade.py` — Hierarquia CEMADEN → Archive → Hist
- ✅ `scripts/auditar.py` — Inclui persistência como baseline
- ✅ `scripts/gerar_frontend.py` — Persistência no ranking
- ✅ `scripts/migrar_classes.py` — **NOVO:** one-shot p/ classes antigas
- ✅ `scripts/reprocessar_historico.py` — Atualizado para novo schema
- ✅ `TOPCLIMABC.bat` — Execução em 1-clique

### Fase 3: Cloud Storage ✅
- [x] Supabase KANBAN + tabela `topclimabc_validacoes`
- [x] SDK no `docs/index.html` (Feed em Tempo Real)
- [x] GitHub Actions ativo (`atualizacao_diaria.yml`)

---

## 🧪 SPRINT DE CORREÇÕES 2026-04-18 — RESUMO

| # | Correção | Status |
|---|----------|--------|
| C1 | Bug `override=true` no insert Supabase | ✅ |
| C2 | Score de volume −5 pts/mm | ✅ |
| C3 | Matriz 5×5 gradual de classificação | ✅ |
| C4 | Nomes de classes unificados (seco/garoa/moderada/forte/intensa) | ✅ |
| C5 | Timezone OWM (UTC → America/Sao_Paulo) | ✅ |
| C6 | Persistência como baseline obrigatório | ✅ |
| C7 | Peso madrugada 0.5× | ✅ |
| C8 | Labels honestos sobre a fonte no frontend | ✅ |
| C9 | Cliente CEMADEN PED (fonte primária) | ✅ |
| C10 | Comentário falso em `config.py` removido | ✅ |
| C11 | Script de migração de classes histórico | ✅ |
| C12 | Banner "Ranking em formação" no UI | ✅ |
| C13 | `STATUS.md` atualizado | ✅ |

Detalhes completos em [`PLANO-CORRECOES.md`](PLANO-CORRECOES.md).

---

## 🚨 BLOQUEIOS ATIVOS

Nenhum. API CEMADEN é testada em runtime; se falhar, o pipeline cai
automaticamente para Open-Meteo Archive sem quebrar.

---

## 🗂️ ESTRUTURA DE ARQUIVOS

```
TOPCLIMABC/
├── ARCHITECTURE.md          (Planejamento)
├── STATUS.md                (este arquivo)
├── PLANO-CORRECOES.md       (sprint 2026-04-18)
├── TOPCLIMABC.bat           (Atalho 1-Clique)
├── data/                    (Base local: realidade, previsões, auditoria)
├── scripts/                 (Backend Python)
│   └── utils/
│       ├── cemaden.py       (NOVO — fonte primária pluviômetro)
│       ├── score.py         (matriz 5×5, volume −5/mm, peso madrugada)
│       ├── classificacao.py (classes unificadas)
│       └── supabase_api.py  (overrides manuais)
├── docs/                    (Site público + dados.json/ranking.json)
└── docs-projeto/            (Manuais extras)
```
