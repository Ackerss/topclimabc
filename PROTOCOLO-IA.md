# 🤖 PROTOCOLO OBRIGATÓRIO PARA TODA IA QUE ABRIR ESTE PROJETO

> ⚠️ **LEIA ISTO ANTES DE QUALQUER COISA.** Se você é uma IA (Gemini, Claude, GPT, etc.) 
> e está prestes a trabalhar no TOPCLIMABC, siga este protocolo EXATAMENTE.
> O dono do projeto não vai ficar repetindo contexto. Tudo que você precisa saber está aqui.

---

## PASSO 1 — LEIA ESTES ARQUIVOS NA ORDEM

```
1. PROTOCOLO-IA.md          ← Você está lendo agora
2. STATUS.md                ← O que já foi feito e o que falta fazer (SEMPRE ATUALIZADO)
3. ARCHITECTURE.md          ← Plano completo de arquitetura (40KB de detalhes)
4. docs-projeto/CREDENCIAIS.md           ← Chaves de API
5. docs-projeto/SUPABASE-COMPARTILHADO.md ← REGRAS DO BANCO (IMPORTANTE)
```

Só depois de ler tudo acima, olhe para os arquivos de código.

---

## PASSO 2 — ENTENDA O STATUS ATUAL

Abra `STATUS.md` e veja:
- O que **já foi implementado** (marque como ✅)
- O que está **em progresso** (⏳)
- O que **falta fazer** (⬜)
- Se há **bloqueios** ativos

---

## PASSO 3 — REGRAS QUE NUNCA PODEM SER QUEBRADAS

### 🔴 REGRAS ABSOLUTAS (violação invalida o projeto)

1. **SNAPSHOT é sagrado.** A previsão coletada em um dia NUNCA pode ser alterada retroativamente. Se o modelo previu 5mm para amanhã e guardamos isso, esse valor fica congelado para sempre — mesmo que o site/modelo depois "corrija" a previsão.

2. **CEMADEN é o juiz.** Dados reais de chuva vêm do CEMADEN (pluviômetros físicos), não de modelos ou reanálise. Open-Meteo Historical é APENAS fallback de emergência.

3. **Supabase compartilhado.** O banco é o projeto "craquepedia" de outro projeto. Toda tabela DEVE ter prefixo `topclimabc_`. NUNCA altere tabelas sem esse prefixo.

4. **Sem Supabase nos JSONs do repo.** Os arquivos `.json` em `data/` e `docs/` são gerados por scripts Python e commitats via GitHub Actions. O Supabase é APENAS para validação manual do usuário.

### 🟡 REGRAS IMPORTANTES

5. **Frontend usa Tailwind CSS v3** via CDN. Não instale npm/node. Não use Tailwind v4.

6. **Sem frameworks JS.** Vanilla JavaScript apenas. Sem React, Vue, Angular.

7. **GitHub Pages serve a pasta `/docs`**. O frontend vive em `docs/`. Não mova para `public/` ou raiz.

8. **Nomes de arquivos em snake_case** para scripts Python. kebab-case para arquivos HTML/CSS/JS.

---

## PASSO 4 — ANTES DE CODAR, ATUALIZE STATUS.md

Quando for iniciar qualquer tarefa:

```markdown
# No STATUS.md, mude:
⬜ Task X.Y: [descrição]
# Para:
⏳ Task X.Y: [descrição] — Em progresso por [Nome-da-IA] em [data]
```

---

## PASSO 5 — QUANDO TERMINAR UMA TAREFA

1. Marque no `STATUS.md` como ✅ com data e descrição do que foi feito
2. Documente qualquer descoberta importante (ex: o endpoint CEMADEN retorna X ao invés de Y)
3. Se encontrou um problema que afeta o plano, documente em `STATUS.md` na seção BLOQUEIOS

---

## PASSO 6 — QUANDO SEUS TOKENS ACABAREM (ou sessão encerrar)

**ANTES de terminares** (ao perceber que está perto do fim da sessão):

1. Salve qualquer arquivo aberto
2. Atualize `STATUS.md` com o estado exato de onde parou
3. Deixe um comentário `# TODO-PROX-IA:` no código onde parou
4. Atualize `STATUS.md` seção "ONDE A IA PAROU"

---

## PERGUNTAS FREQUENTES

**P: Posso usar uma biblioteca Python não listada em requirements.txt?**
R: Adicione ao requirements.txt e documente no STATUS.md por quê foi necessário.

**P: O endpoint CEMADEN não está respondendo. O que faço?**
R: Use Open-Meteo Historical como fallback TEMPORÁRIO, registre no log, e documente no STATUS.md como bloqueio.

**P: Não sei qual estação CEMADEN usar para BC.**
R: Consulte `data/cemaden-estacoes-bc.json` se existir, ou execute `scripts/utils/cemaden.py` diretamente para listar estações.

**P: Posso criar arquivos fora da estrutura definida em ARCHITECTURE.md?**
R: Apenas arquivos temporários de debug. Limpe antes de commitar.

**P: O usuário pediu algo diferente do plano. O que faço?**
R: Implemente o pedido, atualize ARCHITECTURE.md e STATUS.md para refletir a mudança, e documente o motivo.
