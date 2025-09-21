@echo off
REM Script para generar videos con subtítulos al estilo TikTok
REM Uso: tiktok_subtitles.bat video.mp4 subtitulos.srt [output.mp4]

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo.
    echo ========================================
    echo  Generador de Subtítulos TikTok
    echo ========================================
    echo.
    echo Uso: %~nx0 ^<video^> ^<subtitulos.srt^> [salida.mp4]
    echo.
    echo Ejemplos:
    echo   %~nx0 mi_video.mp4 subtitulos.srt
    echo   %~nx0 mi_video.mp4 subtitulos.srt video_final.mp4
    echo.
    echo Opciones adicionales:
    echo   --font-size 80          - Tamaño de fuente
    echo   --font-color yellow     - Color del texto
    echo   --stroke-width 4        - Grosor del contorno
    echo   --background-opacity 0.3 - Opacidad del fondo
    echo   --tiktok                 - Convertir a formato TikTok (9:16)
    echo   --resolution 720x1280   - Resolución personalizada
    echo   --crop-mode center      - Modo de recorte (center/top/bottom)
    echo.
    echo Ejemplos TikTok:
    echo   %~nx0 video.mp4 subs.srt --tiktok
    echo   %~nx0 video.mp4 subs.srt --resolution 720x1280
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: Debes especificar tanto el video como el archivo de subtítulos.
    echo Uso: %~nx0 ^<video^> ^<subtitulos.srt^> [salida.mp4]
    pause
    exit /b 1
)

set "VIDEO=%~1"
set "SUBTITULOS=%~2"
set "SALIDA=%~3"

REM Verificar que los archivos existen
if not exist "%VIDEO%" (
    echo ERROR: Video no encontrado: %VIDEO%
    pause
    exit /b 1
)

if not exist "%SUBTITULOS%" (
    echo ERROR: Archivo de subtítulos no encontrado: %SUBTITULOS%
    pause
    exit /b 1
)

REM Si no se especifica salida, generar nombre automático
if "%SALIDA%"=="" (
    for %%F in ("%VIDEO%") do (
        set "NOMBRE=%%~nF"
        set "EXT=%%~xF"
    )
    set "SALIDA=!NOMBRE!_con_subtitulos!EXT!"
)

echo.
echo ========================================
echo  Generando video con subtítulos TikTok
echo ========================================
echo Video de entrada: %VIDEO%
echo Subtítulos:       %SUBTITULOS%
echo Video de salida:  %SALIDA%
echo ========================================
echo.

REM Ejecutar el script Python
python tiktok_subtitle_overlay.py "%VIDEO%" "%SUBTITULOS%" -o "%SALIDA%" %4 %5 %6 %7 %8 %9

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡Video generado exitosamente!
    echo 📁 Archivo: %SALIDA%
    echo.
    
    REM Preguntar si quiere abrir el archivo
    set /p "ABRIR=¿Quieres abrir el video generado? (s/N): "
    if /i "!ABRIR!"=="s" (
        start "" "%SALIDA%"
    )
) else (
    echo.
    echo ❌ Error generando el video.
    echo Revisa los mensajes de error anteriores.
    echo.
)

echo.
pause