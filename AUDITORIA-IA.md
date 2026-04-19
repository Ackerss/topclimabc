# 🔍 AUDITORIA PARA IAs — TOPCLIMABC

> **Leia este arquivo ANTES de tentar "consertar" qualquer coisa neste projeto.**
>
> Este documento responde 3 perguntas: (1) **o que está funcionando hoje?**, (2) **o que NÃO está e por quê?**, (3) **o que NÃO se deve tentar fazer** (armadilhas em que IAs anteriores caíram).
>
> Última auditoria completa: **2026-04-19** por Claude Opus 4.7.
> O dono do projeto **não é programador** — não espere que ele valide decisões técnicas. Decida você, documente aqui, e siga em frente.

---

## ✅ ESTADO ATUAL: O APP ESTÁ 100% FUNCIONAL

Testado manualmente em 2026-04-19, nessa ordem:

| Etapa | Comando | Resultado |
|-------|---------|-----------|
| 1. Coleta de previsões | `python -m scripts.coletar_previsoes` | ✅ Snapshot salvo em `data/previsoes/snapshot_2026-04-19.json` |
| 2. Coleta de realidade | `python -m scripts.coletar_realidade` | ✅ Fallback Open-Meteo ativado (CEMADEN fora do ar) |
| 3. Auditoria | `python -m scripts.auditar` | ✅ 24 comparações registradas em `historico.json` |
| 4. Sincronização frontend | `python -m scripts.gerar_frontend` | ✅ `dados.json`, `ranking.json`, `estacoes.json`, `todas_realidades.json` regenerados |
| 5. GitHub Actions | `.github/workflows/atualizacao_diaria.yml` | ✅ Rodando diariamente às 12:00 UTC |
| 6. GitHub Pages | `docs/` publicado | ✅ https://ackerss.github.io/topclimabc/ |
| 7. Supabase (validação manual) | Insert em `topclimabc_validacoes` com `override=true` | ✅ Frontend → tabela → backend → JSONs |

**Não há bloqueio crítico.** Tudo que precisa funcionar, funciona.

---

## 🔴 O QUE NÃO FUNCIONA — E POR QUÊ

### 1. CEMADEN PED (fonte primária de pluviômetro)

**Estado:** 🔴 Fora do ar / bloqueando acesso.

**Evidência:**
- Acesso manual a https://sws.cemaden.gov.br/PED/ retorna "Forbidden" (screenshot tirado pelo usuário em 2026-04-19)
- Chamadas programáticas a `sws.cemaden.gov.br/PED/rest/pcds-cadastro/estacoes?municipio={ibge}` retornam **HTTP 400 Bad Request**
- Comportamento reproduzível em ambos municípios (BC `4202008`, Itajaí `4208203`)

**Causa raiz:** problema do **servidor do governo**, não do código. O CEMADEN PED **sempre exigiu autenticação via token** (documentação antiga deste projeto dizia "sem chave, acesso livre" — era **factualmente falso**).

**Workaround ativo:** `scripts/coletar_realidade.py` detecta a falha e cai automaticamente para Open-Meteo Archive (best_match) — reanálise ERA5-Land + assimilação de estações observacionais. É a segunda melhor fonte disponível e está operacional.

**Para resolver (quando possível):**
1. Usuário se cadastra em https://sws.cemaden.gov.br/PED/login (quando o portal voltar)
2. Aguarda aprovação (costuma levar 1–7 dias)
3. Recebe um token
4. Adiciona `CEMADEN_TOKEN=<valor>` no `.env` local + GitHub Secret
5. Pronto — o cliente em `scripts/utils/cemaden.py` já sabe usar o token, sem mudança de código

### 2. INMET API (fallback alternativo)

**Estado:** ⚠️ Timeout nos testes de 2026-04-19.

**Evidência:** `curl -m 15 https://apitempo.inmet.gov.br/estacao/...` retornou "Connection was reset" ou 0 bytes.

**Causa provável:** instabilidade intermitente do serviço. Itajaí tem a estação A868 cadastrada em `scripts/config.py:45` mas nunca foi integrada no pipeline.

**Decisão:** não integrar agora. Open-Meteo Archive já cobre o caso. Reconsiderar se o CEMADEN continuar fora por semanas.

### 3. Banco Supabase "Craquepedia" (mencionado em docs antigas)

**Estado:** ❌ Não existe mais / foi substituído.

**Evidência:** `docs/index.html:773` usa `https://jfjrzkjzfxnyhexwhoby.supabase.co` (projeto KANBAN), não `ndqgvqajdjrzbwgsmmoe` (Craquepedia).

