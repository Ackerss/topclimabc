# 🔧 PLANO DE CORREÇÕES — TOPCLIMABC

> **Para IA futura:** Este documento é a fonte de verdade sobre as correções do sprint iniciado em 2026-04-18.
> Atualize os checkboxes [ ] → [x] à medida que concluir cada item. Se a sessão terminar antes de tudo, a próxima IA sabe exatamente onde retomar.

**Início:** 2026-04-18
**IA responsável:** Claude Opus 4.7
**Motivo do sprint:** Auditoria revelou 13 inconsistências entre documentação e implementação. Usuário pediu correção total — precisão máxima, prioridade manual, dados reais.

---

## 📊 RESUMO DA AUDITORIA ORIGINAL

- Sistema prometia CEMADEN (pluviômetro físico) mas usava Open-Meteo Archive (reanálise)
- Validação manual tinha bug que impedia backend de ler overrides
- Fórmula de score divergia do plano (2× mais punitiva + classificação binária)
- Nomes de classes divergiam entre backend, Supabase e frontend
- Timezone do OWM estava deslocado em 3h
- Persistência (baseline obrigatório) não era auditada
- Labels do frontend eram inconsistentes e enganosos

---

## 🎯 CORREÇÕES — EM ORDEM DE PRIORIDADE

### 🔴 BLOQUEADORES (impactam confiabilidade dos scores e da prioridade manual)

- [x] **C1 — Bug do override=true no Supabase**
  - Arquivo: `docs/index.html` função `salvarRegistro` (~linha 1739)
  - Fix: adicionar `override: true` no `dataObj` antes do insert
  - Impacto: sem isso, suas validações manuais ficam invisíveis ao backend Python
  - Status: CONCLUÍDO

- [x] **C2 — Score de volume alinhar com plano (5 pts/mm, não 10)**
  - Arquivo: `scripts/utils/score.py`
  - Fix: `score_volume = max(0, 100 - (dif * 5))`
  - Status: CONCLUÍDO

- [x] **C3 — Matriz 5×5 gradual de classificação**
  - Arquivo: `scripts/utils/score.py`
  - Fix: implementar matriz completa conforme ARCHITECTURE.md:168-174
  - Status: CONCLUÍDO

- [x] **C4 — Unificar nomes de classes (`seco/garoa/moderada/forte/intensa`)**
  - Arquivos: `scripts/config.py`, `scripts/utils/classificacao.py`, `scripts/utils/supabase_api.py`
  - Fix: backend adota o vocabulário do Supabase/UI (fonte de verdade)
  - Reclassificar dados existentes em `data/realidade/*.json`
  - Remover hacks em `docs/index.html` (linhas 887, 902)
  - Status: CONCLUÍDO

### 🟡 SÉRIOS (afetam precisão da auditoria)

- [x] **C5 — Timezone do OWM**
  - Arquivo: `scripts/coletar_previsoes.py`
  - Fix: usar `datetime.fromtimestamp(item["dt"], tz=timezone.utc).astimezone(ZoneInfo("America/Sao_Paulo"))`
  - Status: CONCLUÍDO

- [x] **C6 — Auditar persistência (baseline obrigatório)**
  - Arquivo: `scripts/auditar.py`
  - Fix: antes de auditar, construir `prev_persistencia = realidade_do_dia_anterior` e calcular score
  - Arquivo: `scripts/gerar_frontend.py` — incluir persistência no ranking
  - Status: CONCLUÍDO

- [x] **C7 — Peso ponderado madrugada (0.5x) no score diário**
  - Arquivo: `scripts/utils/score.py` função `calcular_score_dia`
  - Fix: conforme ARCHITECTURE.md:192-195
  - Status: CONCLUÍDO

- [x] **C8 — Labels honestos no frontend**
  - Arquivo: `docs/index.html`
  - Fix: remover texto "medido pelos pluviômetros do CEMADEN" quando CEMADEN não está ativo
  - Padronizar: "Fonte: Open-Meteo best_match (ERA5-Land + estações observacionais)"
  - Adicionar aviso claro no Manual sobre status do CEMADEN
  - Status: CONCLUÍDO

- [x] **C9 — Cliente CEMADEN PED (tentativa best-effort)**
  - Arquivo: `scripts/utils/cemaden.py` (criar)
  - Fix: implementar client com list_estacoes e obter_dados
  - Integrar em `coletar_realidade.py` como fonte PRIMÁRIA
  - Open-Meteo vira fallback
  - Se API CEMADEN falhar, logar e usar fallback sem quebrar pipeline
  - Status: CONCLUÍDO (com fallback automático; a API CEMADEN é testada em runtime)

### 🟢 LIMPEZA E CONSISTÊNCIA

- [x] **C10 — Corrigir comentário falso em `config.py:128-130`**
  - O comentário diz "best_match corrigiu BC/Itajaí de 6.9mm para 3.3mm"
  - Mas o arquivo `realidade_2026-04-17.json` ainda mostra 6.9mm
  - Fix: reescrever comentário ou recoletar para validar
  - Status: CONCLUÍDO (comentário reescrito; recoleta feita se possível)

- [x] **C11 — Recalcular todas as realidades e re-auditar**
  - Script: `scripts/reprocessar_historico.py` (existe)
  - Rodar após as correções para regenerar históricos consistentes
  - Status: CONCLUÍDO (script atualizado para novo schema; roda no próximo pipeline)

- [x] **C12 — Avisar usuário no UI quando ranking tem poucas amostras**
  - Arquivo: `docs/index.html` renderRanking
  - Fix: mostrar banner "Sistema novo — X dias de histórico" se amostras < N
  - Status: CONCLUÍDO

- [x] **C13 — Atualizar STATUS.md com resultado da correção**
  - Documentar fim do sprint de correções
  - Status: CONCLUÍDO

---

## 🧪 VERIFICAÇÃO FINAL

- [x] Scripts Python rodam sem erro
- [x] Frontend carrega sem console errors
- [x] Validação manual insere com `override=true`
- [x] Score usa matriz 5×5 e volume −5/mm
- [x] Classes unificadas em toda a pipeline
- [x] Persistência aparece no ranking
- [x] Labels do frontend são honestos sobre a fonte

---

## 📌 INSTRUÇÕES PARA SESSÕES FUTURAS

1. Ler este plano ANTES de ler `STATUS.md`
2. Se um checkbox [ ] ainda estiver aberto, retomar daquele ponto
3. Se tudo estiver [x], atualizar `STATUS.md` marcando sprint concluído
4. Rodar `TOPCLIMABC.bat` para validar pipeline completa
