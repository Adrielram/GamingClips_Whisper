#!/usr/bin/env python3
"""
🔍 ANALIZADOR DE SINCRONIZACIÓN
===============================
Analiza problemas específicos de sincronización en archivos SRT.
"""

import os
import sys
import re
from pathlib import Path

def time_to_seconds(time_str):
    """Convierte timestamp SRT a segundos"""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def analyze_sync_problems(srt_path):
    """Analiza problemas específicos de sincronización"""
    
    if not os.path.exists(srt_path):
        print(f"❌ No se encontró el archivo: {srt_path}")
        return
    
    print("🔍 ANÁLISIS DE SINCRONIZACIÓN DETALLADO")
    print("=" * 60)
    print(f"📝 Archivo: {Path(srt_path).name}")
    print()
    
    # Leer archivo SRT
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parsear subtítulos
    subtitles = parse_srt_content(content)
    
    if not subtitles:
        print("❌ No se pudieron parsear los subtítulos")
        return
    
    print(f"📊 Total de subtítulos: {len(subtitles)}")
    print(f"⏱️ Duración total: {subtitles[-1]['end'] - subtitles[0]['start']:.1f}s")
    print()
    
    # Análisis específicos de sincronización
    analyze_drift_patterns(subtitles)
    analyze_gap_patterns(subtitles)
    analyze_duration_patterns(subtitles)
    analyze_timing_consistency(subtitles)
    
    # Recomendaciones específicas
    provide_sync_recommendations(subtitles)

def parse_srt_content(content):
    """Parsea contenido SRT y extrae información"""
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
            except Exception as e:
                continue
    
    return subtitles

def analyze_drift_patterns(subtitles):
    """Analiza patrones de drift temporal"""
    print("🕐 ANÁLISIS DE DRIFT TEMPORAL:")
    
    if len(subtitles) < 10:
        print("    ⚠️ No hay suficientes subtítulos para analizar drift")
        return
    
    # Dividir en segmentos (inicio, medio, final)
    third = len(subtitles) // 3
    
    start_segment = subtitles[:third]
    middle_segment = subtitles[third:2*third]
    end_segment = subtitles[2*third:]
    
    # Calcular duración promedio por segmento
    avg_duration_start = sum(s['duration'] for s in start_segment) / len(start_segment)
    avg_duration_middle = sum(s['duration'] for s in middle_segment) / len(middle_segment)
    avg_duration_end = sum(s['duration'] for s in end_segment) / len(end_segment)
    
    print(f"    📊 Duración promedio:")
    print(f"        🟢 Inicio:  {avg_duration_start:.2f}s")
    print(f"        🟡 Medio:   {avg_duration_middle:.2f}s") 
    print(f"        🔴 Final:   {avg_duration_end:.2f}s")
    
    # Detectar tendencias
    start_to_middle = (avg_duration_middle - avg_duration_start) / avg_duration_start
    middle_to_end = (avg_duration_end - avg_duration_middle) / avg_duration_middle
    
    if abs(start_to_middle) > 0.15:
        trend = "aumentan" if start_to_middle > 0 else "disminuyen"
        print(f"    ⚠️ Las duraciones {trend} {abs(start_to_middle)*100:.1f}% hacia el medio")
    
    if abs(middle_to_end) > 0.15:
        trend = "aumentan" if middle_to_end > 0 else "disminuyen"
        print(f"    ⚠️ Las duraciones {trend} {abs(middle_to_end)*100:.1f}% hacia el final")
    
    # Calcular velocidad de subtítulos
    time_per_subtitle_start = (start_segment[-1]['end'] - start_segment[0]['start']) / len(start_segment)
    time_per_subtitle_end = (end_segment[-1]['end'] - end_segment[0]['start']) / len(end_segment)
    
    speed_change = (time_per_subtitle_end - time_per_subtitle_start) / time_per_subtitle_start
    
    if abs(speed_change) > 0.10:
        direction = "desaceleran" if speed_change > 0 else "aceleran"
        print(f"    🚨 DRIFT DETECTADO: Los subtítulos {direction} {abs(speed_change)*100:.1f}%")
        print(f"    💡 Recomendación: Aplicar corrección temporal progresiva")
    else:
        print(f"    ✅ No se detectó drift significativo")
    
    print()

def analyze_gap_patterns(subtitles):
    """Analiza patrones en los gaps entre subtítulos"""
    print("⏸️  ANÁLISIS DE GAPS ENTRE SUBTÍTULOS:")
    
    gaps = []
    for i in range(len(subtitles) - 1):
        gap = subtitles[i+1]['start'] - subtitles[i]['end']
        gaps.append(gap)
    
    if not gaps:
        return
    
    avg_gap = sum(gaps) / len(gaps)
    max_gap = max(gaps)
    min_gap = min(gaps)
    
    print(f"    📊 Gap promedio: {avg_gap:.2f}s")
    print(f"    📊 Gap máximo: {max_gap:.2f}s")
    print(f"    📊 Gap mínimo: {min_gap:.2f}s")
    
    # Detectar gaps problemáticos
    large_gaps = [g for g in gaps if g > 2.0]
    negative_gaps = [g for g in gaps if g < 0]
    
    if large_gaps:
        print(f"    ⚠️ {len(large_gaps)} gaps largos (>2s) - posibles tiempos muertos")
    
    if negative_gaps:
        print(f"    🚨 {len(negative_gaps)} gaps negativos - SOLAPAMIENTO detectado")
        print(f"    💡 Recomendación: Revisar timestamps, hay superposición")
    
    if avg_gap > 1.5:
        print(f"    ⚠️ Gaps muy largos en promedio - VAD muy conservador")
    elif avg_gap < 0.2:
        print(f"    ⚠️ Gaps muy cortos - posible concatenación excesiva")
    else:
        print(f"    ✅ Gaps en rango normal")
    
    print()