**Ação já tomada em 2026-04-19:** `CREDENCIAIS.md` e `SUPABASE-COMPARTILHADO.md` foram corrigidos para refletir a realidade (projeto KANBAN).

---

## 🚫 APIs TESTADAS E REJEITADAS — NÃO TENTE DE NOVO

### ❌ SGB ArcGIS FeatureServer (sugerido por uma IA externa em 2026-04-18)

**Endpoint sugerido:** `https://geoportal.sgb.gov.br/server/rest/services/Cemaden/FeatureServer/0/query`

**Por que NÃO usar:**
- Cobre APENAS **Alagoas/Maceió**, não Santa Catarina (`fullExtent: xmin=-36.5, ymin=-10.3`)
- Dados congelados em **setembro de 2019** (6+ anos desatualizados)
- Campo `uf: "AL"` em todos os registros retornados
- Keywords do serviço: `"Cemaden,Maceió,Pluviométrico"`

**Lição:** IAs externas alucinam APIs. **Sempre teste com `curl` e inspecione o extent + data antes de integrar.** O padrão diagnóstico:

```bash
curl -s "<endpoint>?f=json" | python -c "import sys, json; d=json.load(sys.stdin); print('Extent:', d.get('fullExtent')); print('Keywords:', d.get('documentInfo', {}).get('Keywords'))"
```

Se o `fullExtent` não cobre latitude ~-27 e longitude ~-48, a API não serve para BC/Itajaí.

### ❌ `mapainterativo.cemaden.gov.br/dados/getEstacoes.php` (tentativa 2026-04-18)

**Por que NÃO usar:** retorna HTML 404 ("Página não encontrada"). O subdomínio `mapainterativo.cemaden.gov.br` existe, mas não expõe esse endpoint PHP.

---

## 📏 REGRAS DE NEGÓCIO — PONTOS QUE IAs COMETEM ERRO

Essas regras estão **ativas no código** e cada uma delas já custou uma sessão de correção. Se for mexer, **leia o histórico primeiro** (`PLANO-CORRECOES.md`).

### 1. Classificação de chuva — vocabulário unificado

Os únicos valores válidos de `classificacao` em QUALQUER parte do sistema:

| Nome | Intervalo (mm) | Label UI |
|------|---------------|----------|
| `seco` | `[0.0, 0.1)` | Seco |
| `garoa` | `[0.1, 2.6)` | Garoa |
| `moderada` | `[2.6, 10.1)` | Moderada |
| `forte` | `[10.1, 25.1)` | Forte |
| `intensa` | `[25.1, ∞)` | Intensa |

**NÃO use** `sem_chuva`, `fraca`, `muito_forte`, `chuvisco`, `leve`, etc. Foram removidos. Existe também `scripts/migrar_classes.py` (one-shot idempotente) caso apareça dado histórico com nomes antigos.

**Fontes de verdade:** `scripts/config.py:108` (`CLASSIFICACOES`), `scripts/utils/classificacao.py` (função `classificar_chuva`), `docs/index.html` (função `formatClass`).

### 2. Score — fórmula específica

Em `scripts/utils/score.py`:

- **Matriz 5×5 gradual** (não binária) de acerto de classificação → ver dict `MATRIZ_CLASSE`
- **Score de volume:** `max(0, 100 - (diferença_mm * 5))` → **5 pontos por mm**, não 10
- **Score final do período:** `60% classificação + 40% volume`
- **Score do dia:** média ponderada dos 4 períodos, com **madrugada = 0.5×** (outros = 1.0×)
- **Persistência** (`persistencia`) é **baseline obrigatório** no ranking — se um modelo perde pra ela, é inútil

### 3. Hierarquia de fontes de realidade — regra de ouro

Em ordem de prioridade (vence quem aparecer primeiro):

1. **Manual (usuário)** → registros em `topclimabc_validacoes` com `override=true`
2. **CEMADEN PED** → pluviômetro físico (hoje indisponível — ver acima)
3. **Open-Meteo Archive best_match** → reanálise ERA5-Land (fonte ativa)
4. **Open-Meteo Historical Forecast** → fallback de emergência
5. **sem_dados** → NUNCA invente 0mm quando não há dado

**Nunca mude essa ordem sem falar com o dono.**

### 4. Snapshot é imutável

A previsão coletada em um dia NUNCA pode ser alterada retroativamente. Se precisa reprocessar, use `scripts/reprocessar_historico.py` (só mexe em realidade, não em previsões).

### 5. Supabase tem prefixo obrigatório

