# Generador de Subtítulos TikTok

Este componente permite añadir subtítulos al estilo TikTok a cualquier video, utilizando archivos de subtítulos .srt generados por el sistema de transcripción.

## 🎯 Características

- **Estilo TikTok**: Subtítulos grandes, centrados, con contorno y posicionados en la parte inferior
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

## 🎨 Ejemplos de Estilos

### Estilo TikTok Clásico (Por defecto)
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt
```
- Texto blanco con contorno negro
- Fuente Arial-Bold de 60px
- Sin fondo

### Estilo Gaming
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt \
  --font-size 70 \
  --font-color "#00FF00" \
  --stroke-color black \
  --stroke-width 4
```
- Texto verde brillante
- Contorno negro más grueso
- Fuente más grande

### Estilo con Fondo Semi-transparente
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt \
  --font-color white \
  --background-opacity 0.7
```
- Fondo negro semi-transparente
- Mejor legibilidad en videos complejos

### Estilo Colorido
```bash
python tiktok_subtitle_overlay.py video.mp4 subs.srt \
  --font-size 80 \
  --font-color yellow \
  --stroke-color purple \
  --stroke-width 5
```
- Texto amarillo con contorno púrpura
- Fuente extra grande

## 🔧 Integración con el Sistema de Transcripción

Este componente está diseñado para trabajar perfectamente con los archivos .srt generados por cualquiera de los scripts de transcripción del proyecto:

```bash
# 1. Transcribir audio/video
python transcribe_vad_advanced.py mi_video.mp4

# 2. Generar video con subtítulos
python tiktok_subtitle_overlay.py mi_video.mp4 output/mi_video.srt
```

## 📁 Estructura de Archivos

```
GameClipping/
├── tiktok_subtitle_overlay.py    # Script principal
├── tiktok_subtitles.bat          # Script batch para Windows
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

# 2. Generar video con subtítulos TikTok
python tiktok_subtitle_overlay.py gameplay.mp4 output/gameplay.srt \
  --font-size 70 --font-color "#00FF00"

# 3. El resultado estará en gameplay_con_subtitulos.mp4
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
- Misma resolución y framerate que el original

## 🎬 Consejos para Mejores Resultados

1. **Usa prompts específicos** al transcribir para mayor precisión
2. **Revisa los subtítulos** antes de generar el video final
3. **Ajusta el tamaño de fuente** según la resolución del video
4. **Usa fondos semi-transparentes** para videos con mucho movimiento
5. **Experimenta con colores** que contrasten bien con tu contenido

---

¡Disfruta creando videos con subtítulos al estilo TikTok! 🎉