@echo off
TITLE TOPCLIMABC - Motor de Auditoria
cls
echo ======================================================
echo           TOPCLIMABC - Auditoria Automatica
echo ======================================================
echo.
echo [1/4] Coletando Previsoes de Hoje...
python -m scripts.coletar_previsoes
echo.
echo [2/4] Coletando Realidade de Ontem...
python -m scripts.coletar_realidade
echo.
echo [3/4] Auditando Acertos...
python -m scripts.auditar
echo.
echo [4/4] Sincronizando Frontend...
python -m scripts.gerar_frontend
echo.
echo ======================================================
echo   PROCESSO CONCLUIDO COM SUCESSO!
echo   Os dados no site (pasta docs) foram atualizados.
echo ======================================================
pause
