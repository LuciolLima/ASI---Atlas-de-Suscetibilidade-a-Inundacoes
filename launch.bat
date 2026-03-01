@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

:: ══════════════════════════════════════════════════════════════
::  ASI | Atlas de Suscetibilidade a Inundações
::  Launcher Unificado — Windows
:: ══════════════════════════════════════════════════════════════

set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
set "STATE_FILE=%BASE_DIR%\.asi_launcher_state"
set "PYTHON_BIN="

cls
goto :TELA_INICIAL


:: ══════════════════════════════════════════════════════════════
::  HELPERS DE COR (via PowerShell — sem vazamento ANSI)
:: ══════════════════════════════════════════════════════════════

:OK
powershell -Command "Write-Host '  v  ' -ForegroundColor Green -NoNewline; Write-Host '%~1'"
goto :EOF

:ERRO
powershell -Command "Write-Host '  X  ' -ForegroundColor Red -NoNewline; Write-Host '%~1' -ForegroundColor Red"
goto :EOF

:AVISO
powershell -Command "Write-Host '  !  ' -ForegroundColor Yellow -NoNewline; Write-Host '%~1' -ForegroundColor Yellow"
goto :EOF

:INFO
powershell -Command "Write-Host '  .  ' -ForegroundColor Cyan -NoNewline; Write-Host '%~1' -ForegroundColor DarkGray"
goto :EOF

:LINHA
powershell -Command "Write-Host ('=' * 62) -ForegroundColor DarkGray"
goto :EOF

:LINHA_FINA
powershell -Command "Write-Host ('-' * 62) -ForegroundColor DarkGray"
goto :EOF

:PAUSA_SEG
timeout /t %~1 /nobreak >nul
goto :EOF

:CABECALHO_PASSO
echo.
call :LINHA
powershell -Command "Write-Host '  PASSO %~1/8  ' -ForegroundColor Cyan -NoNewline; Write-Host '|  ' -ForegroundColor DarkGray -NoNewline; Write-Host '%~2' -ForegroundColor Magenta"
call :LINHA
echo.
goto :EOF

:AGUARDANDO
powershell -Command "Write-Host '  ...  ' -ForegroundColor Blue -NoNewline; Write-Host '%~1' -ForegroundColor DarkGray"
goto :EOF


:: ══════════════════════════════════════════════════════════════
::  TELA INICIAL
:: ══════════════════════════════════════════════════════════════

:TELA_INICIAL
cls
echo.
powershell -Command "Write-Host '  +========================================================+' -ForegroundColor Cyan"
powershell -Command "Write-Host '  |  ' -ForegroundColor Cyan -NoNewline; Write-Host 'ASI ^| Atlas de Suscetibilidade a Inundacoes    ' -ForegroundColor White -NoNewline; Write-Host '  |' -ForegroundColor Cyan"
powershell -Command "Write-Host '  |  ' -ForegroundColor Cyan -NoNewline; Write-Host 'Launcher Unificado v2.0  --  Windows           ' -ForegroundColor DarkGray -NoNewline; Write-Host '  |' -ForegroundColor Cyan"
powershell -Command "Write-Host '  +========================================================+' -ForegroundColor Cyan"
echo.
powershell -Command "Write-Host '  Raiz do projeto: ' -NoNewline -ForegroundColor DarkGray; Write-Host '%BASE_DIR%' -ForegroundColor Cyan"
echo.

if exist "%STATE_FILE%" (
    powershell -Command "Write-Host '  Execucao anterior detectada! Passos concluidos serao acelerados.' -ForegroundColor Green"
    echo.
)

call :PAUSA_SEG 2
goto :PASSO1


:: ══════════════════════════════════════════════════════════════
::  PASSO 1 — VERSÃO DO PYTHON
:: ══════════════════════════════════════════════════════════════

:PASSO1
call :CABECALHO_PASSO 1 "Verificando versao do Python"
call :AGUARDANDO "Detectando interpretador Python..."
call :PAUSA_SEG 1
echo.

for %%P in (python3.14 python3.13 python3.12 python3 python) do (
    if "!PYTHON_BIN!"=="" (
        where %%P >nul 2>&1
        if !errorlevel! == 0 (
            for /f "tokens=*" %%V in ('%%P -c "import sys; print(sys.version_info.major * 100 + sys.version_info.minor)" 2^>nul') do (
                if %%V GEQ 312 (
                    set "PYTHON_BIN=%%P"
                )
            )
        )
    )
)