Só existe/pode existir a tabela `topclimabc_validacoes`. Qualquer tabela nova DEVE começar com `topclimabc_`. O banco é emprestado do projeto KANBAN.

---

## 🧪 COMO VERIFICAR QUE TUDO CONTINUA FUNCIONANDO

```bash
# 1. Instalar dependências (inclui tzdata — obrigatório no Windows)
pip install -r scripts/requirements.txt

# 2. Rodar pipeline completa (ou duplo-clique em TOPCLIMABC.bat)
python -m scripts.coletar_previsoes
python -m scripts.coletar_realidade
python -m scripts.auditar
python -m scripts.gerar_frontend

# 3. Conferir saídas
ls docs/*.json   # deve ter: dados.json, ranking.json, estacoes.json, todas_realidades.json
```

**Sinais de saúde:**
- Cada script imprime `[OK]` ou `[FALLBACK] Archive best_match: X.Xmm` — ambos são aceitáveis.
- `total_dia` em `data/realidade/realidade_*.json` é um número realista (0–80mm tipicamente).
- `docs/ranking.json` tem 5+ modelos listados (GFS, ECMWF, ICON, OWM, best_match, persistencia).

**Sinais de problema (investigar):**
- `ModuleNotFoundError: No module named 'tzdata'` → reinstale deps
- `total_dia: null` em todos os locais → Open-Meteo caiu também (raro)
- `SUPABASE_ANON_KEY não configurada` aparece mas pipeline continua → normal em execução local (só lê overrides manuais quando a key está no .env)

---

## 📋 HISTÓRICO DE SESSÕES DE IA — O QUE CADA UMA FEZ

| Data | IA | O que fez |
|------|----|-----------|
| 2026-04-15 a 2026-04-16 | Gemini (Antigravity) / Claude Sonnet 4.6 | Fase 1 + Fase 2: frontend e backend iniciais |
| 2026-04-16 | Claude Sonnet 4.6 | Fase 3 parcial: Supabase KANBAN + GHA workflow |
| 2026-04-18 | Claude Opus 4.7 | **Sprint de correções 2026-04-18**: auditoria profunda + 13 issues resolvidas (ver `PLANO-CORRECOES.md`). Reprocessamento histórico. Cliente CEMADEN criado. |
| 2026-04-19 | Claude Opus 4.7 | Documentação sincronizada com o código real. Criou este arquivo. Confirmou app 100% funcional. |

---

## ⚠️ ARMADILHAS QUE IAs JÁ CAÍRAM NESTE PROJETO

1. **"Vou mockar os dados pra testar"** — NÃO. Qualquer dado mockado vira commit em `docs/*.json` e engana o usuário. Use Open-Meteo real ou nada.

2. **"Vou consertar o CEMADEN forçando o endpoint"** — NÃO. O servidor está fora do ar do lado deles. O fallback existe exatamente por isso.

3. **"Vou criar um novo projeto Supabase em vez de reutilizar"** — NÃO. O plano gratuito do Supabase limita a 2 projetos por conta do usuário, e ele já usa os 2 slots. Usar o KANBAN com prefixo é a decisão aprovada.

4. **"Vou refatorar todos os nomes de classes pra ficarem em inglês"** — NÃO. As classes em português estão na UI, no backend e no banco. Mudar tudo quebraria 100% dos dados históricos.

5. **"Vou amendar o último commit pra não poluir o histórico"** — NÃO. Sempre crie commits novos. O `docs/*.json` é atualizado pelo GHA diariamente; reescrever histórico atrapalha.

6. **"A IA anterior disse que tem uma API pública de CEMADEN"** — Teste com `curl` antes de confiar. A única API real pública que cobre BC/Itajaí hoje é a **Open-Meteo Archive**.

---

## 🎯 RESUMO EXECUTIVO (PARA DONO NÃO-TÉCNICO)

- **App funciona 100%.** Coleta, audita, publica. Automatizado via GitHub Actions.
- **CEMADEN tá fora do ar**, mas o app tem **"plano B" automático** que usa dados de satélite europeus com validação por estações reais (Open-Meteo Archive). Os números são confiáveis.
- **Quando o CEMADEN voltar**, basta colar o token no arquivo `.env` e ele volta a ser a fonte principal — sem precisar mexer em código.
- **Nada está inventado.** Se não há dado pra um dia, o sistema mostra `null` explicitamente (não um zero fictício).
- **Validação manual sua é prioridade absoluta** sobre qualquer fonte automática.

Qualquer IA futura que abrir este projeto deve **ler este arquivo primeiro** e **não tentar "melhorar" o sistema sem entender essas armadilhas**.
