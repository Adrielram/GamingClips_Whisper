# 🎮 GameClipping VAD System - Guía Rápida de Comandos

> **Sistema VAD Híbrido y Contextual para Transcripción Gaming Profesional**  
> Versión: 2.0 | Fecha: Septiembre 2025

---

## 🚀 Comandos Principales

### 📦 **Instalación y Configuración**

```bash
# Instalar todas las dependencias automáticamente
install_vad_system.bat

# Verificar que todo está instalado correctamente
venv\Scripts\python.exe verify_installation.py
```

---

## 🎯 **Transcripción Rápida**

### 🎮 **Gaming Optimizada (Recomendado)**
```bash
# Transcripción rápida optimizada para gaming
transcribe_gaming.bat mi_gameplay.wav
transcribe_gaming.bat "C:\path\to\audio.mp3"
transcribe_gaming.bat *.wav
```

### 🔬 **Máxima Precisión**
```bash
# Transcripción de alta calidad (más lenta)
transcribe_precision.bat mi_audio.wav
transcribe_precision.bat importante.mp3
```

### 📁 **Procesamiento en Lotes**
```bash
# Procesar múltiples archivos automáticamente
batch_transcribe.bat *.wav
batch_transcribe.bat *.mp3
batch_transcribe.bat C:\audios\*.wav
```

---

## ⚙️ **Comandos Avanzados**

### 🧠 **Transcripción Manual con VAD Avanzado**
```bash
# Perfil Gaming (rápido)
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile gaming

# Perfil Precisión (lento pero preciso)
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile precision

# Perfil Rápido (muy rápido)
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile fast

# Con usuario específico para aprendizaje adaptativo
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile gaming --user "mi_usuario"

# Modo verbose para debugging
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile gaming --verbose
```

### 🔧 **Configuración Personalizada**
```bash
# Especificar archivo de salida personalizado
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --output mi_transcripcion.txt

# Generar también archivo SRT
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --srt

# Usar idioma específico
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --language es

# Configurar threshold VAD
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --vad-threshold 0.7
```

---

## 🛠️ **Diagnóstico y Mantenimiento**

### 🔍 **Verificación del Sistema**
```bash
# Verificación completa con pruebas funcionales
venv\Scripts\python.exe verify_installation.py

# Verificar solo las librerías principales
venv\Scripts\python.exe -c "import silero_vad; import webrtcvad; import librosa; print('✅ OK')"

# Verificar versión de Python
venv\Scripts\python.exe --version

# Ver paquetes instalados
venv\Scripts\python.exe -m pip list
```

### 🔄 **Actualización de Dependencias**
```bash
# Actualizar pip
venv\Scripts\python.exe -m pip install --upgrade pip

# Actualizar paquetes específicos
venv\Scripts\python.exe -m pip install --upgrade faster-whisper
venv\Scripts\python.exe -m pip install --upgrade silero-vad

# Reinstalar todo el sistema
install_vad_system.bat
```

---

## 📊 **Perfiles Disponibles**

| Perfil | Velocidad | Calidad | Uso Recomendado |
|--------|-----------|---------|-----------------|
| `fast` | ⚡⚡⚡ | ⭐⭐ | Pruebas rápidas |
| `gaming` | ⚡⚡ | ⭐⭐⭐ | **Gaming general** |
| `precision` | ⚡ | ⭐⭐⭐⭐⭐ | Audio importante |
| `noise-robust` | ⚡⚡ | ⭐⭐⭐⭐ | Audio con ruido |
| `micro-speech` | ⚡ | ⭐⭐⭐⭐ | Susurros/voz baja |

---

## 📁 **Estructura de Archivos de Salida**

```
output/
├── audio_gaming.txt          # Transcripción gaming rápida
├── audio_gaming.srt          # Subtítulos gaming
├── audio_precision.txt       # Transcripción de precisión
├── audio_precision.srt       # Subtítulos de precisión
└── audio_vad_advanced.txt    # Transcripción avanzada manual
```

---

## 🎮 **Ejemplos Específicos Gaming**

### 🔫 **Gameplay FPS**
```bash
# Optimizado para comunicación rápida en FPS
transcribe_gaming.bat gameplay_fps.wav
```

### 🗣️ **Streams y Comentarios**
```bash
# Para streams con múltiples hablantes
transcribe_precision.bat stream_completo.wav
```

### 🎤 **Chat de Voz**
```bash
# Para chat de Discord/TeamSpeak
venv\Scripts\python.exe transcribe_vad_advanced.py chat.wav --profile gaming --user "streamer"
```

### 📹 **Videos de YouTube**
```bash
# Extraer audio de video y transcribir
transcribe_precision.bat "video_gaming.mp4"
```

---

## ⚠️ **Solución de Problemas Comunes**

### 🔴 **Error: "No module named..."**
```bash
# Reinstalar dependencias
install_vad_system.bat
```

### 🔴 **Error: "Entorno virtual no encontrado"**
```bash
# Verificar que existe el directorio venv
dir venv\Scripts\

# Si no existe, crear entorno virtual
python -m venv venv
install_vad_system.bat
```

### 🔴 **Audio no compatible**
```bash
# Convertir audio a WAV primero (usando FFmpeg)
ffmpeg -i audio.mp3 audio.wav
transcribe_gaming.bat audio.wav
```

### 🔴 **Memoria insuficiente**
```bash
# Usar perfil rápido para ahorrar memoria
venv\Scripts\python.exe transcribe_vad_advanced.py audio.wav --profile fast
```

---

## 🚀 **Flujo de Trabajo Recomendado**

### 1️⃣ **Setup Inicial (una vez)**
```bash
install_vad_system.bat
venv\Scripts\python.exe verify_installation.py
```

### 2️⃣ **Uso Diario Gaming**
```bash
# Para clips cortos de gaming
transcribe_gaming.bat clip.wav

# Para sesiones largas importantes
transcribe_precision.bat sesion_completa.wav
```

### 3️⃣ **Procesamiento Masivo**
```bash
# Procesar toda una carpeta
batch_transcribe.bat C:\gaming_clips\*.wav
```

---

## 📚 **Recursos Adicionales**

- 📖 **Documentación Completa**: `README_VAD_ADVANCED.md`
- 🔮 **Mejoras Futuras**: `FUTURAS_MEJORAS.md`
- 🛠️ **Código Fuente**: `vad_hybrid.py`, `vad_contextual.py`, `transcribe_vad_advanced.py`
- 📊 **Reportes**: `verification_report.json`

---

## 💡 **Tips y Trucos**

### ⚡ **Optimización de Velocidad**
- Usa `--profile fast` para pruebas rápidas
- El perfil `gaming` es el mejor balance velocidad/calidad
- Para audio limpio, `gaming` es más rápido que `precision`

### 🎯 **Optimización de Calidad**
- Usa `--profile precision` para audio importante
- El perfil `noise-robust` es mejor para audio con ruido de fondo
- El perfil `micro-speech` detecta mejor susurros y voz baja

### 🧠 **Aprendizaje Adaptativo**
- Usa `--user "tu_nombre"` para entrenar el sistema con tus patrones
- El sistema mejora automáticamente con el uso continuado
- Los usuarios frecuentes obtienen mejor precisión con el tiempo

---

> **¡Sistema listo para transcripción gaming profesional!** 🎮✨  
> Para soporte adicional, consulta `README_VAD_ADVANCED.md`