# GameClipping - Transcriptor de Videos de Gaming

Este proyecto permite transcribir automáticamente videos de gameplay en español argentino a subtítulos utilizando modelos de reconocimiento de voz avanzados (Whisper).

## 🎯 Objetivo del Proyecto

**Entrada:** Video .mp4 (aproximadamente 2 minutos) de un clip de gameplay en español argentino  
**Salida:** Archivos de subtítulos en formato .srt, .txt o .json

## 📁 Estructura del Proyecto

```
GameClipping/
├── main.py                    # Script principal de transcripción
├── transcribe.py              # Script simplificado preconfigurado
├── transcribe.bat             # Script de Windows (.bat)
├── transcribe.ps1             # Script de PowerShell
├── requirements.txt           # Dependencias de Python
├── README.md                  # Este archivo
├── .gitignore                # Archivos a ignorar en Git
├── audio_clean/              # Audio procesado y herramientas de limpieza
│   ├── clean.md              # Comandos de limpieza de audio
│   └── cleaned_audio.wav     # Audio limpio procesado
├── docs/                     # Documentación adicional
│   └── venv310_pip_list.txt  # Lista de paquetes instalados
├── examples/                 # Archivos de ejemplo
│   └── ayud.txt              # Texto de ejemplo
├── logs/                     # Logs de transcripción
│   ├── transcribe_argprompt_fixed.log
│   ├── transcribe_argprompt_fixed2.log
│   ├── transcribe_argprompt.log
│   └── transcribe_whisperx.log
├── output/                   # Archivos de salida generados
│   ├── *.srt                 # Subtítulos generados
│   ├── out_longprompt_vad.srt
│   ├── out_longprompt.srt
│   ├── out_shortprompt.srt
│   └── subs_reales.srt       # Subtítulos de referencia
├── tools/                    # Herramientas auxiliares
│   ├── check_whisperx.py     # Verificar instalación de WhisperX
│   ├── evaluate_wer.py       # Calcular Word Error Rate (WER)
│   ├── postprocess_subs.py   # Post-procesamiento de subtítulos
│   └── preprocess_audio.py   # Pre-procesamiento de audio
└── venv310/                  # Entorno virtual de Python
```

## ⚡ Uso Rápido (Recomendado)

### Scripts Preconfigurados

Para uso rápido y simple, usa uno de estos scripts que ya tienen la configuración optimizada:

#### Opción 1: Script Python (Multiplataforma)
```bash
python transcribe.py video.mp4
```

#### Opción 2: Script de Windows (.bat)
```cmd
transcribe.bat video.mp4
```

#### Opción 3: Script PowerShell (Windows)
```powershell
.\transcribe.ps1 video.mp4
```

**Configuración automática:**
- ✅ Modelo: `large-v3` (máxima calidad)
- ✅ Beam size: `5` (mejor precisión)  
- ✅ Compute type: `float16` (velocidad óptima)
- ✅ Prompt argentino activado
- ✅ Salida: `<nombre_video>.srt` automáticamente
- ✅ GPU activada (con fallback a CPU)

**Ejemplos:**
```bash
# Transcribir clip de gaming
python transcribe.py gameplay_clip.mp4
# → Genera: gameplay_clip.srt

# Transcribir desde otra carpeta  
python transcribe.py "C:\Videos\mi_clip.mkv"
# → Genera: C:\Videos\mi_clip.srt
```

## 🚀 Instalación

### Requisitos Previos

1. **Python 3.8+** instalado
2. **FFmpeg** instalado y en el PATH del sistema
3. **CUDA** (opcional, para aceleración GPU)

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone <repository-url>
cd GameClipping

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Para soporte GPU (opcional)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Verificar Instalación

```bash
# Verificar FFmpeg
ffmpeg -version

# Verificar WhisperX (opcional)
python tools/check_whisperx.py
```

## 📖 Uso del Programa Principal

### Comando Básico

```bash
python main.py <archivo_entrada> [opciones]
```

### Argumentos del Comando Principal

#### Argumentos Obligatorios

- `input`: Ruta al archivo de audio o video a transcribir
  - Formatos soportados: `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.mp3`, `.wav`, `.m4a`, `.flac`, `.aac`, `.ogg`

#### Argumentos Opcionales

##### Configuración del Modelo

- `--model-size <size>`: Tamaño del modelo Whisper a utilizar
  - **Opciones:** `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`
  - **Por defecto:** `large-v3`
  - **Ejemplo:** `--model-size medium`

- `--device <device>`: Dispositivo para ejecutar el modelo
  - **Opciones:** `cuda`, `cpu`
  - **Por defecto:** `cuda`
  - **Ejemplo:** `--device cpu`