if "!PYTHON_BIN!"=="" (
    call :ERRO "Nenhum Python 3.12+ encontrado no sistema!"
    echo.
    call :AVISO "Instale Python 3.12 ou superior:"
    call :INFO  "https://www.python.org/downloads/"
    echo.
    call :LINHA
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%V in ('!PYTHON_BIN! -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\")" 2^>nul') do set "PYTHON_VER=%%V"

call :INFO "Executavel : !PYTHON_BIN!"
call :INFO "Detectado  : Python !PYTHON_VER!"
call :INFO "Minimo     : Python 3.12"
echo.
call :OK "Python !PYTHON_VER! compativel!"
call :PAUSA_SEG 1
goto :PASSO2


:: ══════════════════════════════════════════════════════════════
::  PASSO 2 — DETECTA data_V2.8
:: ══════════════════════════════════════════════════════════════

:PASSO2
call :CABECALHO_PASSO 2 "Detectando pasta data_V2.8"
call :AGUARDANDO "Procurando pasta data_V2.8..."
call :PAUSA_SEG 1
echo.

if exist "%BASE_DIR%\data\" (
    call :OK "Pasta data\ ja existe — rename anterior detectado."
    call :INFO "Pulando passos 3 e 4."
    call :PAUSA_SEG 1
    goto :PASSO5
)

if not exist "%BASE_DIR%\data_V2.8\" (
    call :ERRO "Pasta data_V2.8 NAO encontrada!"
    echo.
    call :AVISO "Esta pasta e ESSENCIAL para o sistema."
    call :AVISO "Coloque-a na raiz do projeto e tente novamente."
    echo.
    call :LINHA
    echo.
    pause
    exit /b 1
)

call :OK "Pasta data_V2.8\ localizada."
call :INFO "%BASE_DIR%\data_V2.8"
call :PAUSA_SEG 1
goto :PASSO3


:: ══════════════════════════════════════════════════════════════
::  PASSO 3 — VERIFICA ESTRUTURA INTERNA DO data_V2.8
:: ══════════════════════════════════════════════════════════════

:PASSO3
call :CABECALHO_PASSO 3 "Verificando integridade de data_V2.8"

set "ERROS_V2=0"
set "ROOT_V2=%BASE_DIR%\data_V2.8"

call :CHK_PASTA_V2 "%ROOT_V2%\curated\attribute_tables"
call :CHK_ARQ_V2   "%ROOT_V2%\curated\attribute_tables\data_table.txt"
call :CHK_ARQ_V2   "%ROOT_V2%\curated\attribute_tables\data_table.txt.xml"
call :CHK_ARQ_V2   "%ROOT_V2%\curated\attribute_tables\Data_Table.xls"
call :CHK_ARQ_V2   "%ROOT_V2%\curated\attribute_tables\schema.ini"
call :CHK_PASTA_V2 "%ROOT_V2%\curated\attribute_tables\info"
call :CHK_ARQ_V2   "%ROOT_V2%\curated\attribute_tables\info\arc.dir"
call :CHK_PASTA_V2 "%ROOT_V2%\raw\arcmap_exports"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\arcmap_exports\bairros_cabo_oficial.json"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\arcmap_exports\br_uf_2024.json"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\arcmap_exports\Data_Table.xls"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\arcmap_exports\mdt_points_tables.txt"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\arcmap_exports\pe_municipios_2024.json"
call :CHK_PASTA_V2 "%ROOT_V2%\raw\apac_exports"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\apac_exports\precipitacao_pernambuco.csv"
call :CHK_PASTA_V2 "%ROOT_V2%\raw\events"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\events\defesacivil_pe_consolidado.csv"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\events\historico_inundacoes.csv"
call :CHK_PASTA_V2 "%ROOT_V2%\raw\qgis_exports"
call :CHK_ARQ_V2   "%ROOT_V2%\raw\qgis_exports\Hidrografia_Pernambuco.geojson"

echo.
if !ERROS_V2! GTR 0 (
    call :ERRO "!ERROS_V2! item(s) ausente(s) — pasta incompleta!"
    echo.
    call :AVISO "Corrija a estrutura de data_V2.8 e execute novamente."
    echo.
    pause
    exit /b 1
)
call :OK "Integridade de data_V2.8\ confirmada!"
call :PAUSA_SEG 1
goto :PASSO4

:CHK_PASTA_V2
if not exist "%~1\" (
    powershell -Command "Write-Host '  X  Pasta ausente: %~nx1\' -ForegroundColor Red"
    set /a ERROS_V2+=1
) else (
    powershell -Command "Write-Host '  v  ' -ForegroundColor Green -NoNewline; Write-Host '%~nx1\' -ForegroundColor Cyan"
)
goto :EOF

