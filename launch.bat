@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

:: ══════════════════════════════════════════════════════════════════════════════
::  ASI | Atlas de Suscetibilidade a Inundacoes
::  Launcher Unificado v3.2 — Windows
::  Enterprise-Grade SIGWeb with Full Observability Stack
:: ══════════════════════════════════════════════════════════════════════════════

set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"
set "STATE_FILE=%BASE_DIR%\.asi_launcher_state"
set "PYTHON_BIN="

cls
goto :TELA_INICIAL

:: ══════════════════════════════════════════════════════════════════════════════
::  HELPERS DE COR (via PowerShell)
:: ══════════════════════════════════════════════════════════════════════════════

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
powershell -Command "Write-Host ('=' * 70) -ForegroundColor DarkGray"
goto :EOF

:LINHA_FINA
powershell -Command "Write-Host ('-' * 70) -ForegroundColor DarkGray"
goto :EOF

:PAUSA_SEG
if "%~1"=="" (
    powershell -Command "Start-Sleep -Seconds 1"
) else (
    powershell -Command "Start-Sleep -Seconds %~1"
)
goto :EOF

:CABECALHO_PASSO
echo.
call :LINHA
powershell -Command "Write-Host '  PASSO %~1/9  ' -ForegroundColor Cyan -NoNewline; Write-Host '|  ' -ForegroundColor DarkGray -NoNewline; Write-Host '%~2' -ForegroundColor Magenta"
call :LINHA
echo.
goto :EOF

:AGUARDANDO
powershell -Command "Write-Host '  ...  ' -ForegroundColor Blue -NoNewline; Write-Host '%~1' -ForegroundColor DarkGray"
goto :EOF

:: ═══════════════════════════════════════════════════════════════════════════════
::  TELA INICIAL
:: ══════════════════════════════════════════════════════════════════════════════

:TELA_INICIAL
cls
echo.
powershell -Command "Write-Host '  +=====================================================================+' -ForegroundColor Cyan"
powershell -Command "Write-Host '  |  ' -ForegroundColor Cyan -NoNewline; Write-Host 'ASI ^| Atlas de Suscetibilidade a Inundacoes    ' -ForegroundColor White -NoNewline; Write-Host '  |' -ForegroundColor Cyan"
powershell -Command "Write-Host '  |  ' -ForegroundColor Cyan -NoNewline; Write-Host 'Launcher Unificado v3.2  --  Windows           ' -ForegroundColor DarkGray -NoNewline; Write-Host '  |' -ForegroundColor Cyan"
powershell -Command "Write-Host '  |  ' -ForegroundColor Cyan -NoNewline; Write-Host 'DuckDB + Polars + GeoParquet + OpenTelemetry      ' -ForegroundColor DarkGray -NoNewline; Write-Host '  |' -ForegroundColor Cyan"
powershell -Command "Write-Host '  +=====================================================================+' -ForegroundColor Cyan"
echo.
powershell -Command "Write-Host '  Raiz do projeto: ' -NoNewline -ForegroundColor DarkGray; Write-Host '%BASE_DIR%' -ForegroundColor Cyan"
echo.

if exist "%STATE_FILE%" (
    powershell -Command "Write-Host '  Execucao anterior detectada! Passos concluidos serao acelerados.' -ForegroundColor Green"
    echo.
)

call :PAUSA_SEG 2
goto :PASSO1


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 1 — VERSÃO DO PYTHON (3.12+)
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO1
call :CABECALHO_PASSO 1 "Verificando versao do Python (3.12+)"
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

for /f "tokens=*" %%V in ('!PYTHON_BIN! -c "import sys; print(f\\\"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\\\")" 2^>nul') do set "PYTHON_VER=%%V"

call :INFO "Executavel : !PYTHON_BIN!"
call :INFO "Detectado  : Python !PYTHON_VER!"
call :INFO "Minimo     : Python 3.12"
echo.
call :OK "Python !PYTHON_VER! compativel!"
call :PAUSA_SEG 1
goto :PASSO2


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 2 — VERIFICA DADOS GEOESPACIAIS (GeoParquet)
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO2
call :CABECALHO_PASSO 2 "Verificando dados geoespaciais (GeoParquet)"
call :AGUARDANDO "Procurando pasta data/curated..."
call :PAUSA_SEG 1
echo.

if exist "%BASE_DIR%\data\curated\twi_points.parquet" (
    call :OK "Dados GeoParquet ja existentes — download nao necessario."
    call :INFO "Delete .asi_launcher_state para forcar re-download."
    call :PAUSA_SEG 1
    goto :PASSO3
)

