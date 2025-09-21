#!/usr/bin/env python3
"""
🎯 TRANSCRIPTOR SYNC-PERFECT
===========================
Versión especializada en sincronización perfecta.
Se enfoca en mantener timestamps originales de Whisper.
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

def configure_precise_vad():
    """VAD configurado para máxima precisión temporal"""
    return {
        "threshold": 0.4,               # Balanceado (no muy agresivo)
        "min_speech_duration_ms": 200,  # Mínimo speech
        "min_silence_duration_ms": 500, # Pausas más claras
        "speech_pad_ms": 100            # Menos padding para evitar drift
    }

def apply_spelling_corrections(text):
    """Corrige palabras comunes mal transcritas"""
    corrections = {
        # Nombres comunes
        "abriel": "Gabriel", "adriel": "Adriel", "abri": "Gabi", 
        "ebastián": "Sebastián", "sebas": "Sebas", "ristian": "Cristian",
        "amián": "Damián", "estani": "Estani", "wilo": "Wilo",
        "corcho": "Corcho", "ruben": "Rubén", "erizo": "Erizo",
        "rafa": "Rafa", "rafael": "Rafael", "mate": "Mate", "morán": "Morán",
        
        # Gaming terms
        "geegee": "GG", "clutsh": "clutch", "headshoot": "headshot",
        "respón": "respawn", "lagh": "lag",
        
        # Argentino
        "che": "che", "boludo": "boludo", "crack": "crack",
        "pedilo": "pedilo", "allá": "allá"
    }
    
    corrected = text
    for wrong, correct in corrections.items():
        # Reemplazar tanto en minúsculas como con primera letra mayúscula
        corrected = corrected.replace(wrong, correct)
        corrected = corrected.replace(wrong.capitalize(), correct.capitalize())
    
    return corrected

def transcribe_with_perfect_sync(video_path, output_path):
    """Transcripción manteniendo timestamps originales de Whisper"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Error: faster-whisper no está instalado")
        return False
    
    print("🧠 Cargando modelo con configuración de sync perfecto...")
    try:
        model = WhisperModel("large-v3", device="cuda", compute_type="float16")
        device_info = "GPU (CUDA)"
    except Exception:
        model = WhisperModel("large-v3", device="cpu", compute_type="int8")  
        device_info = "CPU"
    
    print(f"💻 Dispositivo: {device_info}")
    
    # Transcripción con configuración optimizada para sincronización
    print("🎤 Transcribiendo con sync perfecto...")
    
    segments, info = model.transcribe(
        video_path,
        # Configuración para palabras correctas
        initial_prompt=create_gaming_prompt(),
        condition_on_previous_text=False,  # ⚠️ CAMBIO: False para evitar drift
        temperature=0.0,
        
        # Configuración balanceada para sync
        vad_filter=True,
        vad_parameters=configure_precise_vad(),
        no_speech_threshold=0.5,  # ⚠️ CAMBIO: Más conservador
        
        # Configuración crítica para sincronización
        word_timestamps=True,
        beam_size=3,  # ⚠️ CAMBIO: Reducido para mejor timing
        language="es"
    )
    
    print(f"🗣️ Idioma: {info.language} (confianza: {info.language_probability:.2f})")
    
    # Procesar segmentos SIN modificar timestamps originales
    processed_segments = []
    
    for segment in segments:
        # Solo aplicar correcciones de texto, NO tocar timestamps
        corrected_text = apply_spelling_corrections(segment.text.strip())
        
        if corrected_text and len(corrected_text) > 2:
            processed_segments.append({
                'start': segment.start,  # ⚠️ MANTENER timestamp original
                'end': segment.end,      # ⚠️ MANTENER timestamp original  
                'text': corrected_text
            })
    
    # Agrupar INTELIGENTEMENTE pero manteniendo timing preciso
    final_segments = group_with_perfect_timing(processed_segments)
    
    # Guardar resultado
    save_srt_perfect_sync(final_segments, output_path)
    
    return True

