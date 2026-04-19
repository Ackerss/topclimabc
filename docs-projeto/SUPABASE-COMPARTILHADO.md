# ⚠️ AVISO IMPORTANTE: SUPABASE COMPARTILHADO

> **Auditado em 2026-04-19** — este doc foi sincronizado com o código real (`docs/index.html:773`, `.github/workflows/atualizacao_diaria.yml:16`, `scripts/utils/supabase_api.py:11`).

## Projeto Supabase Utilizado

Este projeto (TOPCLIMABC) utiliza o banco de dados Supabase do projeto **"KANBAN"** por ser um projeto gratuito existente na conta do usuário.

| Item | Valor |
|------|-------|
| **Nome do Projeto Supabase** | KANBAN (emprestado) |
| **Project ID** | `jfjrzkjzfxnyhexwhoby` |
| **URL** | `https://jfjrzkjzfxnyhexwhoby.supabase.co` |

> **Histórico:** versões antigas desta documentação citavam o projeto "craquepedia" (`ndqgvqajdjrzbwgsmmoe`). Essa informação era obsoleta — a migração para o KANBAN ocorreu quando o Craquepedia foi pausado. O código atual usa exclusivamente `jfjrzkjzfxnyhexwhoby`.

## REGRAS OBRIGATÓRIAS

### 1. Prefixo de Tabelas
TODAS as tabelas criadas para o TOPCLIMABC **DEVEM** ter o prefixo `topclimabc_`.

**Exemplo:**
- ✅ `topclimabc_validacoes`
- ❌ `validacoes` (SEM prefixo — PROIBIDO)

### 2. Não Modificar Dados Existentes
O banco contém tabelas do projeto KANBAN. **NUNCA:**
- Deletar tabelas que não comecem com `topclimabc_`
- Modificar dados de outras tabelas
- Alterar políticas RLS de outras tabelas
- Modificar funções/triggers existentes

### 3. RLS (Row Level Security)
Todas as tabelas `topclimabc_*` devem ter RLS ativado com:
- `INSERT` permitido para `anon` (para o frontend enviar dados)
- `SELECT` permitido para `anon` (para o frontend ler dados)
- `UPDATE` e `DELETE` **bloqueados** para `anon`

### 4. Motivo do Compartilhamento
O plano gratuito do Supabase permite apenas **2 projetos ativos** por conta. Como já havia 2 ativos, optou-se por reutilizar o projeto KANBAN (que estava parcialmente livre) ao invés de criar um novo.

## Tabelas do TOPCLIMABC

### `topclimabc_validacoes`
Armazena validações manuais do usuário sobre o clima real observado. **É a fonte de verdade de maior prioridade do sistema** — sobrescreve qualquer fonte automática (CEMADEN, Open-Meteo, etc).

**Schema real (auditado em `docs/index.html:1796-1805`):**

```sql
CREATE TABLE topclimabc_validacoes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data DATE NOT NULL,
    hora TEXT NOT NULL,                    -- "HH:MM" local BRT
    periodo TEXT NOT NULL CHECK (periodo IN ('madrugada', 'manha', 'tarde', 'noite')),
    local TEXT NOT NULL CHECK (local IN ('balneario_camboriu', 'itajai')),
    classificacao TEXT NOT NULL CHECK (classificacao IN ('seco', 'garoa', 'moderada', 'forte', 'intensa')),
    nota TEXT,
    timestamp TIMESTAMPTZ,                 -- ISO do momento do registro (vem do frontend)
    override BOOLEAN DEFAULT true,         -- SEMPRE true para registros do frontend — o backend só lê registros com override=true
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Importante:** a coluna `override` existe e é crítica. O backend Python filtra registros com `override=eq.true` (ver `scripts/utils/supabase_api.py:45`). Em versões antigas o frontend não mandava esse campo, fazendo com que o backend ignorasse as validações manuais silenciosamente. Isso foi corrigido no sprint 2026-04-18.

### Como as validações manuais entram no fluxo

```
Usuário clica "Estava chovendo forte de manhã" no frontend
  ↓
docs/index.html insere linha com override=true em topclimabc_validacoes
  ↓
GitHub Actions roda (12:00 UTC diário)
  ↓
scripts/utils/supabase_api.buscar_overrides_manuais() lê todos com override=true
  ↓
scripts/gerar_frontend.py sobrescreve a fonte automática pela manual
  ↓
docs/todas_realidades.json passa a refletir a realidade validada pelo usuário
```
