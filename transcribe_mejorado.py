#!/usr/bin/env python3
"""
🎯 TRANSCRIPTOR ULTRA-MEJORADO
=============================
Implementa mejoras específicas para los problemas identificados:
1. Palabras correctas (diccionario personalizado)
2. Tiempos muertos (VAD agresivo) 
3. Sincronización temporal (corrección de drift)
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def create_gaming_prompt():
    """Prompt especializado con vocabulario gaming argentino"""
    gaming_terms = [
        # Nombres comunes personalizados
        "Gabriel", "Adriel", "Estani", "wilo", "corcho", "ruben", "erizo", "rafa", "rafael", "mate",
        "Sebastián", "Alejandro", "Cristian", "Damián", "Ale", "Morán", "Diego", "Matías",
        # Gaming terms
        "respawn", "clutch", "headshot", "camping", "rushing", "lag", "fps", 
        "streaming", "gameplay", "speedrun", "boss", "level up",
        # Argentino gaming
        "che boludo", "qué crack", "tremendo", "genial", "zarpado", "mortal",
        "dale vamos", "buena esa", "gg wp", "ez game", "down", "autista", "gordo", 
        "boludo", "vieja", "tu vieja", "allá", "pedilo"
    ]
    return ", ".join(gaming_terms)

def configure_aggressive_vad():
    """VAD más agresivo para capturar más audio"""
    return {
        "threshold": 0.35,           # Más sensible (default: 0.5)
        "min_speech_duration_ms": 150,  # Speech más corto
        "min_silence_duration_ms": 400, # Pausas más cortas  
        "speech_pad_ms": 250        # Más padding
    }

def apply_spelling_corrections(text):
    """Corrige palabras comunes mal transcritas"""
    corrections = {
        # Nombres comunes
        "abriel": "Gabriel",
        "adriel": "Adriel",
        "abri": "Gabi", 
        "ebastián": "Sebastián",
        "sebas": "Sebas",
        "ristian": "Cristian",
        "amián": "Damián",
        "estani": "Estani",
        "wilo": "Wilo",
        "corcho": "Corcho",
        "ruben": "Rubén",
        "erizo": "Erizo",
        "rafa": "Rafa",
        "rafael": "Rafael",
        "mate": "Mate",
        "morán": "Morán",
        
        # Gaming terms
        "geegee": "GG",
        "clutsh": "clutch",
        "headshoot": "headshot",
        "respón": "respawn",
        "lagh": "lag",
        
        # Argentino
        "che": "che",
        "boludo": "boludo",
        "crack": "crack",
        "pedilo": "pedilo",
        "allá": "allá"
    }
    
    corrected = text
    for wrong, correct in corrections.items():
        # Reemplazar tanto en minúsculas como con primera letra mayúscula
        corrected = corrected.replace(wrong, correct)
        corrected = corrected.replace(wrong.capitalize(), correct.capitalize())
    
    return corrected

def get_video_duration(video_path):
    """Obtiene duración precisa del video"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-select_streams", "v:0", video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['streams'][0]['duration'])
    except Exception as e:
        print(f"⚠️ No se pudo obtener duración del video: {e}")
        return None

def apply_temporal_correction(segments, video_duration):
    """Corrige drift temporal acumulativo"""
    if not segments or not video_duration:
        return segments
    
    # Calcular factor de corrección
    last_segment_end = segments[-1]['end'] 
    drift_factor = video_duration / last_segment_end
    
    if abs(drift_factor - 1.0) > 0.02:  # Solo corregir si hay drift significativo
        print(f"🔧 Aplicando corrección temporal: factor {drift_factor:.4f}")
        
        corrected_segments = []
        for seg in segments:
            # Aplicar corrección progresiva
            progress = seg['start'] / last_segment_end
            correction_factor = 1.0 + (drift_factor - 1.0) * progress
            
            corrected_segments.append({
                'start': seg['start'] * correction_factor,
                'end': seg['end'] * correction_factor,
                'text': seg['text']
            })
        return corrected_segments
    
    return segments

def enhance_audio_preprocessing(video_path):
    """Pre-procesamiento mejorado de audio"""
    temp_audio = video_path.replace('.mp4', '_enhanced.wav')
    
    print("🎵 Mejorando calidad de audio...")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-af", 
        "highpass=f=85,"           # Filtro pasa-altos
        "lowpass=f=8000,"          # Filtro pasa-bajos
        "compand=0.01:1,"          # Compresión dinámica
        "volume=1.8,"              # Amplificación
        "speechnorm=e=12.5",       # Normalización de voz
        "-ar", "16000", "-ac", "1", # Sample rate y mono
        temp_audio
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return temp_audio
    except subprocess.CalledProcessError:
        print("⚠️ Error en pre-procesamiento, usando audio original")
        return video_path

