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

### **⭐ NUEVO: Método Ultra-Mejorado**
```bash
# Para máxima precisión y corrección de problemas:
transcribe_MEJORADO.bat
```

### **🎯 NUEVO: Sync-Perfect (para problemas de sincronización)**
```bash
# Si los subtítulos aparecen antes/después del audio:
transcribe_SYNC_PERFECT.bat
```

**Mejoras específicas:**
- 🔤 **Palabras correctas:** Diccionario gaming argentino (Gabriel vs abriel)
- 🔊 **Tiempos muertos:** VAD agresivo detecta más audio
- ⏱️ **Sincronización:** SYNC-PERFECT mantiene timestamps originales de Whisper

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
├── transcribe_MEJORADO.bat    # 🔥 NUEVO: Ultra-mejorado con correcciones
├── transcribe_SYNC_PERFECT.bat # 🎯 NUEVO: Sincronización perfecta
├── transcribe_CHUNKED.bat     # 🧩 NUEVO: Segmentación inteligente
├── transcribe_ENHANCED.bat    # 🎵 NUEVO: Pre-procesamiento de audio avanzado
├── transcribe_MULTIPASS.bat   # 🎯 NUEVO: Múltiples pasadas adaptativas
├── transcribe_precise.py      # Script de transcripción ultra-precisa
├── transcribe_mejorado.py     # 🆕 Script con todas las mejoras
├── transcribe_sync_perfect.py # 🆕 Script sync-perfect (timestamps originales)
├── transcribe_chunked.py      # 🆕 Script chunking inteligente
├── transcribe_enhanced.py     # 🆕 Script con pre-procesamiento de audio
├── transcribe_multipass.py    # 🆕 Script con múltiples pasadas
├── main.py                    # Script original completo
├── MEJORAS_PRECISION.md       # 📖 Guía detallada de mejoras
├── requirements.txt           # Dependencias Python
├── README.md                  # Esta documentación
├── venv/                      # Entorno virtual (FUNCIONA)
├── tools/                     # Herramientas auxiliares
│   ├── analizar_transcripcion.py  # 🔍 Analiza calidad de SRT
│   ├── analizar_sync.py           # 🎯 Analiza problemas de sincronización
│   ├── precise_transcribe.py      # Transcripción avanzada
│   └── [otras herramientas]
├── audio_clean/              # Audio procesado
├── output/                   # Archivos generados
└── examples/                 # Ejemplos y tests
```

---

## � MODOS DE TRANSCRIPCIÓN

### 📊 ¿Cuál usar?

| Modo | Uso Recomendado | Fortalezas |
|------|----------------|------------|
| **FINAL** | ⭐ Uso general diario | Rápido, confiable, funciona bien |
| **MEJORADO** | 🔥 Máxima precisión de palabras | Vocabulario gaming, correcciones ortográficas |
| **SYNC_PERFECT** | 🎯 Problemas de timing | Preserva timestamps originales de Whisper |
| **CHUNKED** | 🧩 **Subtítulos muy largos** | **Segmenta texto en fragmentos naturales** |
| **ENHANCED** | 🎵 **Audio de baja calidad** | **Pre-procesamiento avanzado de audio** |
| **MULTIPASS** | 🎯 **Máxima cobertura** | **Múltiples pasadas + Merge inteligente** |

### 🧩 **NUEVO: CHUNKED - Para subtítulos largos**

**Problema que resuelve:**
- ❌ Subtítulos que muestran muchas palabras juntas por mucho tiempo
- ❌ Texto que no aparece gradualmente sincronizado con el audio
- ❌ Fragmentos muy largos difíciles de leer

**Solución:**
- ✅ **Segmenta** subtítulos largos en fragmentos de 40-45 caracteres
- ✅ **Distribuye** palabras a lo largo del tiempo proporcionalmente  
- ✅ **Respeta** pausas naturales y puntuación
- ✅ **Mantiene** la precisión de palabras ya lograda

**Úsalo cuando:**
- Los subtítulos duran demasiado tiempo
- Aparecen muchas palabras de golpe
- Quieres lectura más natural y gradual

### 🎵 **NUEVO: ENHANCED - Para audio de baja calidad**

**Problema que resuelve:**
- ❌ Audio con mucho ruido de fondo
- ❌ Voces que se mezclan con efectos de videojuegos
- ❌ Grabaciones con mala calidad de micrófono
- ❌ Música/efectos que interfieren con la transcripción

**Solución:**
- ✅ **Pre-procesamiento** avanzado con FFmpeg
- ✅ **Reducción de ruido** adaptativa y filtros FFT
- ✅ **Mejora de frecuencias** específicas de voz humana
- ✅ **Compresión dinámica** para separar voz de efectos
- ✅ **Filtros gaming** especializados (ventiladores, teclado, etc.)
- ✅ **Normalización** inteligente de volumen

**Úsalo cuando:**
- El audio tiene mucho ruido de fondo
- Hay música o efectos muy fuertes
- El micrófono es de baja calidad
- Quieres máxima precisión en audio difícil

### 🎯 **NUEVO: MULTIPASS - Para máxima cobertura**

**Problema que resuelve:**
- ❌ Tiempos muertos que no detecta una sola pasada
- ❌ Speech que se pierde con configuración conservadora
- ❌ Susurros o habla muy baja que pasa desapercibida
- ❌ Necesidad de balance entre precisión y cobertura

**Solución:**
- ✅ **3 Pasadas adaptativas** con diferentes niveles de agresividad
- ✅ **Pasada conservadora** para speech claro (alta confianza)
- ✅ **Pasada agresiva** para cubrir tiempos muertos
- ✅ **Pasada ultra-agresiva** para detectar susurros
- ✅ **Merge inteligente** eliminando duplicados y conflictos
- ✅ **Priorización** por confianza y consistencia
- ✅ **Relleno de gaps** con segmentos de menor confianza

**Úsalo cuando:**
- Quieres la máxima cobertura posible
- Hay partes muy difíciles de detectar
- Necesitas capturar desde speech claro hasta susurros
- Quieres la transcripción más completa posible

---

## �🔧 Métodos Alternativos

### **🔥 Ultra-Mejorado (Para casos problemáticos)**
```bash
# Arrastra tu video al script mejorado:
transcribe_MEJORADO.bat