def group_with_perfect_timing(segments):
    """Agrupa segmentos manteniendo timing perfecto"""
    if not segments:
        return segments
    
    grouped = []
    current_words = []
    current_start = None
    current_end = None
    
    for seg in segments:
        words = seg['text'].split()
        
        # Inicializar grupo
        if not current_words:
            current_start = seg['start']
            current_end = seg['end']
            current_words = words
            continue
        
        # Criterios MUY conservadores para nueva línea
        gap_between = seg['start'] - current_end  # Tiempo entre segmentos
        total_words = len(current_words) + len(words)
        total_duration = seg['end'] - current_start
        
        should_break = (
            gap_between > 1.0 or          # Gap largo entre speech
            total_words > 8 or            # Demasiadas palabras
            total_duration > 4.0 or       # Duración muy larga
            seg['text'].strip().endswith(('.', '!', '?'))  # Puntuación final clara
        )
        
        if should_break:
            # Guardar grupo actual con timing preciso
            if current_words:
                grouped.append({
                    'start': current_start,
                    'end': current_end,
                    'text': ' '.join(current_words)
                })
            
            # Nuevo grupo
            current_start = seg['start']
            current_end = seg['end']
            current_words = words
        else:
            # Extender grupo actual
            current_words.extend(words)
            current_end = seg['end']  # Actualizar end time
    
    # Agregar último grupo
    if current_words:
        grouped.append({
            'start': current_start,
            'end': current_end,
            'text': ' '.join(current_words)
        })
    
    return grouped

def save_srt_perfect_sync(segments, output_path):
    """Guarda SRT con timestamps exactos"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start_time = format_time_precise(seg['start'])
            end_time = format_time_precise(seg['end'])
            
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{seg['text']}\n\n")

def format_time_precise(seconds):
    """Convierte segundos a formato SRT con máxima precisión"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int(round((seconds % 1) * 1000))  # Redondeo preciso
    
    # Asegurar que millisecs no exceda 999
    if millisecs >= 1000:
        millisecs = 999
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def analyze_timing_quality(segments):
    """Analiza calidad del timing"""
    if len(segments) < 2:
        return
    
    gaps = []
    durations = []
    
    for i in range(len(segments) - 1):
        gap = segments[i+1]['start'] - segments[i]['end']
        gaps.append(gap)
        durations.append(segments[i]['end'] - segments[i]['start'])
    
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    print(f"📊 Análisis de timing:")
    print(f"    📏 Duración promedio: {avg_duration:.2f}s")
    print(f"    ⏸️  Gap promedio: {avg_gap:.2f}s")
    print(f"    📝 Total segmentos: {len(segments)}")

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python transcribe_sync_perfect.py <video_file>")
        return
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Error: No se encontró el archivo {video_path}")
        return
    
    # Generar nombre de salida
    base_path = Path(video_path)
    output_path = base_path.with_suffix('.srt')
    
    print("🎯 TRANSCRIPCIÓN SYNC-PERFECT")
    print("=" * 50)
    print(f"📹 Video: {Path(video_path).name}")
    print(f"📝 Salida: {output_path.name}")
    print()
    print("🎯 Configuración SYNC-PERFECT:")
    print("    ✅ Timestamps originales de Whisper (sin modificar)")
    print("    ✅ Configuración conservadora de VAD")
    print("    ✅ Agrupación inteligente manteniendo timing")
    print("    ✅ Corrección solo de texto, NO de timing")
    print()
    
    start_time = time.time()
    
    if transcribe_with_perfect_sync(video_path, output_path):
        elapsed = time.time() - start_time
        
        # Leer y analizar resultado
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar subtítulos
        subtitle_count = content.count('\n\n')
        
        print(f"\n✅ ¡TRANSCRIPCIÓN SYNC-PERFECT COMPLETADA!")
        print(f"⏱️ Tiempo: {elapsed:.1f}s")
        print(f"📝 Archivo: {output_path}")
        print(f"📊 Subtítulos generados: {subtitle_count}")
        print()
        print("🎯 Optimizaciones aplicadas:")
        print("    🔤 Palabras corregidas (diccionario personalizado)")
        print("    ⏱️ Timestamps originales preservados")
        print("    🎭 Agrupación inteligente sin drift")
        
    else:
        print("\n❌ Error en la transcripción sync-perfect")

if __name__ == "__main__":
    main()