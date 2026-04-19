# 🤖 PROTOCOLO OBRIGATÓRIO PARA TODA IA QUE ABRIR ESTE PROJETO

> ⚠️ **LEIA ISTO ANTES DE QUALQUER COISA.** Se você é uma IA (Gemini, Claude, GPT, etc.)
> e está prestes a trabalhar no TOPCLIMABC, siga este protocolo EXATAMENTE.
> O dono do projeto **não é programador**. Ele não vai repetir contexto — tudo que você precisa saber está neste e nos outros arquivos de documentação.
>
> **Última revisão:** 2026-04-19 (sincronizado com o código real após auditoria profunda).

---

## PASSO 1 — LEIA ESTES ARQUIVOS NA ORDEM

```
1. PROTOCOLO-IA.md          ← Você está lendo agora
2. AUDITORIA-IA.md          ← O QUE FUNCIONA e O QUE NÃO FUNCIONA hoje (LEIA ANTES DE "CONSERTAR" QUALQUER COISA)
3. STATUS.md                ← Estado atual do projeto
4. PLANO-CORRECOES.md       ← Sprint 2026-04-18 (concluído) — lista de bugs já corrigidos
5. ARCHITECTURE.md          ← Plano completo de arquitetura
6. docs-projeto/CREDENCIAIS.md           ← Chaves de API reais
7. docs-projeto/SUPABASE-COMPARTILHADO.md ← REGRAS DO BANCO (IMPORTANTE)
```

Só depois de ler tudo acima, olhe para os arquivos de código.

---

## PASSO 2 — REGRAS QUE NUNCA PODEM SER QUEBRADAS

### 🔴 REGRAS ABSOLUTAS (violação invalida o projeto)

1. **SNAPSHOT é sagrado.** A previsão coletada em um dia NUNCA pode ser alterada retroativamente. Se o modelo previu 5mm para amanhã e guardamos isso, esse valor fica congelado para sempre — mesmo que o site/modelo depois "corrija" a previsão.

2. **Hierarquia de realidade.** Dados de realidade seguem esta ordem (ver `scripts/coletar_realidade.py`):
   - **1º — Validação manual do usuário** (Supabase com `override=true`) — prioridade absoluta, sempre vence
   - **2º — CEMADEN PED** (pluviômetro físico) — atualmente **fora do ar** (retorna "Forbidden")
   - **3º — Open-Meteo Archive best_match** (reanálise ERA5-Land) — fonte automática efetiva hoje
   - **4º — Open-Meteo Historical Forecast** — último recurso
   - **NUNCA inventar 0mm se não há dado** — a ausência é explícita

3. **Supabase compartilhado.** O banco é o projeto "KANBAN" (Project ID `jfjrzkjzfxnyhexwhoby`), emprestado. Toda tabela DEVE ter prefixo `topclimabc_`. NUNCA altere tabelas sem esse prefixo.

4. **Não commit de dados sem fonte.** Os arquivos `.json` em `data/` e `docs/` são gerados por scripts Python automaticamente via GitHub Actions. Se você for mexer em algum, rode a pipeline depois (`TOPCLIMABC.bat`) para regenerar corretamente.

### 🟡 REGRAS IMPORTANTES

5. **Frontend usa Tailwind CSS v3** via CDN. Não instale npm/node. Não use Tailwind v4.

6. **Sem frameworks JS.** Vanilla JavaScript apenas. Sem React, Vue, Angular.

7. **GitHub Pages serve a pasta `/docs`**. O frontend vive em `docs/`. Não mova para `public/` ou raiz.

8. **Nomes de arquivos em snake_case** para scripts Python. kebab-case para arquivos HTML/CSS/JS.

9. **Classes de chuva unificadas:** `seco`, `garoa`, `moderada`, `forte`, `intensa`. Nunca use `fraca`, `muito_forte`, `sem_chuva`, etc (vocabulário antigo, já removido).

10. **Dono não é programador.** Ao responder a ele, evite jargão. Explique em termos de "funciona / não funciona / por quê". Ao *agir*, seja autônomo — ele confia que você resolve.

---

## PASSO 3 — ANTES DE CODAR, ATUALIZE STATUS.md

Quando for iniciar qualquer tarefa:

```markdown
# No STATUS.md, mude a seção "ONDE A IA PAROU" para refletir o que você
# vai fazer agora. Se a tarefa for grande, crie ou atualize PLANO-XXX.md.
```

---

## PASSO 4 — QUANDO TERMINAR UMA TAREFA

1. Atualize o `STATUS.md` com o que foi feito
2. Se descobriu algo importante (ex: uma API mudou), atualize `AUDITORIA-IA.md`
3. Commit com mensagem clara
4. Se tiver `gh` disponível, push para `origin main`

---

## PASSO 5 — QUANDO SEUS TOKENS ACABAREM (ou sessão encerrar)

**ANTES de terminar** (ao perceber que está perto do fim da sessão):

1. Atualize `STATUS.md` com o estado exato de onde parou
2. Se parou no meio de algo, deixe um `# TODO-PROX-IA:` no código
3. Commit tudo que estiver pronto

---

## PERGUNTAS FREQUENTES

**P: O CEMADEN não responde. O que eu faço?**
R: **Nada.** O sistema já tem fallback automático (Open-Meteo Archive). Ver `AUDITORIA-IA.md` seção "CEMADEN" para contexto completo. Não tente "consertar" o CEMADEN — o problema é do servidor deles.

**P: Uma IA antes de mim falou de um endpoint alternativo pra CEMADEN (ex: SGB ArcGIS). Posso usar?**
R: **Tome MUITO cuidado.** Já testamos o endpoint SGB — é específico de Alagoas com dados de 2019. IAs alucinam APIs. **Sempre teste o endpoint com `curl` antes de integrar** e confirme: (a) cobre BC/Itajaí (SC), (b) tem dados recentes (≤ 7 dias). Ver `AUDITORIA-IA.md` seção "APIs testadas e rejeitadas".

**P: Posso usar uma biblioteca Python não listada em `scripts/requirements.txt`?**
R: Adicione ao `scripts/requirements.txt` e documente no `STATUS.md` por quê foi necessário.

**P: Posso criar arquivos fora da estrutura definida em ARCHITECTURE.md?**
R: Apenas arquivos temporários de debug. Limpe antes de commitar.

**P: O usuário pediu algo diferente do plano. O que faço?**
R: Implemente o pedido, atualize `ARCHITECTURE.md` e `STATUS.md` para refletir a mudança, e documente o motivo.

**P: Como rodo o projeto localmente?**
R: `TOPCLIMABC.bat` na raiz (duplo clique no Windows) OU os 4 comandos documentados em `docs-projeto/COMO-EXECUTAR-LOCAL.md`.

**P: Como sei se uma informação neste repositório é confiável?**
R: Sempre confie nos arquivos de **código** primeiro (`.py`, `.html`, `.yml`). A documentação pode estar desatualizada. Se achar uma divergência entre doc e código, **corrija a doc**, nunca o código silenciosamente.
