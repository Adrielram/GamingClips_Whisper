# 📖 COMANDOS DISPONIBLES - GameClipping

## 🎯 INTERFACES DE USUARIO (NUEVO)

### **🖥️ Interfaz Visual (GUI)**
```bash
# Abrir interfaz gráfica (RECOMENDADO)
INTERFAZ_VISUAL.bat

# O directamente
python transcription_gui.py
```

### **💻 Interfaz de Consola (CLI)**
```bash
# Abrir interfaz de consola (alternativa)
INTERFAZ_CONSOLA.bat

# O directamente  
python transcription_cli.py
```

### **🔧 Launcher Unificado con Logging**
```bash
# Menú completo con gestión de logs (NUEVO)
LAUNCHER_CON_LOGS.bat
```

**✨ Características de las interfaces:**
- ✅ Selección visual/interactiva de métodos
- ✅ Explorador de archivos integrado
- ✅ Progreso en tiempo real
- ✅ Control de procesos (iniciar/detener)
- ✅ Log detallado de resultados
- ✅ **NUEVO**: Sistema de logging avanzado para debugging
- ✅ Lista automática de archivos generados

## 📋 SISTEMA DE LOGGING AVANZADO (NUEVO)

### **🔍 Para Debugging Detallado**
```bash
# Script con logging completo
python transcribe_with_logging.py video.mp4

# Con nivel debug máximo
python transcribe_with_logging.py video.mp4 --log-level DEBUG

# Solo métodos específicos
python transcribe_with_logging.py video.mp4 --methods precise enhanced
```

### **📁 Archivos de Log Generados**
- `logs/transcription_*.log` - Log completo con timestamps
- `logs/errors_*.log` - Solo errores para debugging
- `logs/session_summary_*.json` - Resumen estructurado

### **🧪 Probar Sistema de Logging**
```bash
python test_logging.py
```

**💡 El sistema de logging permite identificar exactamente dónde y por qué fallan los métodos**

---

## 🎯 COMANDOS PRINCIPALES (Métodos Recomendados)

### **🚀 Transcripción Principal**
```bash
# MÉTODO PRINCIPAL - Arrastra y suelta tu video
transcribe_FINAL.bat

# MÉTODO ULTRA-MEJORADO - Para casos problemáticos
transcribe_MEJORADO.bat

# 🆕 NUEVO: TODOS LOS MÉTODOS - Genera con todos los enfoques para comparar
transcribe_ALL_METHODS.bat
```

### **🎬 Generación de Videos TikTok**
```bash
# Crear video TikTok con subtítulos (RECOMENDADO)
python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt

# Con opciones avanzadas
python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt --tiktok --font-color white --outline-width 4

# Conversión directa a formato TikTok
python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt --tiktok --crop-mode center
```

---

## 🎯 COMANDO MULTI-MÉTODO (NUEVO)

### **🔄 Generar con TODOS los Métodos**
```bash
# Ejecutar TODOS los métodos disponibles
python transcribe_all_methods.py video.mp4

# O usando el batch (arrastra video)
transcribe_ALL_METHODS.bat
```

**¿Qué hace?**
- Ejecuta automáticamente los 6 métodos de transcripción
- Crea carpeta `{video_name}_transcriptions/` con todos los resultados
- Genera reporte de comparación detallado
- Te permite elegir el mejor método para tu caso específico

**Archivos generados:**
- `video_precise.srt` - Método principal ultra-preciso
- `video_chunked.srt` - Ultra-gradual (máximo 3 palabras)
- `video_enhanced.srt` - Audio mejorado (pre-procesamiento)
- `video_multipass.srt` - Multi-pasadas (5 pasadas adaptativas)
- `video_vad_advanced.srt` - VAD avanzado (detección contextual)
- `video_mejorado.srt` - Gaming optimizado (diccionario argentino)
- `comparison_report.txt` - Reporte detallado de comparación

**⚠️ Importante:** Este proceso puede tomar 30-45 minutos ya que ejecuta scripts especializados.

---

## 🔧 COMANDOS ESPECIALIZADOS

### **📝 Transcripción con Técnicas Específicas**