def transcribe_with_improvements(video_path, output_path):
    """Transcripción con todas las mejoras aplicadas"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Error: faster-whisper no está instalado")
        return False
    
    # 1. Pre-procesamiento de audio
    enhanced_audio = enhance_audio_preprocessing(video_path)
    
    # 2. Obtener duración del video
    video_duration = get_video_duration(video_path)
    
    # 3. Configurar modelo
    print("🧠 Cargando modelo con configuración optimizada...")
    try:
        model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        device_info = "GPU (CUDA)"
    except Exception:
        model = WhisperModel("large-v3", device="cpu", compute_type="int8")  
        device_info = "CPU"
    
    print(f"💻 Dispositivo: {device_info}")
    
    # 4. Transcripción mejorada
    print("🎤 Transcribiendo con mejoras aplicadas...")
    
    segments, info = model.transcribe(
        enhanced_audio,
        # Mejoras para palabras correctas
        initial_prompt=create_gaming_prompt(),
        condition_on_previous_text=True,
        temperature=0.0,
        
        # Mejoras para tiempos muertos
        vad_filter=True,
        vad_parameters=configure_aggressive_vad(),
        no_speech_threshold=0.4,
        log_prob_threshold=-0.8,
        
        # Mejoras para sincronización
        word_timestamps=True,
        beam_size=5,
        language="es"
    )
    
    print(f"🗣️ Idioma: {info.language} (confianza: {info.language_probability:.2f})")
    
    # 5. Procesar segmentos
    processed_segments = []
    for segment in segments:
        # Aplicar correcciones ortográficas
        corrected_text = apply_spelling_corrections(segment.text.strip())
        
        if corrected_text:  # Solo agregar si hay texto
            processed_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': corrected_text
            })
    
    # 6. Corrección temporal
    if video_duration:
        processed_segments = apply_temporal_correction(processed_segments, video_duration)
    
    # 7. Agrupar por palabras inteligentemente
    final_segments = group_segments_intelligently(processed_segments)
    
    # 8. Guardar resultado
    save_srt_improved(final_segments, output_path)
    
    # Limpiar archivo temporal
    if enhanced_audio != video_path and os.path.exists(enhanced_audio):
        os.remove(enhanced_audio)
    
    return True

def group_segments_intelligently(segments):
    """Agrupa segmentos de manera inteligente para mejor lectura"""
    if not segments:
        return segments
    
    grouped = []
    current_group = []
    current_start = None
    
    for seg in segments:
        words = seg['text'].split()
        
        # Inicializar grupo
        if not current_group:
            current_start = seg['start']
            current_group = words
            continue
        
        # Criterios para nueva línea
        duration = seg['end'] - current_start
        should_break = (
            len(current_group) + len(words) > 7 or  # Máximo 7 palabras
            duration > 3.0 or                       # Máximo 3 segundos
            seg['text'].strip().endswith(('.', '!', '?', ':'))  # Puntuación final
        )
        
        if should_break:
            # Guardar grupo actual
            if current_group:
                grouped.append({
                    'start': current_start,
                    'end': segments[len(grouped)]['end'] if len(grouped) < len(segments) else seg['start'],
                    'text': ' '.join(current_group)
                })
            # Iniciar nuevo grupo
            current_start = seg['start']
            current_group = words
        else:
            # Continuar agrupando
            current_group.extend(words)
    
    # Agregar último grupo
    if current_group:
        grouped.append({
            'start': current_start,
            'end': segments[-1]['end'],
            'text': ' '.join(current_group)
        })
    
    return grouped

def save_srt_improved(segments, output_path):
    """Guarda SRT con formato mejorado"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start_time = format_time_srt(seg['start'])
            end_time = format_time_srt(seg['end'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{seg['text']}\n\n")

def format_time_srt(seconds):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python transcribe_mejorado.py <video_file>")
        return
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Error: No se encontró el archivo {video_path}")
        return
    
    # Generar nombre de salida
    base_path = Path(video_path)
    output_path = base_path.with_suffix('.srt')
    
    print("🎯 TRANSCRIPCIÓN ULTRA-MEJORADA")
    print("=" * 50)
    print(f"📹 Video: {Path(video_path).name}")
    print(f"📝 Salida: {output_path.name}")
    print()
    print("🚀 Mejoras aplicadas:")
    print("    ✅ Diccionario gaming argentino")
    print("    ✅ VAD agresivo para tiempos muertos")
    print("    ✅ Corrección temporal automática")
    print("    ✅ Corrección ortográfica")
    print("    ✅ Pre-procesamiento de audio")
    print()
    
    start_time = time.time()
    
    if transcribe_with_improvements(video_path, output_path):
        elapsed = time.time() - start_time
        print(f"\n✅ ¡TRANSCRIPCIÓN MEJORADA COMPLETADA!")
        print(f"⏱️ Tiempo: {elapsed:.1f}s")
        print(f"📝 Archivo: {output_path}")
        print()
        print("🎯 Mejoras implementadas:")
        print("    📝 Palabras más precisas")
        print("    🔊 Mejor detección en ruidos")
        print("    ⏱️ Sincronización corregida")
    else:
        print("\n❌ Error en la transcripción mejorada")

if __name__ == "__main__":
    main()