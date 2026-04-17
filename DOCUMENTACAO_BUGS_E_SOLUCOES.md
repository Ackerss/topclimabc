# POST-MORTEM & SOLUÇÃO DE BUGS CRÍTICOS (TOPCLIMABC)

Este arquivo serve como um "registro permanente de voo e alerta" para Desenvolvedores Humanos ou as **Próximas Inteligências Artificiais** que realizarem a manutenção do `TOPCLIMABC`.

---

## 1. O Pior Inimigo das IAs: "Silent Bugs" e Colisões no Escopo Global

### O que Aconteceu (17/04/2026)?
As IAs passadas realizaram atualizações belíssimas na interface visual (adição de novos Cards, Botões de Manuais interativos, e vinculação com Supabase). Foi validado tudo como "Sintaxe OK", feito o Push e o Commit. Porém: **Todo o Sistema Frontend Paralisou.** Os dados pararam de carregar nos cards, as abas ficaram vazias e os botões não abriam.

### A Investigação (Como achamos)
Quando uma IA tentou avaliar o erro lendo a sintaxe Javascript usando analisadores isolados (Ex: `node -e`), os motores responderam "Sem Erros de Sintaxe" porque avaliavam a string sozinha. O "assassino silencioso" se escondia na montagem global de variáveis do Chrome.

Para acharmos a verdade empírica, injetamos scripts do tipo `window.onerror` e rodamos um servidor local espião Python onde "laçamos" o verdadeiro log do Chrome que dizia:
`Uncaught SyntaxError: Identifier 'supabase' has already been declared`

### A Causa Raiz
Quando usamos CDNs externos de bibliotecas injetando na `<head>`, como:
`<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>`
Esse CDN imediatamente cria uma variável no **Objeto Global** (Window) do navegador que compartilha ou tenta ocupar o nome `supabase`.

Logo nas linhas baixas, dentro do nosso próprio JS (`<script>`), nós tentamos fazer a importação ingênua:
`const supabase = window.supabase.createClient(...)`

Como a tag HTML não possuía formato Modular (`type="module"`), as consts ou lets globais atritaram imediatamente num conflito com a CDN. Esse singelo erro paralisou toda a interpretação do JS seguinte no browser antes de se quer uma função da página rodar.

### Lições Aprendidas para Novas IAs 
1. **NUNCA use identificadores brutos globais que dão Match com suas CDNs (`const supabase`, `const firebase`, `const moment`).** 
2. **Ao invés disso, USE nomes customizados!** Passamos a usar permanentemente `const supabaseClient = window.supabase.createClient(...)` para blindar nossa interface de conflitos globais de namespace. Mantenha essa cultura.
3. Se o site aparenta ter estragado "do nada" sem nenhuma edição falha, **VERIFIQUE as colisões de variáveis.**

---

## 2. A Ilusão das Testes de "Múltipla Falsa Positividade": Cache de GH e CDN

Em segundo plano, logo após o Fix da IA, o projeto continuou a refletir a "Tela Branca" no computador, levando à desconfiança que o Github Actions ou que os arquivos haviam sido corrompidos e gerado o bug novamente.

### Por que isso ocorre e Lição Aprendida
O Github Pages possui uma latência inerente (`CDN TTL` e tempo de re-deploying do Branch). 
- Assim que se faz o `git push` no Main, existe uma diferença de ca. **5 a 10 Minutos** onde a nuvem continua vomitando o `index.html` anterior. 
- Semelhantemente, o Chrome possui níveis pesados de cache para JSON e HTML via Pages.

**Táticas Operacionais:**
- Para que IAs futuras não fiquem rodando em círculos ou destruindo a arquitetura em busca de um erro local que nem existe, usem o comando curl ou `read_url_content` em combinação para checar O QUE o CDN do Github ESTÁ realmente enviando naquele segundo, validando se o deploy final já virou a chave térmica online.
- Instruam o Humano sempre a testar num container de Navegador Isolado (Guias Anônimas) ou ativando a Flag "Ignorar Cache de Rede (CTRL + F5)".

---

> **Status:** Estes bugs foram erradicados. Estruturas `try/catch` protegem agora o app e as variáveis ganharam nomes descolados. As implementações de score do Open-Meteo do TOPCLIMABC não travam o JS central.