#### **🎯 Ultra-Precisión**
```bash
# Transcripción con máxima precisión
python transcribe_precise.py video.mp4

# O usando el batch
transcribe_FINAL.bat  # (arrastra video)
```

#### **🧩 Chunking Ultra-Gradual**
```bash
# Subtítulos de máximo 3 palabras
python transcribe_chunked.py video.mp4
# O usando batch:
transcribe_CHUNKED.bat  # (arrastra video)
```

#### **🎵 Audio Mejorado**
```bash
# Pre-procesamiento avanzado de audio
python transcribe_enhanced.py video.mp4
# O usando batch:
transcribe_ENHANCED.bat  # (arrastra video)
```

#### **🎯 Múltiples Pasadas**
```bash
# 5 pasadas adaptativas con merge inteligente
python transcribe_multipass.py video.mp4
# O usando batch:
transcribe_MULTIPASS.bat  # (arrastra video)
```

#### **🎮 Optimizado para Gaming**
```bash
# Diccionario gaming argentino + VAD agresivo
python transcribe_mejorado.py video.mp4
# O usando batch:
transcribe_MEJORADO.bat  # (arrastra video)
```

### **🛠️ Control Manual Avanzado**
```bash
# Control total con main.py
python main.py video.mp4 --model large-v3 --device cuda
python main.py video.mp4 --model medium --device cpu --beam-size 3
python main.py audio.wav --output custom_name.srt

# 🆕 NUEVO: Todos los métodos en uno (original)
python transcribe_all_methods.py video.mp4

# 🆕 NUEVO: Multi-método simplificado (RECOMENDADO)
python transcribe_all_methods_simple.py video.mp4
```

---

## 🎬 COMANDOS TIKTOK

### **🔥 Generación de Videos TikTok**
```bash
# Básico - Conversión automática
python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt --tiktok

# Personalización de colores
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --font-color yellow --outline-color black

# Diferentes modos de recorte
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --tiktok --crop-mode top     # Recorta desde arriba
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --tiktok --crop-mode center  # Recorta centrado
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --tiktok --crop-mode bottom  # Recorta desde abajo

# Resolución personalizada
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --width 1080 --height 1920

# Configuración avanzada de subtítulos
python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --font-size 48 --outline-width 6 --font-color white
```

### **⚡ Batch para TikTok**
```bash
# Usando archivo batch (arrastra video + SRT)
tiktok_ready.bat
```

---

## 🔧 HERRAMIENTAS DE ANÁLISIS

### **📊 Análisis de Calidad**
```bash
# Analizar calidad de transcripción
python tools/analizar_transcripcion.py archivo.srt

# Analizar problemas de sincronización  
python tools/analizar_sync.py archivo.srt

# Evaluar precisión (WER)
python tools/evaluate_wer.py archivo.srt archivo_referencia.srt
```

### **🛠️ Post-procesamiento**
```bash
# Ajustar sincronización
python tools/sync_adjust.py archivo.srt --offset 0.5

# Dividir subtítulos largos
python tools/split_long_subs.py archivo.srt

# Post-procesar subtítulos
python tools/postprocess_subs.py archivo.srt
```

### **🎵 Procesamiento de Audio**
```bash
# Pre-procesar audio para mejor transcripción
python tools/preprocess_audio.py video.mp4

# Transcripción ultra-precisa con herramientas
python tools/precise_transcribe.py video.mp4 --model large-v3 --max-words 4
```

---

## 🎮 COMANDOS GAMING

### **🔥 Para Contenido Gaming**
```bash
# Optimizado para streams de gaming argentino
transcribe_gaming.bat  # (arrastra video)

# Transcripción con correcciones para gaming
python transcribe_mejorado.py video.mp4
```

---

## ⚙️ CONFIGURACIÓN Y VERIFICACIÓN

### **🔍 Verificar Instalación**
```bash
# Verificar que todo esté instalado correctamente
python verify_installation.py

# Instalar componentes VAD avanzados
install_vad_system.bat
```

### **📦 Procesamiento en Lote**
```bash
# Procesar múltiples videos
batch_transcribe.bat  # (arrastra carpeta con videos)
```

---

## 💡 EJEMPLOS DE USO COMÚN

