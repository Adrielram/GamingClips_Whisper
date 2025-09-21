@echo off
echo ================================================================
echo    🎯 TRANSCRIPTOR CON CHUNKING INTELIGENTE
echo    Segmenta subtítulos para mostrar palabras gradualmente
echo ================================================================
echo.

REM Verificar si se pasó un archivo
if "%~1"=="" (
    echo ❌ Por favor, arrastra un archivo de video a este .bat
    echo.
    pause
    exit /b 1
)

REM Verificar si el archivo existe
if not exist "%~1" (
    echo ❌ El archivo no existe: %~1
    echo.
    pause
    exit /b 1
)

echo 📹 Archivo: %~1
echo 🔄 Iniciando transcripción con chunking...
echo.

REM Activar entorno virtual y ejecutar
cd /d "%~dp0"
call venv310\Scripts\activate.bat
python transcribe_chunked.py "%~1"

REM Verificar si se generó el archivo
set "filename=%~n1"
set "output_dir=%~dp1"
set "srt_file=%output_dir%%filename%_chunked.srt"

if exist "%srt_file%" (
    echo.
    echo ✅ ¡CHUNKING COMPLETADO!
    echo 📄 Archivo generado: %srt_file%
    echo.
    echo 🎯 Los subtítulos ahora se muestran gradualmente
    echo    en fragmentos de 40-45 caracteres máximo
    echo.
) else (
    echo.
    echo ❌ No se pudo generar el archivo de subtítulos
    echo.
)

echo Presiona cualquier tecla para continuar...
pause >nul