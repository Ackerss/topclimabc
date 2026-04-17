# 🔐 CREDENCIAIS DO PROJETO TOPCLIMABC

> **ATENÇÃO:** Os valores reais das chaves NÃO devem estar neste arquivo em produção.
> Eles devem estar configurados como **GitHub Secrets** no repositório.

## Chaves de API

### OpenWeatherMap
| Item | Valor |
|------|-------|
| **Nome no OWM** | TOPCLIMABC |
| **API Key** | `d642bd544942199ff3b862927da91923` |
| **GitHub Secret Name** | `OWM_API_KEY` |
| **Docs** | https://openweathermap.org/api |
| **Limite Free** | 1000 calls/dia, 60 calls/min |

### Supabase (Projeto Craquepedia)
| Item | Valor |
|------|-------|
| **Project ID** | `ndqgvqajdjrzbwgsmmoe` |
| **URL** | `https://ndqgvqajdjrzbwgsmmoe.supabase.co` |
| **Anon Key** | *(obter via dashboard Supabase → Settings → API)* |
| **GitHub Secret Names** | `SUPABASE_URL` e `SUPABASE_KEY` |
| **⚠️ VER** | `docs-projeto/SUPABASE-COMPARTILHADO.md` |

### APIs Sem Chave (Grátis)
| Serviço | Limite | Notas |
|---------|--------|-------|
| **Open-Meteo** | 10,000 calls/dia | Sem chave necessária |
| **CEMADEN PED** | Sem limite documentado | Sem chave necessária |

## Configuração no GitHub

1. Acesse: `https://github.com/Ackerss/topclimabc/settings/secrets/actions`
2. Clique "New repository secret"
3. Adicione cada secret listado acima

## Configuração Local (para desenvolvimento)

Criar arquivo `.env` na raiz (está no `.gitignore`):

```env
OWM_API_KEY=d642bd544942199ff3b862927da91923
SUPABASE_URL=https://ndqgvqajdjrzbwgsmmoe.supabase.co
SUPABASE_KEY=<anon_key_do_supabase>
```
