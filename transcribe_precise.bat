@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM Script para transcripción ULTRA-PRECISA con sincronización perfecta
REM Uso: Arrastra tu video al archivo .bat

if "%~1"=="" (
    echo.
    echo 🎯 TRANSCRIPCIÓN ULTRA-PRECISA
    echo ================================
    echo.
    echo ❌ Error: Debes especificar el archivo de video a transcribir
    echo.
    echo 📖 Uso:
    echo     transcribe_precise.bat video.mp4
    echo     O arrastra el video directamente a este archivo
    echo.
    echo ✨ Características ULTRA-PRECISAS:
    echo     • Sincronización palabra por palabra
    echo     • Timestamps con precisión de milisegundos
    echo     • Forced alignment con WhisperX
    echo     • Optimizado para gaming argentino
    echo     • Subtítulos cortos (máx 6 palabras)
    echo.
    pause
    exit /b 1
)

REM Obtener información del archivo
set "SCRIPT_DIR=%~dp0"
set "VIDEO_PATH=%~1"
set "VIDEO_NAME=%~n1"

echo 🎯 TRANSCRIPCIÓN ULTRA-PRECISA
echo =====================================
echo 📹 Video: %VIDEO_PATH%
echo 📝 Salida: %VIDEO_NAME%.srt
echo 📁 Directorio: %SCRIPT_DIR%
echo.
echo ✨ Técnicas aplicadas:
echo     🔬 Word-level timestamps
echo     🎯 Forced alignment (WhisperX)
echo     📏 VAD preciso
echo     🎮 Gaming argentino optimizado
echo     ⏱️ Post-procesamiento temporal
echo.

REM Verificar que el video existe
if not exist "%VIDEO_PATH%" (
    echo ❌ Error: No se encontró el archivo de video
    echo    Ruta: %VIDEO_PATH%
    echo.
    pause
    exit /b 1
)

REM Cambiar al directorio del script
cd /d "%SCRIPT_DIR%"

REM Verificar que transcribe_precise.py existe
if not exist "transcribe_precise.py" (
    echo ❌ Error: No se encontró transcribe_precise.py
    echo    Directorio actual: %CD%
    echo.
    echo 🔧 Asegúrate de ejecutar desde la carpeta GameClipping
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist "venv310\Scripts\activate.bat" (
    echo ⚡ Activando entorno virtual...
    call "venv310\Scripts\activate.bat"
    echo.
) else (
    echo ⚠️  Usando Python del sistema (sin entorno virtual)
    echo.
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo.
    echo 🔧 Instala Python desde: https://python.org
    pause
    exit /b 1
)

echo 🐍 Python detectado: 
python --version
echo.

REM Verificar dependencias críticas
echo 🔍 Verificando dependencias...
python -c "import faster_whisper; print('✅ faster-whisper OK')" 2>nul || (
    echo ❌ faster-whisper no encontrado
    echo 💡 Instala con: pip install faster-whisper
    echo.
    pause
    exit /b 1
)

python -c "import whisperx; print('✅ whisperx OK')" 2>nul || (
    echo ⚠️  whisperx no encontrado (funcionalidad reducida)
    echo 💡 Para máxima precisión instala: pip install whisperx
    echo.
)

echo.
echo 🚀 INICIANDO TRANSCRIPCIÓN ULTRA-PRECISA...
echo ⏳ Esto puede tomar varios minutos para máxima calidad...
echo 💡 El proceso incluye múltiples etapas de refinamiento
echo.

REM Ejecutar transcripción ultra-precisa
python "%SCRIPT_DIR%transcribe_precise.py" "%VIDEO_PATH%"

if errorlevel 1 (
    echo.
    echo ❌ Error en la transcripción ultra-precisa
    echo.
    echo 🔄 Intentando método de respaldo estándar...
    echo.
    
    REM Método de respaldo
    python "%SCRIPT_DIR%transcribe.py" "%VIDEO_PATH%"
    
    if errorlevel 1 (
        echo ❌ Error también en método de respaldo
        echo.
        echo 🔧 Posibles soluciones:
        echo     • Verificar que el video no esté corrupto
        echo     • Instalar dependencias: pip install -r requirements.txt
        echo     • Verificar que FFmpeg esté instalado
        echo     • Probar con un video más corto primero
        echo     • Revisar espacio en disco disponible
        echo.
        pause
        exit /b 1
    ) else (
        echo.
        echo ✅ Transcripción de respaldo completada
        echo 📝 Se usó método estándar en lugar de ultra-preciso
    )
) else (
    echo.
    echo 🎉 ¡TRANSCRIPCIÓN ULTRA-PRECISA COMPLETADA!
    echo ===============================================
    echo.
    echo 📁 Archivo generado: %VIDEO_NAME%.srt
    echo 📍 Ubicación: Misma carpeta que tu video
    echo.
    echo ✨ Características del archivo:
    echo     🎯 Sincronización palabra por palabra
    echo     ⏱️ Precisión de milisegundos
    echo     📏 Líneas cortas para mejor lectura
    echo     🎮 Optimizado para gaming argentino
    echo     🔬 Procesado con IA avanzada
    echo.
    echo 💡 Consejos de uso:
    echo     • Usa en reproductores que soporten SRT
    echo     • Ajusta tamaño de fuente si es necesario
    echo     • Verifica sincronización en momentos clave
    echo     • Si hay pequeños desfases, usa sync_adjust.py
)

echo.
echo 🏁 Proceso finalizado
pause