:CHK_ARQ_V2
if not exist "%~1" (
    powershell -Command "Write-Host '       X  %~nx1  <- ausente' -ForegroundColor Red"
    set /a ERROS_V2+=1
) else (
    powershell -Command "Write-Host '       v  ' -ForegroundColor Green -NoNewline; Write-Host '%~nx1' -ForegroundColor DarkGray"
)
goto :EOF


:: ══════════════════════════════════════════════════════════════
::  PASSO 4 — RENOMEIA data_V2.8 → data
:: ══════════════════════════════════════════════════════════════

:PASSO4
call :CABECALHO_PASSO 4 "Renomeando data_V2.8 para data"

if exist "%BASE_DIR%\data\" (
    call :AVISO "Pasta data\ ja existe — rename ignorado."
    call :PAUSA_SEG 1
    goto :PASSO5
)

call :AGUARDANDO "Aplicando rename..."
call :PAUSA_SEG 1

rename "%BASE_DIR%\data_V2.8" "data" >nul 2>&1

if !errorlevel! NEQ 0 (
    call :ERRO "Falha ao renomear a pasta!"
    call :AVISO "Verifique se a pasta nao esta aberta em outro programa."
    echo.
    pause
    exit /b 1
)

echo.
powershell -Command "Write-Host '  v  ' -ForegroundColor Green -NoNewline; Write-Host 'data_V2.8\  ->  ' -ForegroundColor Yellow -NoNewline; Write-Host 'data\' -ForegroundColor Green -NoNewline; Write-Host '  renomeada com sucesso!' -ForegroundColor DarkGray"
call :PAUSA_SEG 1
goto :PASSO5


:: ══════════════════════════════════════════════════════════════
::  PASSO 5 — ESTRUTURA COMPLETA DO PROJETO
:: ══════════════════════════════════════════════════════════════

:PASSO5
call :CABECALHO_PASSO 5 "Verificando estrutura completa do projeto"

if exist "%STATE_FILE%" (
    findstr /c:"estrutura_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Estrutura ja validada anteriormente."
        call :INFO "Delete .asi_launcher_state para revalidar."
        call :PAUSA_SEG 1
        goto :PASSO6
    )
)

set "ERROS_ESTR=0"

call :CHK_ARQ_E   "%BASE_DIR%\app.py"
call :CHK_PASTA_E "%BASE_DIR%\data\curated\attribute_tables"
call :CHK_ARQ_E   "%BASE_DIR%\data\curated\attribute_tables\data_table.txt"
call :CHK_ARQ_E   "%BASE_DIR%\data\curated\attribute_tables\data_table.txt.xml"
call :CHK_ARQ_E   "%BASE_DIR%\data\curated\attribute_tables\Data_Table.xls"
call :CHK_ARQ_E   "%BASE_DIR%\data\curated\attribute_tables\schema.ini"
call :CHK_PASTA_E "%BASE_DIR%\data\curated\attribute_tables\info"
call :CHK_ARQ_E   "%BASE_DIR%\data\curated\attribute_tables\info\arc.dir"
call :CHK_PASTA_E "%BASE_DIR%\data\raw\arcmap_exports"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\arcmap_exports\bairros_cabo_oficial.json"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\arcmap_exports\br_uf_2024.json"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\arcmap_exports\Data_Table.xls"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\arcmap_exports\mdt_points_tables.txt"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\arcmap_exports\pe_municipios_2024.json"
call :CHK_PASTA_E "%BASE_DIR%\data\raw\apac_exports"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\apac_exports\precipitacao_pernambuco.csv"
call :CHK_PASTA_E "%BASE_DIR%\data\raw\events"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\events\defesacivil_pe_consolidado.csv"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\events\historico_inundacoes.csv"
call :CHK_PASTA_E "%BASE_DIR%\data\raw\qgis_exports"
call :CHK_ARQ_E   "%BASE_DIR%\data\raw\qgis_exports\Hidrografia_Pernambuco.geojson"
call :CHK_PASTA_E "%BASE_DIR%\docs\academic_context"
call :CHK_ARQ_E   "%BASE_DIR%\docs\academic_context\credits.md"
call :CHK_ARQ_E   "%BASE_DIR%\docs\academic_context\DTM_doc.md"
call :CHK_ARQ_E   "%BASE_DIR%\docs\academic_context\institutions.md"
call :CHK_ARQ_E   "%BASE_DIR%\docs\academic_context\project_origin.md"
call :CHK_ARQ_E   "%BASE_DIR%\docs\academic_context\timeline.md"
call :CHK_PASTA_E "%BASE_DIR%\docs\ethics_and_use"
call :CHK_PASTA_E "%BASE_DIR%\docs\methodology"
call :CHK_PASTA_E "%BASE_DIR%\docs\project_overview"
call :CHK_ARQ_E   "%BASE_DIR%\docs\project_overview\estructure.txt.txt"
call :CHK_PASTA_E "%BASE_DIR%\docs\roadmap"
call :CHK_PASTA_E "%BASE_DIR%\outputs\charts"
call :CHK_PASTA_E "%BASE_DIR%\outputs\dashboards"
call :CHK_PASTA_E "%BASE_DIR%\outputs\maps"
call :CHK_PASTA_E "%BASE_DIR%\outputs\reports"
call :CHK_ARQ_E   "%BASE_DIR%\references\articles.md"
call :CHK_ARQ_E   "%BASE_DIR%\references\links.md"
call :CHK_ARQ_E   "%BASE_DIR%\references\technical_docs.md"
call :CHK_PASTA_E "%BASE_DIR%\src\analysis"
call :CHK_ARQ_E   "%BASE_DIR%\src\analysis\analytics.py"
call :CHK_PASTA_E "%BASE_DIR%\src\dashboard"
call :CHK_PASTA_E "%BASE_DIR%\src\processing"
call :CHK_ARQ_E   "%BASE_DIR%\src\processing\data_loader.py"
call :CHK_PASTA_E "%BASE_DIR%\src\scripts"
call :CHK_ARQ_E   "%BASE_DIR%\src\scripts\utilits.py"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\components.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\config.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\documentation.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\map_engine.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\report_generator.py"

