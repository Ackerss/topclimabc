# ✅ LISTA DE TAREFAS — TOPCLIMABC

> **Auditado em 2026-04-19.** Sincronizado com o código real após sprint de correções.
> Para detalhamento completo do que funciona e do que não funciona, veja `AUDITORIA-IA.md`.

---

## 🟢 CONCLUÍDO

### 🎨 Frontend (SPA Moderna)
- [x] Interface em Cards (Dark Mode por padrão)
- [x] Sistema de 4 Abas (Auditoria, Ranking, Histórico, Estações)
- [x] Seleção dinâmica Balneário Camboriú / Itajaí
- [x] PWA Ready (instalável no Android/iPhone)
- [x] Validação manual via modal com persistência no Supabase
- [x] Banner "Ranking em formação" quando amostras < 7
- [x] Labels honestos sobre a fonte real dos dados
- [x] Classes de chuva unificadas (seco/garoa/moderada/forte/intensa)

### 🐍 Backend Python (Motor de Auditoria)
- [x] **Coleta Diária de Previsões:** Open-Meteo (4 modelos) + OpenWeatherMap
- [x] **Hierarquia de fontes de realidade** (Manual → CEMADEN → Archive → Hist)
- [x] **Cliente CEMADEN PED** (`scripts/utils/cemaden.py`) — pronto para quando o serviço voltar
- [x] **Motor de Pontuação** — Matriz 5×5 gradual + volume −5/mm + peso madrugada 0.5×
- [x] **Persistência como baseline** (ranking mostra linha de corte "amanhã = hoje")
- [x] **Sincronização de Frontend** — gera `dados.json`, `ranking.json`, `estacoes.json`, `todas_realidades.json`
- [x] **Migração de classes** (`scripts/migrar_classes.py`) — one-shot idempotente já executado em 2026-04-18
- [x] **Timezone correto** — conversões UTC→BRT para OWM
- [x] **Atalho de Uso:** Arquivo `TOPCLIMABC.bat` para execução local

### ☁️ Cloud / Automação
- [x] **Supabase integrado** — projeto KANBAN (`jfjrzkjzfxnyhexwhoby`), tabela `topclimabc_validacoes`
- [x] **Override manual** — frontend envia `override=true`, backend lê e aplica prioridade
- [x] **GitHub Actions** — `.github/workflows/atualizacao_diaria.yml` roda 12:00 UTC todo dia
- [x] **GitHub Pages** — `docs/` publicado em https://ackerss.github.io/topclimabc/
- [x] **Commit automático** de dados atualizados pelo workflow

---

## 🟡 OPCIONAL / DESEJÁVEL (NÃO BLOQUEIA O APP)

### Fonte primária CEMADEN (quando possível)
- [ ] Aguardar cadastro do usuário em https://sws.cemaden.gov.br/PED/login (atualmente retorna "Forbidden" — problema do lado do governo)
- [ ] Quando aprovado, adicionar `CEMADEN_TOKEN` no `.env` local e nos GitHub Secrets
- [ ] O cliente `scripts/utils/cemaden.py` já está pronto para usar o token — nenhuma mudança de código será necessária

### INMET como fonte adicional
- [ ] Avaliar integração com `apitempo.inmet.gov.br` (Itajaí tem estação A868 cadastrada)
- [ ] API INMET deu timeout em testes recentes — acompanhar status antes de integrar

---

## 🚨 BLOQUEIOS ATIVOS

**Nenhum bloqueio crítico.** O app está 100% funcional — com fallback automático para Open-Meteo Archive quando o CEMADEN está fora do ar (que é o estado atual).

---

## 📂 ESTRUTURA ATUAL

- `docs/`: O site (HTML, JS, Dados gerados).
- `scripts/`: O motor Python (coleta, auditoria, sincronização).
- `scripts/utils/`: Utilidades (score, classificação, clients API).
- `data/`: Base de dados local (previsões, realidade, auditoria).
- `docs-projeto/`: Manuais e guias técnicos.
- `.github/workflows/`: Automação CI/CD.