def analyze_duration_patterns(subtitles):
    """Analiza patrones en las duraciones de subtítulos"""
    print("⏱️  ANÁLISIS DE DURACIONES:")
    
    durations = [s['duration'] for s in subtitles]
    avg_duration = sum(durations) / len(durations)
    
    # Categorizar duraciones
    very_short = [d for d in durations if d < 0.5]
    short = [d for d in durations if 0.5 <= d < 1.5]
    normal = [d for d in durations if 1.5 <= d < 3.5]
    long = [d for d in durations if 3.5 <= d < 6.0]
    very_long = [d for d in durations if d >= 6.0]
    
    print(f"    📊 Duración promedio: {avg_duration:.2f}s")
    print(f"    📊 Distribución:")
    print(f"        ⚡ Muy cortos (<0.5s): {len(very_short)} ({len(very_short)/len(durations)*100:.1f}%)")
    print(f"        🟢 Cortos (0.5-1.5s): {len(short)} ({len(short)/len(durations)*100:.1f}%)")
    print(f"        🟡 Normales (1.5-3.5s): {len(normal)} ({len(normal)/len(durations)*100:.1f}%)")
    print(f"        🟠 Largos (3.5-6.0s): {len(long)} ({len(long)/len(durations)*100:.1f}%)")
    print(f"        🔴 Muy largos (>6.0s): {len(very_long)} ({len(very_long)/len(durations)*100:.1f}%)")
    
    # Recomendaciones
    if len(very_short) > len(subtitles) * 0.2:
        print(f"    ⚠️ Muchos subtítulos muy cortos - pueden ser difíciles de leer")
    
    if len(very_long) > 0:
        print(f"    ⚠️ Subtítulos muy largos detectados - dividir para mejor lectura")
    
    print()

def analyze_timing_consistency(subtitles):
    """Analiza consistencia en el timing"""
    print("📏 ANÁLISIS DE CONSISTENCIA:")
    
    # Calcular palabras por segundo
    wps_values = []
    for sub in subtitles:
        if sub['duration'] > 0:
            wps = sub['word_count'] / sub['duration']
            wps_values.append(wps)
    
    if wps_values:
        avg_wps = sum(wps_values) / len(wps_values)
        print(f"    📊 Palabras por segundo promedio: {avg_wps:.1f}")
        
        # Detectar outliers
        fast_subs = [wps for wps in wps_values if wps > avg_wps * 2]
        slow_subs = [wps for wps in wps_values if wps < avg_wps * 0.5]
        
        if fast_subs:
            print(f"    ⚡ {len(fast_subs)} subtítulos muy rápidos (>{avg_wps*2:.1f} pps)")
        
        if slow_subs:
            print(f"    🐌 {len(slow_subs)} subtítulos muy lentos (<{avg_wps*0.5:.1f} pps)")
    
    print()

def provide_sync_recommendations(subtitles):
    """Proporciona recomendaciones específicas"""
    print("💡 RECOMENDACIONES ESPECÍFICAS:")
    
    # Análisis general
    total_duration = subtitles[-1]['end'] - subtitles[0]['start']
    avg_duration = sum(s['duration'] for s in subtitles) / len(subtitles)
    
    print("    🔧 Para mejor sincronización:")
    
    if avg_duration > 3.0:
        print("    • Usar configuración más agresiva de segmentación")
        print("    • Reducir max_duration en agrupación")
    
    # Detectar si hay drift
    start_third = subtitles[:len(subtitles)//3]
    end_third = subtitles[-len(subtitles)//3:]
    
    start_avg = sum(s['duration'] for s in start_third) / len(start_third)
    end_avg = sum(s['duration'] for s in end_third) / len(end_third)
    
    if abs(end_avg - start_avg) / start_avg > 0.15:
        print("    • APLICAR corrección de drift temporal")
        print("    • Usar transcribe_sync_perfect.py")
    else:
        print("    • Mantener timestamps originales de Whisper")
        print("    • NO aplicar corrección temporal")
    
    print()
    print("📋 Scripts recomendados:")
    if abs(end_avg - start_avg) / start_avg > 0.15:
        print("    🎯 transcribe_sync_perfect.py (timestamps originales)")
    else:
        print("    ✅ transcribe_FINAL.py (configuración actual)")

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python analizar_sync.py archivo.srt")
        return
    
    srt_path = sys.argv[1]
    analyze_sync_problems(srt_path)

if __name__ == "__main__":
    main()