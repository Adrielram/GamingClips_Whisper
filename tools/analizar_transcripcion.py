#!/usr/bin/env python3
"""
🔧 HERRAMIENTA DE ANÁLISIS DE TRANSCRIPCIÓN
==========================================
Analiza la calidad de transcripciones y detecta problemas específicos.
"""

import os
import sys
import re
from pathlib import Path
from collections import defaultdict

def analyze_transcription_quality(srt_path):
    """Analiza calidad de un archivo SRT"""
    
    if not os.path.exists(srt_path):
        print(f"❌ No se encontró el archivo: {srt_path}")
        return
    
    print("🔍 ANÁLISIS DE CALIDAD DE TRANSCRIPCIÓN")
    print("=" * 50)
    print(f"📝 Archivo: {Path(srt_path).name}")
    print()
    
    # Leer archivo SRT
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analizar estructura
    analyze_srt_structure(content)
    
    # Analizar problemas de palabras
    analyze_word_problems(content)
    
    # Analizar tiempos muertos
    analyze_timing_gaps(content)
    
    # Analizar sincronización
    analyze_synchronization_issues(content)

def analyze_srt_structure(content):
    """Analiza estructura básica del SRT"""
    lines = content.strip().split('\n\n')
    subtitles = []
    
    for block in lines:
        block_lines = block.strip().split('\n')
        if len(block_lines) >= 3:
            try:
                # Parsear timestamp
                time_line = block_lines[1]
                start_time, end_time = time_line.split(' --> ')
                text = ' '.join(block_lines[2:])
                
                start_seconds = time_to_seconds(start_time)
                end_seconds = time_to_seconds(end_time)
                
                subtitles.append({
                    'start': start_seconds,
                    'end': end_seconds,
                    'duration': end_seconds - start_seconds,
                    'text': text,
                    'word_count': len(text.split())
                })
            except:
                continue
    
    if not subtitles:
        print("❌ No se pudieron parsear los subtítulos")
        return
    
    # Estadísticas generales
    total_subtitles = len(subtitles)
    total_duration = subtitles[-1]['end'] - subtitles[0]['start']
    avg_duration = sum(s['duration'] for s in subtitles) / total_subtitles
    avg_words = sum(s['word_count'] for s in subtitles) / total_subtitles
    
    print("📊 ESTRUCTURA GENERAL:")
    print(f"    📝 Total de subtítulos: {total_subtitles}")
    print(f"    ⏱️ Duración total: {total_duration:.1f}s")
    print(f"    📏 Duración promedio: {avg_duration:.1f}s")
    print(f"    📖 Palabras promedio: {avg_words:.1f}")
    print()
    
    # Detectar problemas de estructura
    problems = []
    
    # Subtítulos muy largos
    long_subs = [s for s in subtitles if s['duration'] > 4.0]
    if long_subs:
        problems.append(f"⚠️ {len(long_subs)} subtítulos muy largos (>4s)")
    
    # Subtítulos muy cortos
    short_subs = [s for s in subtitles if s['duration'] < 0.5]
    if short_subs:
        problems.append(f"⚠️ {len(short_subs)} subtítulos muy cortos (<0.5s)")
    
    # Muchas palabras por línea
    dense_subs = [s for s in subtitles if s['word_count'] > 8]
    if dense_subs:
        problems.append(f"⚠️ {len(dense_subs)} subtítulos con muchas palabras (>8)")
    
    if problems:
        print("🚨 PROBLEMAS DETECTADOS:")
        for problem in problems:
            print(f"    {problem}")
        print()
    else:
        print("✅ Estructura correcta")
        print()

def analyze_word_problems(content):
    """Analiza problemas de reconocimiento de palabras"""
    print("🔤 ANÁLISIS DE PALABRAS:")
    
    # Palabras sospechosas (posibles errores de transcripción)
    suspicious_patterns = [
        r'\babriel\b',      # Gabriel mal transcrito
        r'\bebastián\b',    # Sebastián mal transcrito
        r'\bristian\b',     # Cristian mal transcrito
        r'\bamián\b',       # Damián mal transcrito
        r'\b\w{1,2}\b',     # Palabras muy cortas (posibles errores)
        r'[a-z]{10,}',      # Palabras muy largas sin espacios
        r'\b[BCDFGHJKLMNPQRSTVWXYZ]{3,}\b',  # Consonantes seguidas
    ]
    
    issues_found = []
    
    for pattern in suspicious_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues_found.extend(matches)
    
    # Contar palabras extrañas
    all_words = re.findall(r'\b\w+\b', content.lower())
    word_freq = defaultdict(int)
    for word in all_words:
        word_freq[word] += 1
    
    # Palabras que aparecen solo una vez (posibles errores)
    rare_words = [word for word, freq in word_freq.items() if freq == 1 and len(word) > 3]
    
    if issues_found or rare_words:
        print(f"    ⚠️ {len(set(issues_found))} palabras sospechosas encontradas")
        if issues_found:
            print(f"       Ejemplos: {', '.join(set(issues_found)[:5])}")
        
        if rare_words and len(rare_words) > 10:
            print(f"    📝 {len(rare_words)} palabras únicas (posibles errores)")
            print(f"       Ejemplos: {', '.join(rare_words[:5])}")
    else:
        print("    ✅ No se detectaron problemas obvios de palabras")
    
    print()

