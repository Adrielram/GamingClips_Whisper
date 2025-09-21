# Generador de Subtítulos TikTok

Este componente permite añadir subtítulos al estilo TikTok a cualquier video, utilizando archivos de subtítulos .srt generados por el sistema de transcripción.

## 🎯 Características

- **Estilo TikTok**: Subtítulos grandes, centrados, con contorno y posicionados en la parte inferior
- **Formato TikTok Ready**: Conversión automática a 9:16 (1080x1920) para TikTok/Instagram Reels
- **Resoluciones personalizadas**: Configura cualquier resolución personalizada
- **Modos de recorte**: Centro, superior o inferior para videos horizontales
- **Personalizable**: Tamaño de fuente, colores, contorno y fondo ajustables
- **Automático**: Parsea archivos .srt y sincroniza automáticamente con el video
- **Múltiples líneas**: Divide automáticamente texto largo en líneas apropiadas
- **Fácil de usar**: Interfaz de línea de comandos simple

## 🚀 Instalación

1. Instalar dependencias:
```bash
pip install moviepy>=1.0.3
```

2. O instalar todas las dependencias del proyecto:
```bash
pip install -r requirements.txt
```

## 📖 Uso

### Uso Básico

```bash
# Generar video con subtítulos usando configuración por defecto
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt

# Especificar archivo de salida
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt -o video_final.mp4
```

### 🎯 TikTok Ready (NUEVO)

```bash
# Convertir automáticamente a formato TikTok (9:16, 1080x1920)
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --tiktok

# Con modo de recorte específico
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --tiktok --crop-mode top

# Script batch especializado para TikTok
tiktok_ready.bat video.mp4 subtitulos.srt
```

### 📱 Resoluciones Personalizadas

```bash
# Instagram Stories (9:16)
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --resolution 1080x1920

# YouTube Shorts (9:16)
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --resolution 1080x1920

# TikTok HD
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --resolution 720x1280

# Resolución personalizada con recorte inferior
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --resolution 540x960 --crop-mode bottom
```

### Uso con Script Batch (Windows)

```bash
# Uso básico
tiktok_subtitles.bat video.mp4 subtitulos.srt

# Con archivo de salida específico
tiktok_subtitles.bat video.mp4 subtitulos.srt video_con_subs.mp4
```

### Opciones Avanzadas

```bash
# Personalizar estilo
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt \
  --font-size 80 \
  --font-color yellow \
  --stroke-color black \
  --stroke-width 4 \
  --background-opacity 0.3

# Cambiar fuente
python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt \
  --font-family "Comic Sans MS" \
  --font-size 70
```

## ⚙️ Parámetros de Configuración

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `--font-size` | Tamaño de la fuente en píxeles | 60 |
| `--font-color` | Color del texto | white |
| `--stroke-color` | Color del contorno | black |
| `--stroke-width` | Grosor del contorno | 3 |
| `--font-family` | Familia de fuente | Arial-Bold |
| `--background-opacity` | Opacidad del fondo (0.0-1.0) | 0.0 |
| `--tiktok` | Convertir a formato TikTok (9:16) | False |
| `--resolution` | Resolución personalizada (ej: 720x1280) | None |
| `--crop-mode` | Modo de recorte (center/top/bottom) | center |

## 🎨 Ejemplos de Estilos

### Estilo TikTok Ready
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt --tiktok
```
- Formato 9:16 (1080x1920)
- Fuente optimizada automáticamente
- Recorte inteligente centrado
- Listo para TikTok/Instagram Reels

### Estilo Gaming para TikTok
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt \
  --tiktok \
  --font-color "#00FF00" \
  --stroke-width 5 \
  --crop-mode top
```
- Formato TikTok vertical
- Texto verde brillante gaming
- Contorno negro más grueso
- Recorte desde arriba (para gaming)

### Estilo YouTube Shorts
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt \
  --resolution 1080x1920 \
  --font-size 90 \
  --background-opacity 0.3
```
- Resolución Full HD vertical
- Fuente extra grande para móviles
- Fondo semi-transparente para legibilidad

## 🔧 Integración con el Sistema de Transcripción

Este componente está diseñado para trabajar perfectamente con los archivos .srt generados por cualquiera de los scripts de transcripción del proyecto:

```bash
# 1. Transcribir audio/video
python transcribe_vad_advanced.py mi_video.mp4

# 2. Generar video TikTok con subtítulos
python tiktok_subtitle_overlay.py mi_video.mp4 output/mi_video.srt --tiktok