echo.
if !ERROS_ESTR! GTR 0 (
    call :ERRO "!ERROS_ESTR! erro(s) critico(s) na estrutura!"
    echo.
    call :AVISO "Corrija os itens marcados com X e execute novamente."
    echo.
    pause
    exit /b 1
)

call :OK "Estrutura completa e integra!"
echo estrutura_ok> "%STATE_FILE%"
call :PAUSA_SEG 1
goto :PASSO6

:CHK_PASTA_E
if not exist "%~1\" (
    powershell -Command "Write-Host '  X  Pasta ausente: %~nx1\' -ForegroundColor Red"
    set /a ERROS_ESTR+=1
) else (
    powershell -Command "Write-Host '  v  ' -ForegroundColor Green -NoNewline; Write-Host '%~nx1\' -ForegroundColor Cyan"
)
goto :EOF

:CHK_ARQ_E
if not exist "%~1" (
    powershell -Command "Write-Host '       X  %~nx1  <- ausente' -ForegroundColor Red"
    set /a ERROS_ESTR+=1
) else (
    powershell -Command "Write-Host '       v  ' -ForegroundColor Green -NoNewline; Write-Host '%~nx1' -ForegroundColor DarkGray"
)
goto :EOF


:: ══════════════════════════════════════════════════════════════
::  PASSO 6 — INSTALA BIBLIOTECAS
:: ══════════════════════════════════════════════════════════════

:PASSO6
call :CABECALHO_PASSO 6 "Instalando bibliotecas"

if exist "%STATE_FILE%" (
    findstr /c:"libs_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Bibliotecas ja instaladas anteriormente."
        call :INFO "Delete .asi_launcher_state para reinstalar."
        call :PAUSA_SEG 1
        goto :PASSO7
    )
)

set "REQ_FILE="
if exist "%BASE_DIR%\requirements.txt" set "REQ_FILE=%BASE_DIR%\requirements.txt"
if exist "%BASE_DIR%\requirements.txt"  set "REQ_FILE=%BASE_DIR%\requirements.txt"

call :AGUARDANDO "Atualizando pip..."
!PYTHON_BIN! -m pip install --upgrade pip --quiet
call :OK "pip atualizado."
echo.

if "!REQ_FILE!"=="" (
    call :AVISO "requirements.txt nao encontrado — instalando libs individualmente."
    echo.
    !PYTHON_BIN! -m pip install streamlit streamlit-folium folium pyproj geopy pandas plotly
) else (
    call :INFO "Usando: !REQ_FILE!"
    echo.
    call :LINHA_FINA
    echo.
    !PYTHON_BIN! -m pip install -r "!REQ_FILE!"
    echo.
    call :LINHA_FINA
)