### **Flujo Básico Completo**
```bash
# 1. Transcribir video
transcribe_FINAL.bat  # (arrastra video.mp4)

# 2. Generar video TikTok
python tiktok_ffmpeg_overlay.py video.mp4 video.srt --tiktok
```

### **🆕 Flujo Multi-Método (Comparar Resultados)**
```bash
# 1. Generar con TODOS los métodos
transcribe_ALL_METHODS.bat  # (arrastra video.mp4)

# 2. Revisar reporte de comparación
# Carpeta: {video_name}_transcriptions/comparison_report.txt

# 3. Elegir el mejor método y crear TikTok
python tiktok_ffmpeg_overlay.py video.mp4 {video_name}_transcriptions/video_mejorado.srt --tiktok
```

### **Flujo Avanzado para Gaming**
```bash
# 1. Transcripción optimizada para gaming
transcribe_MEJORADO.bat  # (arrastra video.mp4)

# 2. Analizar calidad
python tools/analizar_transcripcion.py video.srt

# 3. Crear video TikTok personalizado
python tiktok_ffmpeg_overlay.py video.mp4 video.srt --tiktok --font-color yellow --crop-mode center
```

### **Flujo Ultra-Preciso**
```bash
# 1. Múltiples pasadas
transcribe_MULTIPASS.bat  # (arrastra video)

# 2. Verificar sincronización
python tools/analizar_sync.py video_multipass.srt

# 3. Ajustar si es necesario
python tools/sync_adjust.py video_multipass.srt --offset 0.2

# 4. Crear video final
python tiktok_ffmpeg_overlay.py video.mp4 video_multipass.srt --tiktok
```

---

## 🎯 PARÁMETROS IMPORTANTES

### **Modelos Whisper Disponibles**
- `tiny` - Más rápido, menor precisión
- `base` - Balance básico
- `small` - Buena precisión
- `medium` - Muy buena precisión  
- `large-v3` - **RECOMENDADO** - Máxima precisión

### **Dispositivos**
- `cuda` - **RECOMENDADO** - GPU NVIDIA
- `cpu` - Para sistemas sin GPU compatible

### **Formatos Soportados**
- **Videos**: MP4, MKV, AVI, MOV, WEBM
- **Audio**: WAV, MP3, FLAC, M4A
- **Subtítulos**: SRT (entrada y salida)

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### **Error de FFmpeg**
```bash
# Verificar FFmpeg instalado
ffmpeg -version

# Si no está instalado, reinstalar el entorno
install_vad_system.bat
```

### **Error de GPU**
```bash
# Forzar uso de CPU
python main.py video.mp4 --device cpu
```

### **Subtítulos desincronizados**
```bash
# Ajustar timing
python tools/sync_adjust.py archivo.srt --offset 0.5  # +0.5 segundos
python tools/sync_adjust.py archivo.srt --offset -0.3 # -0.3 segundos
```

### **Transcripción incompleta**
```bash
# Usar método más agresivo
transcribe_MULTIPASS.bat  # Detecta más speech
```

---

## 📋 ARCHIVOS DE CONFIGURACIÓN

- `requirements.txt` - Dependencias Python
- `verification_report.json` - Estado de instalación
- `learning_models/` - Modelos de aprendizaje adaptativo
- `contextual_vad_models/` - Modelos VAD contextuales
- `output/` - Archivos de salida generados
- `logs/` - Logs de transcripción

---

## 🎯 COMANDOS SEGÚN TU OBJETIVO

| **Objetivo** | **Comando Recomendado** |
|-------------|------------------------|
| Transcripción rápida y confiable | `transcribe_FINAL.bat` |
| Máxima precisión para gaming | `transcribe_MEJORADO.bat` |
| **🆕 Comparar TODOS los métodos** | `transcribe_ALL_METHODS.bat` |
| Subtítulos ultra-graduales | `transcribe_CHUNKED.bat` |
| Audio de baja calidad | `transcribe_ENHANCED.bat` |
| Cobertura máxima | `transcribe_MULTIPASS.bat` |
| Video TikTok | `python tiktok_ffmpeg_overlay.py video.mp4 subs.srt --tiktok` |
| Análisis de calidad | `python tools/analizar_transcripcion.py archivo.srt` |

**¡Todos los comandos están optimizados para contenido de gaming argentino!** 🎮🇦🇷