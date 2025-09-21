@echo off
setlocal enabledelayedexpansion

:: ===============================================
:: 🎮 GameClipping - Procesamiento en Lote
:: ===============================================
:: Script para transcribir múltiples archivos
:: Uso: batch_transcribe.bat "*.wav" [perfil]
:: ===============================================

if "%~1"=="" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║               🔄 Procesamiento en Lote                          ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo ❌ Error: Especifica un patrón de archivos
    echo.
    echo 💡 Uso: batch_transcribe.bat "patrón" [perfil]
    echo.
    echo 🎯 Ejemplos:
    echo    batch_transcribe.bat "*.wav"
    echo    batch_transcribe.bat "*.mp3" gaming
    echo    batch_transcribe.bat "gameplay_*.wav" precision
    echo    batch_transcribe.bat "C:\audio\*.m4a" fast
    echo.
    echo 📋 Perfiles disponibles:
    echo    • gaming    - Optimizado para gaming (por defecto)
    echo    • precision - Máxima calidad
    echo    • fast      - Procesamiento rápido
    echo    • streaming - Para contenido streaming
    echo.
    pause
    exit /b 1
)

:: Configurar parámetros
set "FILE_PATTERN=%~1"
set "PROFILE=%~2"
if "%PROFILE%"=="" set "PROFILE=gaming"

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║               🔄 Procesamiento en Lote                          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo 📁 Patrón de archivos: %FILE_PATTERN%
echo 🎯 Perfil seleccionado: %PROFILE%
echo.

:: Verificar entorno virtual
if not exist "venv\Scripts\python.exe" (
    echo ❌ Error: Entorno virtual no encontrado
    echo 💡 Ejecuta primero: install_vad_system.bat
    pause
    exit /b 1
)

:: Activar entorno virtual
echo 🔄 Activando entorno VAD Gaming...
echo 🔄 Usando entorno VAD Gaming...

:: Preparar directorio de salida
set "OUTPUT_DIR=output_batch_%PROFILE%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
echo 📂 Directorio de salida: %OUTPUT_DIR%
echo.

:: Buscar archivos que coincidan con el patrón
echo 🔍 Buscando archivos...
set "FILE_COUNT=0"
set "FILES_LIST="

for %%F in (%FILE_PATTERN%) do (
    set /a FILE_COUNT+=1
    echo    [!FILE_COUNT!] %%F
    set "FILES_LIST=!FILES_LIST! "%%F""
)

