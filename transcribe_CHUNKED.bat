@echo off
echo ================================================================
echo    🎯 TRANSCRIPTOR ULTRA-GRADUAL (MAX 3 PALABRAS)
echo    Subtítulos que aparecen palabra por palabra naturalmente
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
echo 🔄 Iniciando transcripción ultra-gradual (máximo 3 palabras)...
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
    echo ✅ ¡CHUNKING ULTRA-GRADUAL COMPLETADO!
    echo 📄 Archivo generado: %srt_file%
    echo.
    echo 🎯 Los subtítulos ahora aparecen máximo 3 palabras
    echo    a la vez, creando lectura ultra-natural
    echo.
) else (
    echo.
    echo ❌ No se pudo generar el archivo de subtítulos
    echo.
)

echo Presiona cualquier tecla para continuar...
pause >nul