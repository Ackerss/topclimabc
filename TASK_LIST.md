# ✅ LISTA DE TAREFAS — TOPCLIMABC

Este arquivo resume o que já foi construído e o que ainda falta para o deploy final.

---

## 🟢 CONCLUÍDO (FASE 1 & 2)

### 🎨 Frontend (SPA Moderna)
- [x] Interface em Cards (Dark Mode por padrão)
- [x] Sistema de 4 Abas (Auditoria, Ranking, Histórico, Estações)
- [x] Seleção dinâmica Balneário Camboriú / Itajaí
- [x] PWA Ready (instalável no Android/iPhone)
- [x] Mock de dados iniciais substituído por dados reais do backend

### 🐍 Backend Python (Motor de Auditoria)
- [x] **Coleta Diária:** Busca previsões do Open-Meteo (4 modelos) e OpenWeatherMap.
- [x] **Juiz da Realidade:** Coleta chuva real medida via Open-Meteo Historical (Reanálise ERA5).
- [x] **Motor de Pontuação:** Algoritmo que dá notas de 0 a 100% com base no erro de mm e na classe de chuva.
- [x] **Sincronização:** Atualiza automaticamente os arquivos JSON consumidos pelo site.
- [x] **Bootstrap:** Carga inicial de 15 dias de dados históricos para o app não começar vazio.
- [x] **Atalho de Uso:** Arquivo `TOPCLIMABC.bat` para execução local simplificada.

---

## 🟡 EM ANDAMENTO / PRÓXIMO (FASE 3)

### ☁️ Nuvem e Banco de Dados (Supabase)
- [ ] **Restauração do Supabase:** Reativar o projeto "Craquepedia" no painel do Supabase.
- [ ] **Persistência de Validação:** Trocar o `localStorage` (salvamento no navegador) pelo Supabase para compartilhar registros entre usuários.

### 🤖 Automação (GitHub Actions)
- [ ] Criar o workflow para rodar os scripts Python na nuvem todo dia às 03:00 AM.
- [ ] Publicar no GitHub Pages automaticamente.

---

## 📂 ESTRUTURA ATUAL
- `docs/`: O site (HTML, JS, Dados).
- `scripts/`: O motor Python.
- `data/`: O histórico de previsões e chuva real coletado.
- `docs-projeto/`: Manuais e guias técnicos.

---

## 🚨 BLOQUEIOS
- [ ] **Supabase Inativo:** Precisamos que o usuário restaure o projeto no dashboard para as validações manuais serem salvas na nuvem.