# O ejecuta manualmente:
python transcribe_mejorado.py "tu_video.mp4"
```

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

## 🎯 Mejoras de Precisión Implementadas

### **📖 Documento Detallado**
Ver `MEJORAS_PRECISION.md` para análisis completo de problemas y soluciones.

### **🔤 Problema: Palabras Incorrectas**
**Ejemplo:** "abriel" en lugar de "Gabriel"

**Soluciones implementadas:**
- ✅ Diccionario personalizado con nombres gaming argentinos
- ✅ Corrección ortográfica post-procesamiento
- ✅ Prompts especializados para gaming
- ✅ Pre-procesamiento de audio mejorado

### **🔇 Problema: Tiempos Muertos** 
**Ejemplo:** No se generan subtítulos durante ruidos o voces simultáneas

**Soluciones implementadas:**
- ✅ VAD (Voice Activity Detection) más agresivo
- ✅ Umbral de confianza reducido
- ✅ Separación de fuentes de audio
- ✅ Detección de speech más corto

### **⏱️ Problema: Desincronización Temporal**
**Ejemplo:** Subtítulos aparecen 1-2 segundos antes al final del video

**Soluciones implementadas:**
- ✅ Corrección automática de drift temporal
- ✅ Sincronización con landmarks de audio
- ✅ Timestamps de referencia con FFmpeg
- ✅ Ajuste progresivo de timestamps

### **📊 Herramienta de Análisis**
```bash
# Analizar calidad de transcripción existente:
python tools/analizar_transcripcion.py archivo.srt
```

**Detecta automáticamente:**
- 🔍 Palabras sospechosas o mal transcritas
- 🔍 Huecos temporales largos
- 🔍 Problemas de sincronización
- 🔍 Drift temporal acumulativo

---

## 📞 Soporte

**¿Problemas?** 
1. Verificar que `transcribe_FINAL.bat` existe
2. Probar arrastrar un video corto (30 segundos)
3. Revisar que FFmpeg está instalado
4. Verificar espacio en disco disponible

**¡Tu video de gaming será transcrito con precisión milimétrica!** 🎯