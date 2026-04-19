# 🔐 CREDENCIAIS DO PROJETO TOPCLIMABC

> **ATENÇÃO:** Os valores reais das chaves NÃO devem estar neste arquivo em produção.
> Eles devem estar configurados como **GitHub Secrets** no repositório.
> Este doc foi auditado em 2026-04-19 — está sincronizado com o código real.

## Chaves de API

### OpenWeatherMap
| Item | Valor |
|------|-------|
| **Nome no OWM** | TOPCLIMABC |
| **API Key** | `d642bd544942199ff3b862927da91923` |
| **GitHub Secret Name** | `OWM_API_KEY` |
| **Docs** | https://openweathermap.org/api |
| **Limite Free** | 1000 calls/dia, 60 calls/min |

### Supabase (Projeto KANBAN emprestado)
| Item | Valor |
|------|-------|
| **Project ID** | `jfjrzkjzfxnyhexwhoby` |
| **URL** | `https://jfjrzkjzfxnyhexwhoby.supabase.co` |
| **Anon Key** | Incorporada no `docs/index.html:774` (pública por natureza). Para backend Python, usar GitHub Secret `SUPABASE_ANON_KEY` |
| **GitHub Secret Name** | `SUPABASE_ANON_KEY` |
| **⚠️ VER** | `docs-projeto/SUPABASE-COMPARTILHADO.md` |

> **Nota:** o `CREDENCIAIS.md` antigo apontava para o projeto `ndqgvqajdjrzbwgsmmoe` (Craquepedia). Isso estava desatualizado — o projeto realmente em uso é o KANBAN (`jfjrzkjzfxnyhexwhoby`), conforme `docs/index.html:773` e `.github/workflows/atualizacao_diaria.yml:16`.

### APIs Sem Chave (acesso livre)
| Serviço | Status real (auditado 2026-04-19) | Notas |
|---------|-----------------------------------|-------|
| **Open-Meteo Forecast** | ✅ Funcionando, livre | 10.000 calls/dia |
| **Open-Meteo Archive (best_match)** | ✅ Funcionando, livre | Reanálise ERA5-Land — fonte de realidade atualmente ativa |
| **Open-Meteo Historical Forecast** | ✅ Funcionando, livre | Fallback de último recurso |

### CEMADEN PED — REQUER CADASTRO (NÃO É LIVRE)
| Item | Valor |
|------|-------|
| **Endpoint** | `https://sws.cemaden.gov.br/PED/rest/` |
| **Estado (2026-04-19)** | 🔴 **Portal retorna "Forbidden"** — serviço do governo fora do ar ou bloqueando acesso não autenticado |
| **Registro exigido?** | **SIM** — não é API livre. Requer cadastro em https://sws.cemaden.gov.br/PED/login e aprovação manual |
| **Env var** | `CEMADEN_TOKEN` (opcional; se vazio, pipeline usa Open-Meteo Archive como fallback automático) |
| **GitHub Secret Name** | `CEMADEN_TOKEN` (ainda não configurado — aguardando cadastro oficial) |

> **Informação importante para IAs:** versões antigas desta doc diziam "CEMADEN sem chave, acesso livre". Isso era **factualmente incorreto**. O CEMADEN PED sempre exigiu autenticação. O código `scripts/utils/cemaden.py` tenta acessar sem token (modo "tentativa pública"), mas o servidor retorna 400/403 atualmente. O sistema inteiro continua funcionando via fallback Open-Meteo Archive — ver `scripts/coletar_realidade.py`.

## Configuração no GitHub

1. Acesse: `https://github.com/Ackerss/topclimabc/settings/secrets/actions`
2. Clique "New repository secret"
3. Adicione os secrets abaixo:
   - `OWM_API_KEY` (obrigatório)
   - `SUPABASE_ANON_KEY` (obrigatório para backend ler overrides manuais)
   - `CEMADEN_TOKEN` (opcional — quando o cadastro for aprovado)

## Configuração Local (para desenvolvimento)

Criar arquivo `.env` na raiz (está no `.gitignore`):

```env
OWM_API_KEY=d642bd544942199ff3b862927da91923
SUPABASE_URL=https://jfjrzkjzfxnyhexwhoby.supabase.co
SUPABASE_ANON_KEY=<anon_key_lida_de_docs/index.html:774_ou_dashboard>
# CEMADEN_TOKEN=  # opcional — deixe vazio até o cadastro ser aprovado
```
