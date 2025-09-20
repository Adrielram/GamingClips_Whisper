@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
REM Script de Windows para transcribir videos de gaming
REM Uso: transcribe.bat video.mp4

if "%~1"=="" (
    echo.
    echo ❌ Error: Debes especificar el archivo de video a transcribir
    echo.
    echo 📖 Uso:
    echo     transcribe.bat video.mp4
    echo     transcribe.bat "C:\path\to\video.mkv"
    echo.
    echo 🎯 El script generará automáticamente:
    echo     - Archivo .srt con el mismo nombre del video
    echo     - Configuración optimizada para gaming argentino
    echo     - Máxima calidad de transcripción
    echo.
    echo 💡 También puedes arrastrar el video directamente al archivo .bat
    echo.
    pause
    exit /b 1
)

REM Obtener directorio del script
set "SCRIPT_DIR=%~dp0"
set "VIDEO_PATH=%~1"
set "VIDEO_NAME=%~n1"

echo 🎮 Transcriptor de Gaming - Configuración Optimizada
echo ============================================================
echo 📹 Video: %VIDEO_PATH%
echo 📝 Salida: %VIDEO_NAME%.srt
echo 📁 Directorio del proyecto: %SCRIPT_DIR%
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

REM Verificar que main.py existe
if not exist "main.py" (
    echo ❌ Error: No se encontró main.py en el directorio del proyecto
    echo    Directorio actual: %CD%
    echo    Buscando: main.py
    echo.
    echo 🔧 Asegúrate de ejecutar el script desde la carpeta GameClipping
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist "venv310\Scripts\activate.bat" (
    echo ⚡ Activando entorno virtual...
    call "venv310\Scripts\activate.bat"
) else (
    echo ⚠️  No se encontró entorno virtual venv310, usando Python del sistema
)

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    echo.
    echo 🔧 Instala Python desde: https://python.org
    pause
    exit /b 1
)

echo ⚙️  Python detectado: 
python --version

echo.
echo 🚀 Iniciando transcripción...
echo ⏳ Esto puede tomar varios minutos...
echo.

REM Ejecutar transcripción
python "%SCRIPT_DIR%transcribe.py" "%VIDEO_PATH%"

if errorlevel 1 (
    echo.
    echo ❌ Error en la transcripción
    echo.
    echo 🔧 Posibles soluciones:
    echo     • Verificar que el video no esté corrupto
    echo     • Instalar dependencias: pip install -r requirements.txt
    echo     • Verificar que FFmpeg esté instalado
    echo     • Revisar el log de errores arriba
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ ¡Transcripción completada!
echo 📁 Busca el archivo .srt en la misma carpeta que tu video
pause