if %FILE_COUNT%==0 (
    echo ❌ No se encontraron archivos que coincidan con: %FILE_PATTERN%
    echo.
    echo 💡 Verificar:
    echo    • Ruta correcta
    echo    • Extensión del archivo
    echo    • Permisos de lectura
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Encontrados %FILE_COUNT% archivos para procesar
echo.

:: Confirmar procesamiento
echo ⚠️ Se procesarán %FILE_COUNT% archivos con perfil '%PROFILE%'
echo 📊 Tiempo estimado: %FILE_COUNT% x 2-10 minutos (dependiendo del perfil)
echo.
choice /c YN /m "¿Continuar con el procesamiento en lote? (Y/N)"
if !errorlevel!==2 (
    echo 🔚 Procesamiento cancelado por el usuario
    pause
    exit /b 0
)

:: Inicializar contadores
set "PROCESSED=0"
set "SUCCESS=0"
set "ERRORS=0"
set "START_BATCH_TIME=%time%"

echo.
echo 🚀 Iniciando procesamiento en lote...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Crear log de procesamiento
set "LOG_FILE=%OUTPUT_DIR%\batch_log.txt"
echo Batch Processing Log - %date% %time% > "%LOG_FILE%"
echo Profile: %PROFILE% >> "%LOG_FILE%"
echo Files Pattern: %FILE_PATTERN% >> "%LOG_FILE%"
echo Total Files: %FILE_COUNT% >> "%LOG_FILE%"
echo ========================== >> "%LOG_FILE%"

:: Procesar cada archivo
for %%F in (%FILE_PATTERN%) do (
    set /a PROCESSED+=1
    set "CURRENT_FILE=%%F"
    set "BASE_NAME=%%~nF"
    set "FILE_START_TIME=!time!"
    
    echo [!PROCESSED!/%FILE_COUNT%] Procesando: !CURRENT_FILE!
    echo.
    
    :: Generar nombres de salida
    set "OUTPUT_TXT=%OUTPUT_DIR%\!BASE_NAME!_%PROFILE%.txt"
    set "OUTPUT_SRT=%OUTPUT_DIR%\!BASE_NAME!_%PROFILE%.srt"
    
    :: Ejecutar transcripción
    venv\Scripts\python.exe transcribe_vad_advanced.py "!CURRENT_FILE!" ^
        --output "!OUTPUT_TXT!" ^
        --profile %PROFILE% ^
        --user "batch_user" > nul 2>&1
    
    set "RESULT=!errorlevel!"
    set "FILE_END_TIME=!time!"
    
    if !RESULT! equ 0 (
        set /a SUCCESS+=1
        echo    ✅ Completado: !BASE_NAME!
        
        :: Log success
        echo [!FILE_START_TIME!] SUCCESS: !CURRENT_FILE! >> "%LOG_FILE%"
        
        :: Verificar archivos generados
        if exist "!OUTPUT_TXT!" (
            for %%A in ("!OUTPUT_TXT!") do set "TXT_SIZE=%%~zA"
            echo       📄 TXT: !TXT_SIZE! bytes
        )
        
        if exist "!OUTPUT_SRT!" (
            echo       📺 SRT: Generado
        )
        
    ) else (
        set /a ERRORS+=1
        echo    ❌ Error: !BASE_NAME!
        
        :: Log error
        echo [!FILE_START_TIME!] ERROR: !CURRENT_FILE! >> "%LOG_FILE%"
    )
    
    echo    ⏱️ Tiempo: !FILE_START_TIME! - !FILE_END_TIME!
    echo.
    echo ──────────────────────────────────────────────────────────────────
    echo.
)

set "END_BATCH_TIME=%time%"

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🏁 Procesamiento en lote completado
echo.
echo 📊 Estadísticas finales:
echo    📁 Archivos procesados: %PROCESSED%
echo    ✅ Exitosos: %SUCCESS%
echo    ❌ Errores: %ERRORS%
echo    📈 Tasa de éxito: 
if %PROCESSED% gtr 0 (
    set /a SUCCESS_RATE=!SUCCESS!*100/!PROCESSED!
    echo !SUCCESS_RATE!%%
) else (
    echo 0%%
)
echo    ⏱️ Tiempo total: %START_BATCH_TIME% - %END_BATCH_TIME%
echo.

:: Completar log
echo ========================== >> "%LOG_FILE%"
echo SUMMARY >> "%LOG_FILE%"
echo Processed: %PROCESSED% >> "%LOG_FILE%"
echo Success: %SUCCESS% >> "%LOG_FILE%"
echo Errors: %ERRORS% >> "%LOG_FILE%"
echo End Time: %END_BATCH_TIME% >> "%LOG_FILE%"

:: Mostrar archivos generados
if %SUCCESS% gtr 0 (
    echo 📂 Archivos generados en: %OUTPUT_DIR%
    echo.
    echo 📄 Archivos de texto:
    dir /b "%OUTPUT_DIR%\*.txt" 2>nul | findstr /v "batch_log.txt"
    
    echo.
    echo 📺 Archivos SRT:
    dir /b "%OUTPUT_DIR%\*.srt" 2>nul
    
    echo.
    echo 📋 Log detallado: %LOG_FILE%
    
    echo.
    echo 🔧 Opciones disponibles:
    echo    [1] Abrir carpeta de resultados
    echo    [2] Ver log de procesamiento
    echo    [3] Crear resumen JSON
    echo    [4] Salir
    echo.
    
    choice /c 1234 /m "Selecciona una opción"
    
    if !errorlevel!==1 (
        explorer "%OUTPUT_DIR%"
    ) else if !errorlevel!==2 (
        notepad "%LOG_FILE%"
    ) else if !errorlevel!==3 (
        echo 📊 Generando resumen JSON...
        
        :: Crear resumen JSON básico
        echo { > "%OUTPUT_DIR%\batch_summary.json"
        echo   "profile": "%PROFILE%", >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "pattern": "%FILE_PATTERN%", >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "total_files": %FILE_COUNT%, >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "processed": %PROCESSED%, >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "success": %SUCCESS%, >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "errors": %ERRORS%, >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "start_time": "%START_BATCH_TIME%", >> "%OUTPUT_DIR%\batch_summary.json"
        echo   "end_time": "%END_BATCH_TIME%" >> "%OUTPUT_DIR%\batch_summary.json"
        echo } >> "%OUTPUT_DIR%\batch_summary.json"
        
        echo ✅ Resumen JSON creado: %OUTPUT_DIR%\batch_summary.json
    )
    
) else (
    echo ❌ No se generaron archivos exitosamente
    echo.
    echo 💡 Posibles soluciones:
    echo    • Verificar formato de audio soportado
    echo    • Ejecutar: python verify_installation.py
    echo    • Probar con un solo archivo primero
    echo    • Revisar log: %LOG_FILE%
    echo.
)

echo.
echo 🔚 Procesamiento en lote terminado
pause