def analyze_timing_gaps(content):
    """Analiza tiempos muertos y huecos en la transcripción"""
    print("🔇 ANÁLISIS DE TIEMPOS MUERTOS:")
    
    # Parsear timestamps
    time_pattern = r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    timestamps = re.findall(time_pattern, content)
    
    if len(timestamps) < 2:
        print("    ❌ No hay suficientes timestamps para analizar")
        return
    
    gaps = []
    previous_end = None
    
    for start_str, end_str in timestamps:
        start_time = time_to_seconds(start_str)
        end_time = time_to_seconds(end_str)
        
        if previous_end is not None:
            gap = start_time - previous_end
            if gap > 2.0:  # Gap mayor a 2 segundos
                gaps.append(gap)
        
        previous_end = end_time
    
    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        max_gap = max(gaps)
        print(f"    ⚠️ {len(gaps)} huecos largos detectados (>2s)")
        print(f"    📊 Hueco promedio: {avg_gap:.1f}s")
        print(f"    📊 Hueco máximo: {max_gap:.1f}s")
        
        if len(gaps) > len(timestamps) * 0.2:
            print("    🚨 Muchos tiempos muertos - configurar VAD más agresivo")
    else:
        print("    ✅ No hay tiempos muertos significativos")
    
    print()

def analyze_synchronization_issues(content):
    """Analiza problemas de sincronización temporal"""
    print("⏱️ ANÁLISIS DE SINCRONIZACIÓN:")
    
    # Parsear timestamps
    time_pattern = r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    timestamps = re.findall(time_pattern, content)
    
    if len(timestamps) < 10:
        print("    ❌ No hay suficientes timestamps para análisis de drift")
        return
    
    # Calcular velocidad de subtítulos a lo largo del tiempo
    velocities = []
    window_size = 5
    
    for i in range(len(timestamps) - window_size):
        window_start = time_to_seconds(timestamps[i][0])
        window_end = time_to_seconds(timestamps[i + window_size][1])
        window_duration = window_end - window_start
        
        velocities.append(window_duration / window_size)
    
    if len(velocities) > 2:
        # Detectar aceleración/desaceleración
        start_velocity = sum(velocities[:3]) / 3
        end_velocity = sum(velocities[-3:]) / 3
        
        velocity_change = (end_velocity - start_velocity) / start_velocity
        
        if abs(velocity_change) > 0.05:  # Cambio mayor al 5%
            direction = "aceleración" if velocity_change > 0 else "desaceleración"
            print(f"    ⚠️ Drift detectado: {direction} del {abs(velocity_change)*100:.1f}%")
            print("    🔧 Recomendación: aplicar corrección temporal")
        else:
            print("    ✅ Sincronización estable")
    
    # Analizar duración de subtítulos al final vs inicio
    first_quarter = timestamps[:len(timestamps)//4]
    last_quarter = timestamps[-len(timestamps)//4:]
    
    avg_duration_start = sum(time_to_seconds(end) - time_to_seconds(start) 
                           for start, end in first_quarter) / len(first_quarter)
    avg_duration_end = sum(time_to_seconds(end) - time_to_seconds(start) 
                         for start, end in last_quarter) / len(last_quarter)
    
    duration_change = (avg_duration_end - avg_duration_start) / avg_duration_start
    
    if abs(duration_change) > 0.1:  # Cambio mayor al 10%
        trend = "más largos" if duration_change > 0 else "más cortos"
        print(f"    📊 Subtítulos al final son {abs(duration_change)*100:.1f}% {trend}")
    
    print()

def time_to_seconds(time_str):
    """Convierte timestamp SRT a segundos"""
    # Formato: HH:MM:SS,mmm
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python analizar_transcripcion.py archivo.srt")
        return
    
    srt_path = sys.argv[1]
    analyze_transcription_quality(srt_path)
    
    print("💡 RECOMENDACIONES:")
    print("    • Para palabras incorrectas: usar transcribe_mejorado.py")
    print("    • Para tiempos muertos: ajustar VAD más agresivo")
    print("    • Para sincronización: aplicar corrección temporal")
    print()

if __name__ == "__main__":
    main()