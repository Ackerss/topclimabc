# 🌧️ TOPCLIMABC

**Quem acerta a chuva em Balneário Camboriú e Itajaí?**

App Web que monitora previsões de chuva de múltiplos modelos meteorológicos, compara com dados REAIS medidos por pluviômetros (CEMADEN), e gera um ranking confiável para você saber em qual app de previsão do tempo confiar.

## 🎯 O Que Este Projeto Faz

1. **Coleta diária** de previsões de 6+ modelos meteorológicos (GFS, ECMWF, ICON...)
2. **Congela snapshots** — a previsão de hoje para daqui 7 dias fica salva e imutável
3. **Coleta dados reais** dos pluviômetros do CEMADEN nos bairros de BC e Itajaí
4. **Audita automaticamente** — compara previsão vs. realidade com score gradual (0-100)
5. **Gera ranking** — qual modelo/app acerta mais para 1 dia, 3 dias, 7 dias, 15 dias

## 🔗 Acesso

🌐 **[topclimabc.github.io](https://ackerss.github.io/topclimabc/)** *(em construção)*

## 🧭 Qual App Usar?

| Modelo Auditado | Apps que Usam |
|-----------------|---------------|
| ECMWF IFS | Windy, Apple Weather, Climatempo (base) |
| GFS | Weather.com, The Weather Channel |
| ICON | Windy (opção), Bright Sky |
| OWM | OpenWeatherMap app |

Veja o ranking completo no app!

## 📖 Documentação

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — Plano completo de arquitetura
- **[docs-projeto/CREDENCIAIS.md](./docs-projeto/CREDENCIAIS.md)** — Chaves de API
- **[docs-projeto/SUPABASE-COMPARTILHADO.md](./docs-projeto/SUPABASE-COMPARTILHADO.md)** — Aviso sobre banco compartilhado
- **[docs-projeto/COMO-EXECUTAR-LOCAL.md](./docs-projeto/COMO-EXECUTAR-LOCAL.md)** — Guia de execução local

## 🏗️ Stack

- **Frontend:** HTML + Tailwind CSS v3 + Vanilla JS (GitHub Pages)
- **Backend:** Python (GitHub Actions)
- **Dados Reais:** CEMADEN PED API (pluviômetros)
- **Previsões:** Open-Meteo + OpenWeatherMap
- **Validação Manual:** Supabase
- **CI/CD:** GitHub Actions (cron diário)

## 📄 Licença

Projeto pessoal. Dados meteorológicos: CEMADEN/MCTI.
