# 🎮 GameClipping - Transcriptor Ultra-Preciso

**Transcripción automática de videos de gaming a subtítulos con precisión palabra por palabra.**

Optimizado para español argentino y contenido de gaming. Usa modelos de IA avanzados para generar subtítulos sincronizados con timestamps precisos.

---

## 🚀 Uso Súper Fácil

### **🎯 Método Principal (Recomendado)**
```bash
# 1. Arrastra tu video MP4 al archivo:
transcribe_FINAL.bat

# 2. ¡Espera y listo! Se genera tu_video.srt automáticamente
```

**Características automáticas:**
- ✅ Modelo `large-v3` (máxima calidad)
- ✅ Timestamps palabra por palabra  
- ✅ Optimizado para gaming argentino
- ✅ Archivo `.srt` con mismo nombre del video
- ✅ Ultra-preciso y sincronizado

---

## 📁 Estructura del Proyecto

```
GameClipping/
├── transcribe_FINAL.bat       # ⭐ SCRIPT PRINCIPAL - Drag & Drop
├── transcribe_precise.py      # Script de transcripción ultra-precisa
├── main.py                    # Script original completo
├── requirements.txt           # Dependencias Python
├── README.md                  # Esta documentación
├── venv/                      # Entorno virtual (FUNCIONA)
├── tools/                     # Herramientas auxiliares
├── audio_clean/              # Audio procesado
├── output/                   # Archivos generados
└── examples/                 # Ejemplos y tests
```

---

## 🔧 Métodos Alternativos

### **Manual con Python**
```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar transcripción
python transcribe_precise.py "tu_video.mp4"
```

### **Con main.py (control total)**
```bash
python main.py --video "video.mp4" --model large-v3 --device auto
```

---

## ⚙️ Instalación (Solo Primera Vez)

### **Requisitos**
- Python 3.8+
- FFmpeg instalado
- GPU (opcional, mejora velocidad)

### **Setup Rápido**
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## 🎯 Características Técnicas

### **Configuración Optimizada**
- **Modelo:** `large-v3` (mejor disponible)
- **Beam Size:** `5` (máxima precisión)
- **Compute Type:** `float16` (velocidad óptima)
- **Word Timestamps:** Activado (sincronización perfecta)
- **VAD Filter:** Activado (mejor segmentación)
- **Language:** Español argentino
- **Gaming Prompt:** Optimizado para gaming

### **Calidad de Salida**
- ✅ Subtítulos sincronizados palabra por palabra
- ✅ Timestamps precisos al milisegundo
- ✅ Optimizado para jerga gamer argentina
- ✅ Detecta pausas y silencios automáticamente
- ✅ Formato SRT compatible con todos los players

---

## 📊 Rendimiento

- **Video 2 minutos:** ~3-5 minutos procesamiento
- **Precisión:** >95% para audio claro
- **Sincronización:** Precisión de milisegundos
- **Compatibilidad:** Todos los formatos de video comunes

---

## 🛠️ Herramientas Incluidas

### **tools/ - Utilidades**
- `evaluate_wer.py` - Calcular precisión (Word Error Rate)
- `postprocess_subs.py` - Post-procesar subtítulos
- `preprocess_audio.py` - Limpiar audio antes de transcribir

### **Ejemplos de Uso**
```bash
# Evaluar precisión de transcripción
python tools/evaluate_wer.py original.srt transcrito.srt

# Post-procesar subtítulos
python tools/postprocess_subs.py archivo.srt

# Pre-procesar audio
python tools/preprocess_audio.py video.mp4
```

---

## 🎮 Optimización Gaming

### **Prompt Especializado**
El sistema incluye prompts optimizados para contenido de gaming:
- Reconoce jerga gamer
- Entiende expresiones argentinas
- Detecta nombres de juegos y personajes
- Maneja exclamaciones y reacciones típicas

### **Ejemplos de Reconocimiento**
- "Che, mirá esto" ✅
- "Qué genial, dale vamos" ✅ 
- "GG, buena partida" ✅
- "Nooo, me mataron" ✅

---

## 🔍 Solución de Problemas

### **Error: Video no encontrado**
- Verificar que el archivo existe
- Usar rutas sin espacios o entre comillas

### **Error: Python no encontrado**
- Verificar instalación de Python
- Activar entorno virtual: `venv\Scripts\activate`

### **Error: FFmpeg no encontrado**
- Instalar FFmpeg: `https://ffmpeg.org/`
- Agregar al PATH del sistema

### **Transcripción lenta**
- Usar GPU si está disponible
- Verificar que no hay otros procesos pesados ejecutándose

---

## 📝 Formato de Salida

### **Archivo SRT Generado**
```
1
00:00:00,000 --> 00:00:02,500
Hola che, vamos a jugar un poco

2
00:00:02,500 --> 00:00:05,000
Mirá este nivel, está genial

3
00:00:05,000 --> 00:00:07,500
Dale, vamos que podemos ganar
```

### **Características del SRT**
- Timestamps precisos (milisegundos)
- Máximo 7 palabras por línea
- Máximo 3 segundos por subtítulo
- Breaks inteligentes en pausas naturales
- Codificación UTF-8 (soporta acentos)

---

## 🚀 Próximas Mejoras

- [ ] Soporte para múltiples idiomas
- [ ] Detección automática de idioma  
- [ ] Interfaz gráfica (GUI)
- [ ] Transcripción en tiempo real
- [ ] Integración con OBS Studio

---

## 📞 Soporte

**¿Problemas?** 
1. Verificar que `transcribe_FINAL.bat` existe
2. Probar arrastrar un video corto (30 segundos)
3. Revisar que FFmpeg está instalado
4. Verificar espacio en disco disponible

**¡Tu video de gaming será transcrito con precisión milimétrica!** 🎯