if !errorlevel! NEQ 0 (
    echo.
    call :ERRO "Falha durante a instalacao!"
    call :AVISO "Verifique sua conexao ou o requirements.txt."
    echo.
    pause
    exit /b 1
)

echo.
call :OK "Instalacao concluida com sucesso!"
call :PAUSA_SEG 1
goto :PASSO7


:: ══════════════════════════════════════════════════════════════
::  PASSO 7 — VALIDA BIBLIOTECAS
:: ══════════════════════════════════════════════════════════════

:PASSO7
call :CABECALHO_PASSO 7 "Validando bibliotecas instaladas"

if exist "%STATE_FILE%" (
    findstr /c:"libs_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Validacao ja realizada anteriormente."
        call :PAUSA_SEG 1
        goto :PASSO8
    )
)

set "FALHAS_LIB=0"

call :TST_LIB streamlit        streamlit
call :TST_LIB streamlit_folium streamlit-folium
call :TST_LIB folium           folium
call :TST_LIB pyproj           pyproj
call :TST_LIB geopy            geopy
call :TST_LIB pandas           pandas
call :TST_LIB plotly           plotly

echo.
if !FALHAS_LIB! GTR 0 (
    call :ERRO "!FALHAS_LIB! biblioteca(s) com falha!"
    call :AVISO "Execute: pip install -r requirements.txt"
    echo.
    pause
    exit /b 1
)

call :OK "Todas as bibliotecas funcionando corretamente!"

echo estrutura_ok>  "%STATE_FILE%"
echo libs_ok>>      "%STATE_FILE%"

call :PAUSA_SEG 1
goto :PASSO8

:TST_LIB
powershell -Command "Write-Host '  ...  ' -ForegroundColor Blue -NoNewline; Write-Host 'Testando %~2...' -ForegroundColor DarkGray"
!PYTHON_BIN! -c "import %~1" >nul 2>&1
if !errorlevel! == 0 (
    for /f "tokens=*" %%V in ('!PYTHON_BIN! -c "import %~1; print(getattr(__import__(^'%~1^'),^'__version__^',^'?^'))" 2^>nul') do (
        powershell -Command "Write-Host '  v  ' -ForegroundColor Green -NoNewline; Write-Host '%-22s%~2' -NoNewline; Write-Host '  %%V' -ForegroundColor Green"
    )
) else (
    powershell -Command "Write-Host '  X  %~2  NAO INSTALADA' -ForegroundColor Red"
    set /a FALHAS_LIB+=1
)
goto :EOF


:: ══════════════════════════════════════════════════════════════
::  PASSO 8 — EXECUTAR SIGWEB
:: ══════════════════════════════════════════════════════════════

:PASSO8
call :CABECALHO_PASSO 8 "Iniciar o SIGWeb"

if not exist "%BASE_DIR%\app.py" (
    call :ERRO "app.py nao encontrado na raiz do projeto!"
    echo.
    pause
    exit /b 1
)

powershell -Command "Write-Host '  Todos os passos concluidos com sucesso!' -ForegroundColor Green"
echo.
powershell -Command "Write-Host '  Comando que sera executado:' -ForegroundColor DarkGray"
powershell -Command "Write-Host '    streamlit run app.py' -ForegroundColor Cyan"
echo.
call :LINHA_FINA
echo.

set /p "RESPOSTA=  Deseja iniciar o SIGWeb agora? [S/n]: "
echo.

if /i "!RESPOSTA!"=="n"   goto :NAO_EXEC
if /i "!RESPOSTA!"=="nao" goto :NAO_EXEC
if /i "!RESPOSTA!"=="no"  goto :NAO_EXEC

powershell -Command "Write-Host '  ...  Iniciando servidor Streamlit...' -ForegroundColor Blue"
call :PAUSA_SEG 2
echo.
call :OK "Abrindo o navegador... SIGWeb esta subindo!"
call :INFO "Para encerrar, feche esta janela ou pressione Ctrl+C."
echo.
call :LINHA
echo.

cd /d "%BASE_DIR%"
!PYTHON_BIN! -m streamlit run app.py

echo.
call :LINHA
echo.
powershell -Command "Write-Host '  Aplicacao encerrada.' -ForegroundColor Yellow"
echo.
pause
exit /b 0

:NAO_EXEC
call :INFO "Para iniciar manualmente, execute:"
call :INFO "streamlit run app.py"
echo.
call :LINHA
echo.
pause
exit /b 0