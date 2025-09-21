@echo off
setlocal enabledelayedexpansion

:: ===============================================
:: 🎮 GameClipping - Transcripción de Precisión
:: ===============================================
:: Script para transcripción de máxima calidad
:: Uso: transcribe_precision.bat archivo_audio.wav
:: ===============================================

if "%~1"=="" (
    echo.
    echo ╔══════════════════════════════════════════════════════════════════╗
    echo ║             🎯 Transcripción de Máxima Precisión                ║
    echo ╚══════════════════════════════════════════════════════════════════╝
    echo.
    echo ❌ Error: Especifica un archivo de audio
    echo.
    echo 💡 Uso: transcribe_precision.bat archivo_audio.wav
    echo.
    echo 🎯 Características:
    echo    • Máxima precisión y calidad
    echo    • VAD Híbrido activo
    echo    • Análisis contextual completo
    echo    • Sistema multipass 5-pasadas
    echo    • Aprendizaje adaptativo
    echo    • Información detallada incluida
    echo.
    echo ⚠️ Nota: Procesamiento más lento pero máxima calidad
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║             🎯 Transcripción de Máxima Precisión                ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Verificar entorno virtual
if not exist "venv\Scripts\python.exe" (
    echo ❌ Error: Entorno virtual no encontrado
    echo 💡 Ejecuta primero: install_vad_system.bat
    pause
    exit /b 1
)

:: Usar entorno virtual
echo 🔄 Usando entorno VAD Gaming...

:: Verificar archivo
set "INPUT_FILE=%~1"
if not exist "%INPUT_FILE%" (
    echo ❌ Error: Archivo no encontrado: %INPUT_FILE%
    pause
    exit /b 1
)

echo ✅ Archivo de entrada: %INPUT_FILE%

:: Preparar salidas
set "OUTPUT_BASE=%~n1"
set "OUTPUT_DIR=output"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "OUTPUT_TXT=%OUTPUT_DIR%\%OUTPUT_BASE%_precision.txt"
set "OUTPUT_SRT=%OUTPUT_DIR%\%OUTPUT_BASE%_precision.srt"
set "OUTPUT_JSON=%OUTPUT_DIR%\%OUTPUT_BASE%_detailed.json"

echo.
echo 📁 Archivos de salida:
echo    📄 TXT detallado: %OUTPUT_TXT%
echo    📺 SRT avanzado:  %OUTPUT_SRT%
echo    📊 JSON completo: %OUTPUT_JSON%
echo.

:: Mostrar configuración
echo 🔧 Configuración de Precisión Activada:
echo    ✅ VAD Híbrido (Silero + PyAnnote + WebRTC)
echo    ✅ Análisis Contextual Gaming
echo    ✅ Sistema Multipass 5-pasadas
echo    ✅ Aprendizaje Adaptativo
echo    ✅ Preprocesamiento VAD
echo    ✅ Información de confianza
echo    ✅ Exportación detallada
echo.

:: Confirmar procesamiento
echo ⚠️ ADVERTENCIA: El modo precisión puede tomar considerablemente más tiempo
echo    pero ofrece la máxima calidad posible.
echo.
choice /c YN /m "¿Continuar con transcripción de precisión? (Y/N)"
if !errorlevel!==2 (
    echo 🔚 Procesamiento cancelado por el usuario
    pause
    exit /b 0
)

echo.
echo 🎯 Iniciando transcripción de máxima precisión...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: Medir tiempo de inicio
set "START_TIME=%time%"

:: Ejecutar transcripción de precisión
venv\Scripts\python.exe transcribe_vad_advanced.py "%INPUT_FILE%" ^
    --output "%OUTPUT_TXT%" ^
    --profile precision ^
    --user "precision_user" ^
    --verbose

set "TRANSCRIBE_RESULT=%errorlevel%"
set "END_TIME=%time%"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if %TRANSCRIBE_RESULT% equ 0 (
    echo ✅ Transcripción de precisión completada exitosamente!
    echo.
    echo ⏱️ Tiempo de procesamiento: %START_TIME% - %END_TIME%
    echo.
    
    :: Verificar y mostrar archivos
    if exist "%OUTPUT_TXT%" (
        echo 📄 Archivo TXT creado: %OUTPUT_TXT%
        
        :: Obtener tamaño del archivo
        for %%A in ("%OUTPUT_TXT%") do set "FILE_SIZE=%%~zA"
        echo    📏 Tamaño: !FILE_SIZE! bytes
        
        echo.
        echo 👀 Vista previa de transcripción:
        echo ╭────────────────────────────────────────╮
        type "%OUTPUT_TXT%" | more +0
        echo ╰────────────────────────────────────────╯
    )
    
    if exist "%OUTPUT_SRT%" (
        echo.
        echo 📺 Archivo SRT avanzado creado: %OUTPUT_SRT%
        echo    🏷️ Incluye información contextual y confianza
    )
    
    if exist "%OUTPUT_JSON%" (
        echo.
        echo 📊 Archivo JSON detallado creado: %OUTPUT_JSON%
        echo    🔍 Contiene análisis completo y métricas
        
        :: Mostrar algunas estadísticas del JSON
        echo.
        echo 📈 Estadísticas rápidas:
        python -c "
import json
try:
    with open('%OUTPUT_JSON%', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'    🎯 Confianza general: {data.get(\"overall_confidence\", 0):.2f}')
    print(f'    🎮 Contexto dominante: {data.get(\"dominant_context\", \"unknown\")}')
    print(f'    📊 Ratio de speech: {data.get(\"speech_ratio\", 0):.2f}')
    print(f'    ⏱️ Tiempo procesamiento: {data.get(\"processing_time\", 0):.1f}s')
    print(f'    🔧 Modelos VAD usados: {len(data.get(\"vad_models_used\", []))}')
except Exception as e:
    print(f'    ⚠️ Error leyendo estadísticas: {e}')
" 2>nul
    )
    
    echo.
    echo 🎉 ¡Transcripción de máxima precisión completada!
    echo.
    echo 💡 Archivos generados:
    echo    📄 Texto: %OUTPUT_TXT%
    echo    📺 SRT:   %OUTPUT_SRT%
    echo    📊 JSON:  %OUTPUT_JSON%
    echo.
    
    :: Opciones post-procesamiento
    echo 🔧 Opciones disponibles:
    echo    [1] Abrir archivo de texto
    echo    [2] Abrir archivo SRT
    echo    [3] Ver estadísticas JSON
    echo    [4] Abrir carpeta de salida
    echo    [5] Salir
    echo.
    
    choice /c 12345 /m "Selecciona una opción"
    
    if !errorlevel!==1 (
        notepad "%OUTPUT_TXT%"
    ) else if !errorlevel!==2 (
        if exist "%OUTPUT_SRT%" (
            notepad "%OUTPUT_SRT%"
        ) else (
            echo ⚠️ Archivo SRT no encontrado
        )
    ) else if !errorlevel!==3 (
        if exist "%OUTPUT_JSON%" (
            notepad "%OUTPUT_JSON%"
        ) else (
            echo ⚠️ Archivo JSON no encontrado
        )
    ) else if !errorlevel!==4 (
        explorer "%OUTPUT_DIR%"
    )
    
) else (
    echo ❌ Error en la transcripción de precisión
    echo.
    echo 💡 Posibles causas y soluciones:
    echo    • Audio corrupto o formato no soportado
    echo      → Convierte a WAV: ffmpeg -i input.mp4 -ar 16000 output.wav
    echo.
    echo    • Memoria insuficiente
    echo      → Prueba con: transcribe_gaming.bat "%INPUT_FILE%"
    echo.
    echo    • Modelos no instalados correctamente
    echo      → Ejecuta: python verify_installation.py
    echo.
    echo    • Dependencias faltantes
    echo      → Reejecuta: install_vad_system.bat
    echo.
    echo 📚 Consulta README_VAD_ADVANCED.md para troubleshooting detallado
    echo.
)

echo.
echo 🔚 Proceso de precisión terminado
pause