call :AVISO "Dados GeoParquet nao encontrados. Serao baixados do GitHub Releases na execucao."
call :INFO "Fonte: https://github.com/LuciolLima/ASI/releases/tag/v3.1"
call :INFO "Arquivos: twi_points.parquet, bairros.parquet, hidro.parquet, eventos.parquet, defesa_civil.parquet"
echo.
call :OK "Verificacao concluida (download automatico no startup)."
call :PAUSA_SEG 1
goto :PASSO3


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 3 — VERIFICA ESTRUTURA DO PROJETO
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO3
call :CABECALHO_PASSO 3 "Verificando estrutura completa do projeto ASI v3.2"

if exist "%STATE_FILE%" (
    findstr /c:"estrutura_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Estrutura ja validada anteriormente."
        call :INFO "Delete .asi_launcher_state para revalidar."
        call :PAUSA_SEG 1
        goto :PASSO4
    )
)

set "ERROS_ESTR=0"

call :CHK_ARQ_E   "%BASE_DIR%\app.py"
call :CHK_ARQ_E   "%BASE_DIR%\requirements.txt"
call :CHK_ARQ_E   "%BASE_DIR%\pyproject.toml"
call :CHK_PASTA_E "%BASE_DIR%\src\api"
call :CHK_ARQ_E   "%BASE_DIR%\src\api\ibge_sidra.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\api\charts.py"
call :CHK_PASTA_E "%BASE_DIR%\src\core"
call :CHK_ARQ_E   "%BASE_DIR%\src\core\state.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\core\metrics.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\core\error_boundary.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\core\tracing.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\core\a11y.py"
call :CHK_PASTA_E "%BASE_DIR%\src\processing"
call :CHK_ARQ_E   "%BASE_DIR%\src\processing\data_layer.py"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\ui"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\ui\atoms"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\ui\molecules"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\ui\organisms"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\ui\layouts"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\ui\tokens.py"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\ui\theme.py"
call :CHK_PASTA_E "%BASE_DIR%\src\sigweb\map"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\map\package.json"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\map\vite.config.ts"
call :CHK_ARQ_E   "%BASE_DIR%\src\sigweb\map\src\AsiMap.tsx"
call :CHK_PASTA_E "%BASE_DIR%\monitoring"
call :CHK_ARQ_E   "%BASE_DIR%\docker-compose.monitoring.yml"
call :CHK_ARQ_E   "%BASE_DIR%\docker-compose.observability.yml"
call :CHK_PASTA_E "%BASE_DIR%\scripts"
call :CHK_ARQ_E   "%BASE_DIR%\scripts\convert_to_parquet.py"
call :CHK_ARQ_E   "%BASE_DIR%\scripts\benchmark.py"
call :CHK_PASTA_E "%BASE_DIR%\tests"
call :CHK_ARQ_E   "%BASE_DIR%\tests\unit\test_state.py"
call :CHK_ARQ_E   "%BASE_DIR%\docs\runbooks\incident_runbook.md"

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
goto :PASSO4

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


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 4 — INSTALA DEPENDÊNCIAS PYTHON
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO4
call :CABECALHO_PASSO 4 "Instalando dependencias Python (requirements.txt)"

if exist "%STATE_FILE%" (
    findstr /c:"deps_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Dependencias ja instaladas anteriormente."
        call :INFO "Delete .asi_launcher_state para reinstalar."
        call :PAUSA_SEG 1
        goto :PASSO5
    )
)

call :AGUARDANDO "Atualizando pip..."
!PYTHON_BIN! -m pip install --upgrade pip --quiet
call :OK "pip atualizado."
echo.

