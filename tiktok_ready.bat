@echo off
REM Script especializado para generar videos TikTok con subtítulos
REM Uso: tiktok_ready.bat video.mp4 subtitulos.srt [salida.mp4] [modo_recorte]

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo.
    echo ========================================
    echo  🎯 Generador TikTok Ready
    echo ========================================
    echo.
    echo Convierte videos a formato TikTok (9:16) con subtítulos
    echo.
    echo Uso: %~nx0 ^<video^> ^<subtitulos.srt^> [salida.mp4] [modo_recorte]
    echo.
    echo Modos de recorte:
    echo   center - Recorta desde el centro (por defecto)
    echo   top    - Mantiene la parte superior
    echo   bottom - Mantiene la parte inferior
    echo.
    echo Ejemplos:
    echo   %~nx0 gameplay.mp4 subtitulos.srt
    echo   %~nx0 gameplay.mp4 subtitulos.srt tiktok_video.mp4
    echo   %~nx0 gameplay.mp4 subtitulos.srt tiktok_video.mp4 top
    echo.
    echo ✨ Formato de salida: 1080x1920 (TikTok Ready)
    echo ✨ Tamaño de fuente optimizado automáticamente
    echo ✨ Subtítulos estilo TikTok con contorno
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: Debes especificar tanto el video como el archivo de subtítulos.
    echo Uso: %~nx0 ^<video^> ^<subtitulos.srt^> [salida.mp4] [modo_recorte]
    pause
    exit /b 1
)

set "VIDEO=%~1"
set "SUBTITULOS=%~2"
set "SALIDA=%~3"
set "MODO_RECORTE=%~4"

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
    set "SALIDA=!NOMBRE!_tiktok!EXT!"
)

REM Modo de recorte por defecto
if "%MODO_RECORTE%"=="" (
    set "MODO_RECORTE=center"
)

echo.
echo ========================================
echo  🎯 Generando Video TikTok Ready
echo ========================================
echo Video de entrada: %VIDEO%
echo Subtítulos:       %SUBTITULOS%
echo Video de salida:  %SALIDA%
echo Modo de recorte:  %MODO_RECORTE%
echo Formato:          1080x1920 (9:16)
echo ========================================
echo.

REM Ejecutar el script Python con configuración TikTok optimizada
python tiktok_subtitle_overlay.py "%VIDEO%" "%SUBTITULOS%" ^
    -o "%SALIDA%" ^
    --tiktok ^
    --crop-mode %MODO_RECORTE% ^
    --font-color white ^
    --stroke-color black ^
    --stroke-width 4 ^
    --background-opacity 0.2

if %errorlevel% equ 0 (
    echo.
    echo ✅ ¡Video TikTok generado exitosamente!
    echo 📁 Archivo: %SALIDA%
    echo 🎯 Formato: 1080x1920 (TikTok Ready)
    echo 📱 Listo para subir a TikTok, Instagram Reels, YouTube Shorts
    echo.
    
    REM Preguntar si quiere abrir el archivo
    set /p "ABRIR=¿Quieres abrir el video TikTok? (s/N): "
    if /i "!ABRIR!"=="s" (
        start "" "%SALIDA%"
    )
    
    echo.
    echo 💡 Consejos para TikTok:
    echo    - Verifica que el contenido principal esté visible
    echo    - Los subtítulos están optimizados para lectura móvil
    echo    - El formato 9:16 es perfecto para feeds verticales
    
) else (
    echo.
    echo ❌ Error generando el video TikTok.
    echo Revisa los mensajes de error anteriores.
    echo.
    echo 💡 Consejos:
    echo    - Verifica que el video original no esté corrupto
    echo    - Asegúrate de tener espacio suficiente en disco
    echo    - Prueba con un modo de recorte diferente (top/center/bottom)
)

echo.
pause