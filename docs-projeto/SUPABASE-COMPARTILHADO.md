# ⚠️ AVISO IMPORTANTE: SUPABASE COMPARTILHADO

## Projeto Supabase Utilizado

Este projeto (TOPCLIMABC) utiliza o banco de dados Supabase do projeto **"craquepedia"** (organização: Acker) por ser um projeto gratuito existente na conta.

| Item | Valor |
|------|-------|
| **Nome do Projeto Supabase** | craquepedia |
| **Organização** | Acker |
| **Project ID** | `ndqgvqajdjrzbwgsmmoe` |
| **Region** | us-east-1 |
| **URL** | `https://ndqgvqajdjrzbwgsmmoe.supabase.co` |

## REGRAS OBRIGATÓRIAS

### 1. Prefixo de Tabelas
TODAS as tabelas criadas para o TOPCLIMABC **DEVEM** ter o prefixo `topclimabc_`.

**Exemplo:**
- ✅ `topclimabc_validacoes`
- ✅ `topclimabc_configuracoes`
- ❌ `validacoes` (SEM prefixo — PROIBIDO)

### 2. Não Modificar Dados Existentes
O banco contém tabelas de outros projetos (Craquepedia). **NUNCA:**
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
O plano gratuito do Supabase permite apenas **2 projetos ativos** por conta. Como já havia 2 ativos, optou-se por reutilizar o projeto Craquepedia (que estava INATIVO) ao invés de criar um novo.

## Tabelas do TOPCLIMABC

### `topclimabc_validacoes`
Armazena registros manuais do usuário sobre o clima real.

```sql
CREATE TABLE topclimabc_validacoes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    periodo TEXT NOT NULL CHECK (periodo IN ('madrugada', 'manha', 'tarde', 'noite')),
    local TEXT NOT NULL CHECK (local IN ('balneario_camboriu', 'itajai')),
    classificacao TEXT NOT NULL CHECK (classificacao IN ('seco', 'garoa', 'moderada', 'forte', 'intensa')),
    nota TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```