- `--compute-type <type>`: Tipo de cómputo para el modelo
  - **Opciones:** `float16`, `int8_float16`, `int8`
  - **Por defecto:** `float16`
  - **Ejemplo:** `--compute-type int8`

##### Configuración de Transcripción

- `--beam-size <number>`: Tamaño del beam para la transcripción
  - **Tipo:** Entero
  - **Por defecto:** `5`
  - **Ejemplo:** `--beam-size 3`

- `--output <archivo>`: Ruta del archivo de salida
  - **Formatos:** `.srt`, `.txt`, `.json`
  - **Ejemplo:** `--output subtitulos.srt`

##### Características Específicas para Argentino

- `--use-argentine-prompt`: Usar prompt corto optimizado para español argentino y gaming
  - **Descripción:** Incluye palabras clave como "che", "boludo", "pibe", "gg", "clutch"
  - **Recomendado:** Para la mayoría de casos de uso

- `--use-argentine-prompt-long`: Usar prompt largo conversacional argentino
  - **Advertencia:** Puede causar inserción literal del prompt en la transcripción
  - **Uso:** Solo para casos específicos donde se necesite mayor contexto

##### Características Avanzadas

- `--vad-split`: Pre-dividir audio usando detección de silencio
  - **Descripción:** Divide el audio en segmentos usando ffmpeg silencedetect
  - **Útil:** Para capturar momentos que podrían perderse en transcripción continua

- `--no-whisperx`: Desactivar alineación forzada con WhisperX
  - **Descripción:** Evita usar WhisperX incluso si está instalado
  - **Uso:** Para depuración o si WhisperX causa problemas

### Ejemplos de Uso

#### Transcripción Básica

```bash
# Transcripción simple de un video
python main.py video_gameplay.mp4

# Con archivo de salida específico
python main.py video_gameplay.mp4 --output subtitulos.srt
```

#### Transcripción Optimizada para Gaming Argentino

```bash
# Con prompt argentino (recomendado)
python main.py clip_gaming.mp4 --use-argentine-prompt --output gaming_subs.srt

# Con división por VAD para mejor captura
python main.py clip_gaming.mp4 --use-argentine-prompt --vad-split --output gaming_vad.srt
```

#### Configuración de Rendimiento

```bash
# Modelo más rápido para pruebas
python main.py video.mp4 --model-size medium --beam-size 3

# CPU en lugar de GPU
python main.py video.mp4 --device cpu --compute-type int8

# Máxima calidad (GPU requerida)
python main.py video.mp4 --model-size large-v3 --beam-size 5 --use-argentine-prompt
```

#### Diferentes Formatos de Salida

```bash
# Formato SRT (subtítulos)
python main.py video.mp4 --output subtitulos.srt

# Formato texto plano
python main.py video.mp4 --output transcripcion.txt

# Formato JSON con metadatos
python main.py video.mp4 --output datos.json
```

## 🛠️ Herramientas Auxiliares

### 1. Verificación de WhisperX (`check_whisperx.py`)

Verifica si WhisperX está correctamente instalado y funcionando.

```bash
python tools/check_whisperx.py
```

**Funcionalidad:**
- Verifica importación de WhisperX
- Prueba carga de modelos en CUDA y CPU
- Reporta errores de configuración

### 2. Evaluación de WER (`evaluate_wer.py`)

Calcula la tasa de error de palabras (Word Error Rate) entre dos archivos de subtítulos.

```bash
python tools/evaluate_wer.py <referencia.srt> <hipotesis.srt>
```

**Argumentos:**
- `referencia.srt`: Archivo de subtítulos de referencia (ground truth)
- `hipotesis.srt`: Archivo de subtítulos a evaluar

**Ejemplo:**
```bash
python tools/evaluate_wer.py output/subs_reales.srt output/transcripcion_test.srt
```

**Salida:**
```
Reference words: 245
Hypothesis words: 251
Errors: 23
WER: 0.094
```

### 3. Post-procesamiento de Subtítulos (`postprocess_subs.py`)

Limpia y mejora subtítulos generados automáticamente.

```bash
python tools/postprocess_subs.py <entrada.srt> <salida.srt> [opciones]
```

**Argumentos:**
- `entrada.srt`: Archivo de subtítulos a procesar
- `salida.srt`: Archivo de subtítulos limpio

**Opciones:**
- `--replacements <archivo.json>`: Archivo JSON con reemplazos personalizados
- `--use-symspell`: Usar corrección ortográfica con SymSpell

**Funcionalidades:**
- Normalización de mayúsculas/minúsculas
- Corrección de errores comunes de ASR
- Reemplazos personalizables para jerga argentina
- Corrección ortográfica opcional