# 3. O usar el script batch especializado
tiktok_ready.bat mi_video.mp4 output/mi_video.srt
```

## 🎯 Modos de Recorte para Videos Horizontales

Cuando conviertes videos horizontales (16:9) a formato vertical (9:16), puedes elegir qué parte mantener:

### Center (Por defecto)
- Mantiene el centro del video
- Ideal para gaming donde la acción está centrada
- Recorta partes iguales de arriba y abajo

### Top
- Mantiene la parte superior
- Útil para gameplays donde la info importante está arriba
- Recorta solo la parte inferior

### Bottom  
- Mantiene la parte inferior
- Útil cuando el contenido importante está abajo
- Recorta solo la parte superior

```bash
# Ejemplos de modos de recorte
python tiktok_subtitle_overlay.py video.mp4 subs.srt --tiktok --crop-mode center
python tiktok_subtitle_overlay.py video.mp4 subs.srt --tiktok --crop-mode top
python tiktok_subtitle_overlay.py video.mp4 subs.srt --tiktok --crop-mode bottom
```

## 📁 Estructura de Archivos

```
GameClipping/
├── tiktok_subtitle_overlay.py    # Script principal
├── tiktok_subtitles.bat          # Script batch para Windows
├── tiktok_ready.bat              # 🆕 Script especializado para TikTok
├── requirements.txt              # Dependencias actualizadas
└── output/                       # Directorio de subtítulos .srt
    ├── video1.srt
    ├── video2.srt
    └── ...
```

## ⚠️ Requisitos del Sistema

- **Python 3.7+**
- **FFmpeg**: Requerido por MoviePy para procesamiento de video
- **Memoria**: Videos largos pueden requerir bastante RAM
- **Espacio**: El video de salida tendrá tamaño similar al original

### Instalación de FFmpeg

**Windows:**
1. Descargar FFmpeg desde https://ffmpeg.org/download.html
2. Extraer y añadir al PATH del sistema
3. O usar: `pip install ffmpeg-python`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## 🐛 Solución de Problemas

### Error: "moviepy no está instalado"
```bash
pip install moviepy
```

### Error: "FFmpeg no está disponible"
- Instalar FFmpeg siguiendo las instrucciones anteriores
- Verificar que FFmpeg esté en el PATH: `ffmpeg -version`

### Error: "Archivo SRT no encontrado"
- Verificar la ruta al archivo .srt
- Asegurarse de que el archivo existe y tiene la extensión correcta

### Video sin subtítulos
- Verificar que el archivo .srt tiene el formato correcto
- Comprobar que los timestamps coinciden con la duración del video
- Revisar la consola para mensajes de advertencia

### Rendimiento lento
- Videos muy largos pueden tardar varios minutos
- Considerar reducir la resolución del video de entrada
- Cerrar otras aplicaciones que consuman memoria

## 🎯 Flujo de Trabajo Completo

```bash
# 1. Transcribir un video de gaming
python transcribe_vad_advanced.py gameplay.mp4 --prompt "gaming, videojuego, acción"

# 2. Generar video TikTok Ready con subtítulos
tiktok_ready.bat gameplay.mp4 output/gameplay.srt

# 3. O personalizar completamente
python tiktok_subtitle_overlay.py gameplay.mp4 output/gameplay.srt \
  --tiktok --font-color "#00FF00" --crop-mode top --background-opacity 0.2

# 4. El resultado estará en gameplay_tiktok.mp4 (formato 9:16)
```

## 📊 Formatos Soportados

**Videos de entrada:**
- MP4, AVI, MOV, MKV, WMV
- Cualquier formato soportado por FFmpeg

**Subtítulos:**
- Archivos .srt en formato estándar
- Codificación UTF-8

**Videos de salida:**
- MP4 con codec H.264
- Audio AAC
- Resolución personalizable (TikTok: 1080x1920)
- Ratio de aspecto optimizado para vertical (9:16)
- Misma duración que el original

## 🎬 Consejos para Mejores Resultados

1. **Usa prompts específicos** al transcribir para mayor precisión
2. **Revisa los subtítulos** antes de generar el video final
3. **Para TikTok**: Usa `--tiktok` para formato automático optimizado
4. **Modo de recorte**: Elige `top` para gaming, `center` para contenido general
5. **Fuente automática**: El formato TikTok ajusta el tamaño automáticamente
6. **Usa fondos semi-transparentes** para videos con mucho movimiento
7. **Experimenta con colores** que contrasten bien con tu contenido
8. **Resoluciones recomendadas**:
   - TikTok: 1080x1920 (automático con `--tiktok`)
   - Instagram Reels: 1080x1920
   - YouTube Shorts: 1080x1920
   - TikTok básico: 720x1280

### 🎯 Configuraciones Recomendadas por Plataforma

```bash
# TikTok Premium
python tiktok_subtitle_overlay.py video.mp4 subs.srt --tiktok --font-size 80

# Instagram Reels
python tiktok_subtitle_overlay.py video.mp4 subs.srt --resolution 1080x1920 --background-opacity 0.3

# YouTube Shorts
python tiktok_subtitle_overlay.py video.mp4 subs.srt --resolution 1080x1920 --font-size 85
```

---

¡Disfruta creando videos con subtítulos al estilo TikTok! 🎉