if exist "%BASE_DIR%\requirements.txt" (
    call :INFO "Usando: requirements.txt"
    echo.
    call :LINHA_FINA
    echo.
    !PYTHON_BIN! -m pip install -r "%BASE_DIR%\requirements.txt"
    echo.
    call :LINHA_FINA
) else (
    call :ERRO "requirements.txt nao encontrado!"
    echo.
    pause
    exit /b 1
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
goto :PASSO5


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 5 — VALIDA BIBLIOTECAS CORE
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO5
call :CABECALHO_PASSO 5 "Validando bibliotecas core instaladas"

if exist "%STATE_FILE%" (
    findstr /c:"deps_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Validacao ja realizada anteriormente."
        call :PAUSA_SEG 1
        goto :PASSO6
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
call :TST_LIB duckdb           duckdb
call :TST_LIB polars           polars
call :TST_LIB pyarrow          pyarrow
call :TST_LIB geopandas        geopandas
call :TST_LIB prometheus_client prometheus-client
call :TST_LIB opentelemetry_api opentelemetry-api

echo.
if !FALHAS_LIB! GTR 0 (
    call :ERRO "!FALHAS_LIB! biblioteca(s) com falha!"
    call :AVISO "Execute: pip install -r requirements.txt"
    echo.
    pause
    exit /b 1
)

call :OK "Todas as bibliotecas core funcionando!"

echo deps_ok>> "%STATE_FILE%"
call :PAUSA_SEG 1
goto :PASSO6

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


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 6 — BUILD MAPA REACT (Deck.gl + MapLibre)
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO6
call :CABECALHO_PASSO 6 "Build do componente React (Deck.gl + MapLibre)"

if exist "%STATE_FILE%" (
    findstr /c:"map_build_ok" "%STATE_FILE%" >nul 2>&1
    if !errorlevel! == 0 (
        call :OK "Build do mapa ja realizado anteriormente."
        call :INFO "Delete .asi_launcher_state para rebuild."
        call :PAUSA_SEG 1
        goto :PASSO7
    )
)

if not exist "%BASE_DIR%\src\sigweb\map\package.json" (
    call :AVISO "Projeto do mapa nao encontrado — pulando build."
    call :PAUSA_SEG 1
    goto :PASSO7
)

call :INFO "Instalando dependencias Node.js..."
cd /d "%BASE_DIR%\src\sigweb\map"
where npm >nul 2>&1
if !errorlevel! NEQ 0 (
    call :ERRO "npm nao encontrado! Instale Node.js 18+."
    echo.
    pause
    exit /b 1
)

call :AGUARDANDO "npm install..."
npm install --silent 2>&1 | findstr /v "warn" >nul
if !errorlevel! NEQ 0 (
    call :ERRO "Falha no npm install!"
    call :AVISO "Verifique conexao ou package.json."
    cd /d "%BASE_DIR%"
    echo.
    pause
    exit /b 1
)

call :OK "Dependencias Node instaladas."
call :AGUARDANDO "Build Vite (producao)..."
npm run build --silent 2>&1
if !errorlevel! NEQ 0 (
    call :ERRO "Falha no build Vite!"
    cd /d "%BASE_DIR%"
    echo.
    pause
    exit /b 1
)

call :OK "Build do mapa concluido com sucesso!"
echo map_build_ok>> "%STATE_FILE%"
cd /d "%BASE_DIR%"
call :PAUSA_SEG 1
goto :PASSO7


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 7 — TESTES UNITARIOS
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO7
call :CABECALHO_PASSO 7 "Executando testes unitarios (pytest)"

call :AGUARDANDO "Rodando pytest..."
!PYTHON_BIN! -m pytest tests/ -v --tb=short 2>&1 | findstr /r /c:"passed" /c:"failed" /c:"error"
if !errorlevel! NEQ 0 (
    call :ERRO "Testes falharam!"
    echo.
    pause
    exit /b 1
)

call :OK "Todos os testes passaram!"
call :PAUSA_SEG 1
goto :PASSO8


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 8 — STACK DE OBSERVABILIDADE (Docker Compose)
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO8
call :CABECALHO_PASSO 8 "Verificando stack de observabilidade (Docker)"

where docker >nul 2>&1
if !errorlevel! NEQ 0 (
    call :AVISO "Docker nao encontrado — stack de observabilidade nao sera iniciada."
    call :INFO "Instale Docker Desktop para habilitar: Prometheus, Grafana, Tempo, Loki, Pyroscope, Alertmanager."
    call :PAUSA_SEG 2
    goto :PASSO9
)

where docker-compose >nul 2>&1
if !errorlevel! NEQ 0 (
    call :AVISO "docker-compose nao encontrado."
    call :PAUSA_SEG 1
    goto :PASSO9
)

call :INFO "Docker detectado. Stack disponivel:"
call :INFO "  - Prometheus (9090) + Alertmanager (9093)"
call :INFO "  - Grafana (3000) + Loki (3100) + Promtail"
call :INFO "  - OpenTelemetry Collector (4317/4318) + Tempo (3200)"
call :INFO "  - Pyroscope (4040) + Node Exporter (9100)"
echo.
call :AVISO "Para iniciar a stack completa:"
call :INFO "  docker-compose -f docker-compose.monitoring.yml up -d"
call :AVISO "Para stack estendida (Tracing + Profiling):"
call :INFO "  docker-compose -f docker-compose.observability.yml up -d"
echo.
call :OK "Docker disponivel. Stack pronta para uso."
call :PAUSA_SEG 1
goto :PASSO9


:: ══════════════════════════════════════════════════════════════════════════════
::  PASSO 9 — EXECUTAR SIGWEB
:: ══════════════════════════════════════════════════════════════════════════════

:PASSO9
call :CABECALHO_PASSO 9 "Iniciar o SIGWeb ASI v3.2"

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
powershell -Command "Write-Host '  URLs de acesso:' -ForegroundColor DarkGray"
powershell -Command "Write-Host '    Local:      http://localhost:8501' -ForegroundColor Cyan"
powershell -Command "Write-Host '    Network:    http://<seu-ip>:8501' -ForegroundColor Cyan"
powershell -Command "Write-Host '    Health:     http://localhost:8501/?_health=1' -ForegroundColor Cyan"
echo.
call :LINHA_FINA
echo.
call :INFO "Pressione ENTER para iniciar o ASI..."
pause >nul

call :LINHA
echo.
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

:: Fim do script
exit /b 0