**Ejemplo:**
```bash
python tools/postprocess_subs.py output/raw_subs.srt output/clean_subs.srt --use-symspell
```

**Reemplazos por defecto:**
```json
{
  "аний": "adriel",
  "adne": "adriel", 
  "borudo": "boludo",
  "me metieron en el orto": "metetelo en el orto"
}
```

### 4. Pre-procesamiento de Audio (`preprocess_audio.py`)

Prepara archivos de audio para mejorar la calidad de transcripción.

```bash
python tools/preprocess_audio.py <entrada> <salida.wav> [opciones]
```

**Argumentos:**
- `entrada`: Archivo de audio/video de entrada
- `salida.wav`: Archivo WAV procesado de salida

**Opciones:**
- `--rate <hz>`: Frecuencia de muestreo (por defecto: 16000)
- `--highpass <hz>`: Filtro pasa-altos (por defecto: desactivado)
- `--lowpass <hz>`: Filtro pasa-bajos (por defecto: desactivado)  
- `--normalize`: Normalizar volumen

**Ejemplo:**
```bash
# Procesamiento básico
python tools/preprocess_audio.py video.mp4 clean_audio.wav --normalize

# Con filtros de frecuencia
python tools/preprocess_audio.py video.mp4 filtered_audio.wav --highpass 200 --lowpass 3000 --normalize
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Configurar cache de modelos
export HF_HOME=/path/to/cache

# Configurar CUDA
export CUDA_VISIBLE_DEVICES=0
```

### Optimización de Memoria

Para videos largos o sistemas con poca memoria:

```bash
# Usar modelo más pequeño
python main.py video.mp4 --model-size medium

# Usar tipo de cómputo int8
python main.py video.mp4 --compute-type int8

# Procesar en CPU
python main.py video.mp4 --device cpu
```

### Limpieza de Audio Manual

Para audio con mucho ruido, usar FFmpeg directamente:

```bash
# Filtro básico (como en audio_clean/clean.md)
ffmpeg -i input.mp4 -af "highpass=f=200, lowpass=f=3000" cleaned_audio.wav

# Filtro avanzado con reducción de ruido
ffmpeg -i input.mp4 -af "highpass=f=200, lowpass=f=3000, afftdn" cleaned_audio.wav
```

## 📊 Evaluación de Calidad

### Métricas de Evaluación

- **WER (Word Error Rate)**: Porcentaje de palabras incorrectas
- **Tiempo de procesamiento**: Velocidad de transcripción
- **Calidad perceptual**: Evaluación manual de naturalidad

### Benchmark de Modelos

| Modelo | WER Típico | Velocidad | Memoria GPU |
|--------|------------|-----------|-------------|
| tiny | ~15-20% | 5x | 1GB |
| base | ~12-15% | 3x | 1GB |
| small | ~10-12% | 2x | 2GB |
| medium | ~8-10% | 1.5x | 3GB |
| large-v3 | ~6-8% | 1x | 6GB |

## 🐛 Solución de Problemas

### Errores Comunes

#### Error de CUDA/GPU
```
RuntimeError: CUDA not available
```
**Solución:** Usar `--device cpu` o instalar CUDA toolkit

#### Error de FFmpeg
```
ffmpeg not found on PATH
```
**Solución:** Instalar FFmpeg y agregarlo al PATH del sistema

#### Error de Memoria
```
CUDA out of memory
```
**Solución:** Usar `--model-size medium` o `--device cpu`

#### WhisperX no encontrado
```
ImportError: No module named 'whisperx'
```
**Solución:** Instalar con `pip install whisperx` o usar `--no-whisperx`

### Depuración

```bash
# Verificar instalación
python tools/check_whisperx.py

# Modo verbose (agregar prints al código)
python main.py video.mp4 --output debug.srt 2>&1 | tee debug.log

# Probar con archivo corto
python main.py short_clip.mp4 --model-size small --output test.srt
```

## 📝 Contribución

### Estructura de Commits

- `feat:` Nueva funcionalidad
- `fix:` Corrección de errores
- `docs:` Documentación
- `refactor:` Refactorización de código
- `test:` Pruebas

### Desarrollo Local

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install black flake8 pytest

# Ejecutar tests
python -m pytest

# Formatear código
black *.py tools/*.py
```

## 📄 Licencia

[Especificar licencia del proyecto]

## 🙋‍♂️ Soporte

Para reportar problemas o solicitar funcionalidades:
1. Verificar la sección de solución de problemas
2. Crear un issue en el repositorio
3. Incluir logs de error y configuración del sistema