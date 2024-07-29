@echo off
setlocal enabledelayedexpansion

:menu
cls
echo Executando main.py...
cd %~dp0
python main.py
echo Pressione 1 para executar novamente, qualquer outra tecla para sair.
set /p choice=""

if !choice! equ 1 (
    goto menu
)
endlocal
