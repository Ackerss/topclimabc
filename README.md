# 🌧️ TOPCLIMABC

**Quem acerta a chuva em Balneário Camboriú e Itajaí?**

App Web que monitora previsões de chuva de múltiplos modelos meteorológicos, compara com dados de referência (pluviômetros físicos do CEMADEN quando disponíveis, ou reanálise ERA5-Land como fallback), e gera um ranking confiável para você saber em qual app de previsão do tempo confiar.

## 🎯 O Que Este Projeto Faz

1. **Coleta diária** de previsões de 5 modelos meteorológicos (GFS, ECMWF, ICON, OpenWeatherMap, Best Match)
2. **Congela snapshots** — a previsão de hoje para daqui 7 dias fica salva e imutável
3. **Coleta dados de realidade** com hierarquia de fontes (ver seção "Fonte de realidade")
4. **Audita automaticamente** — compara previsão vs. realidade com score gradual (0-100)
5. **Gera ranking** — qual modelo/app acerta mais para 1 dia, 3 dias, 7 dias, 15 dias
6. **Aceita validação manual** do usuário (via Supabase) com prioridade absoluta sobre fontes automáticas

## 🌡️ Fonte de realidade (hierarquia)

Auditado em 2026-04-19. O sistema tenta, em ordem:

| Prioridade | Fonte | Estado atual | Status retornado |
|------------|-------|--------------|------------------|
| 1 (manual) | Validação do usuário via Supabase | ✅ Funcional | `override=true` |
| 2 (auto) | CEMADEN PED (pluviômetro físico) | 🔴 Servidor retorna "Forbidden" — fora do ar/restrito | `completo` |
| 3 (auto) | Open-Meteo Archive best_match (ERA5-Land + estações) | ✅ Funcionando | `provisorio_reanalise` |
| 4 (auto) | Open-Meteo Historical Forecast | ✅ Funcionando (último recurso) | `provisorio` |

**Hoje, na prática,** a fonte automática ativa é o **Open-Meteo Archive** (reanálise). Assim que o usuário obtiver um token CEMADEN oficial (`CEMADEN_TOKEN` no `.env`), a fonte primária passa automaticamente para pluviômetro físico — sem precisar mudar nenhuma linha de código.

## 🔗 Acesso

🌐 **https://ackerss.github.io/topclimabc/**

## 🧭 Qual App Usar?

| Modelo Auditado | Apps que Usam |
|-----------------|---------------|
| ECMWF IFS | Windy, Apple Weather |
| GFS | Weather.com, The Weather Channel |
| ICON | Windy (opção), Bright Sky |
| OpenWeatherMap | OpenWeatherMap app |
| Best Match | Open-Meteo App (blend automático) |
| Persistência (baseline) | — (linha de corte: "amanhã = hoje") |

Veja o ranking completo no app.

## 📖 Documentação

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — Plano completo de arquitetura
- **[STATUS.md](./STATUS.md)** — Estado atual do projeto (sempre atualizado)
- **[AUDITORIA-IA.md](./AUDITORIA-IA.md)** — Log honesto do que funciona, o que não funciona e por quê
- **[PLANO-CORRECOES.md](./PLANO-CORRECOES.md)** — Sprint 2026-04-18 (concluído)
- **[PROTOCOLO-IA.md](./PROTOCOLO-IA.md)** — Como outras IAs devem trabalhar aqui
- **[docs-projeto/CREDENCIAIS.md](./docs-projeto/CREDENCIAIS.md)** — Chaves e tokens
- **[docs-projeto/SUPABASE-COMPARTILHADO.md](./docs-projeto/SUPABASE-COMPARTILHADO.md)** — Regras do banco compartilhado
- **[docs-projeto/COMO-EXECUTAR-LOCAL.md](./docs-projeto/COMO-EXECUTAR-LOCAL.md)** — Guia de execução local

## 🏗️ Stack

- **Frontend:** HTML + Tailwind CSS v3 (CDN) + Vanilla JS — GitHub Pages
- **Backend:** Python 3.11+ (rodando no GitHub Actions diariamente às 12:00 UTC)
- **Fonte de realidade:** hierarquia descrita acima
- **Previsões:** Open-Meteo (5 modelos) + OpenWeatherMap
- **Validação Manual:** Supabase (projeto KANBAN emprestado, tabela `topclimabc_validacoes`)
- **CI/CD:** GitHub Actions (`.github/workflows/atualizacao_diaria.yml`)

## 📄 Licença

Projeto pessoal de auditoria climática. Dados meteorológicos: Open-Meteo (CC-BY 4.0), CEMADEN/MCTI (domínio público), OpenWeatherMap (licença gratuita).
