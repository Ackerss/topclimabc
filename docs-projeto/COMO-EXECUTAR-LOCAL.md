# 🛠️ Como Executar o TOPCLIMABC Localmente

Este guia explica como rodar o sistema completo na sua máquina.

## 📋 Pré-requisitos
1. **Python 3.9+** instalado.
2. Bibliotecas necessárias (instale via terminal):
   ```bash
   pip install requests python-dotenv beautifulsoup4
   ```

---

## 🚀 Executando o Backend (Auditoria)
Para atualizar o site com as previsões de hoje e checar quem acertou ontem, você tem duas opções:

### Opção 1: Atalho de 1-Clique (Recomendado)
Basta dar um duplo-clique no arquivo **`TOPCLIMABC.bat`** na raiz do projeto. 
Ele vai abrir uma janela e rodar toda a sequência sozinho:
1. Coleta previsões.
2. Coleta a realidade de ontem.
3. Faz a auditoria.
4. Atualiza o site local.

### Opção 2: Via Terminal
Se preferir rodar manualmente:
```bash
python -m scripts.coletar_previsoes
python -m scripts.coletar_realidade
python -m scripts.auditar
python -m scripts.gerar_frontend
```

---

## 🌐 Visualizando o Site (Frontend)
O site fica na pasta `/docs`.

### Abrindo o arquivo diretamente
Você pode simplesmente abrir o arquivo `docs/index.html` no seu navegador (Chrome/Edge). Como ele salva os dados no `localStorage`, as validações manuais vão funcionar normalmente.

### Rodando um servidor local (Opcional)
Se quiser testar como um site real:
```bash
cd docs
python -m http.server 8000
```
Depois acesse: `http://localhost:8000`

---

## 📂 Onde ficam os dados?
- **Previsões brutas:** `data/previsoes/`
- **Chuva medida (Realidade):** `data/realidade/`
- **Resultados da Auditoria:** `data/auditoria/historico.json`
- **Dados para o site:** `docs/dados.json` e `docs/ranking.json`

---

## ⚡ Solução de Problemas
- **Erro "ModuleNotFound":** Rode o comando `pip install` listado nos Pré-requisitos.
- **Site não atualiza:** Certifique-se de que rodou o `TOPCLIMABC.bat` ou os scripts Python recentemente.
- **Gráficos Vazios:** Na primeira vez, é normal. Rode o script de auditoria para começar a gerar história. (Dica: Rode `python -m scripts.bootstrap_realidade` para carregar história agora).
