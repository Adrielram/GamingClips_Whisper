"""
Herramienta para dividir subtítulos largos en segmentos más pequeños
basándose en duración máxima y puntuación natural.

Uso:
python tools/split_long_subs.py input.srt output.srt --max-duration 3 --max-chars 80
"""

import argparse
import re
from pathlib import Path
from types import SimpleNamespace

def parse_srt_time(time_str):
    """Convierte timestamp SRT a segundos"""
    # 00:01:23,456 -> 83.456
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def format_srt_time(seconds):
    """Convierte segundos a timestamp SRT"""
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def read_srt(file_path):
    """Lee archivo SRT y retorna lista de subtítulos"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    blocks = content.split('\n\n')
    subtitles = []
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
            
        index = int(lines[0])
        time_line = lines[1]
        text = '\n'.join(lines[2:])
        
        # Parsear tiempos
        start_str, end_str = time_line.split(' --> ')
        start = parse_srt_time(start_str)
        end = parse_srt_time(end_str)
        
        subtitles.append(SimpleNamespace(
            index=index,
            start=start,
            end=end,
            text=text
        ))
    
    return subtitles

def split_long_subtitle(subtitle, max_duration=3.0, max_chars=80):
    """Divide un subtítulo largo en varios más cortos"""
    text = subtitle.text.strip()
    duration = subtitle.end - subtitle.start
    
    # Si ya es corto, no dividir
    if duration <= max_duration and len(text) <= max_chars:
        return [subtitle]
    
    # Dividir por oraciones primero
    sentences = re.split(r'[.!?]+\s*', text)
    if len(sentences) <= 1:
        # Si no hay oraciones, dividir por comas
        sentences = re.split(r',\s*', text)
    if len(sentences) <= 1:
        # Si no hay comas, dividir por palabras
        words = text.split()
        sentences = []
        for i in range(0, len(words), 8):  # Grupos de 8 palabras
            sentences.append(' '.join(words[i:i+8]))
    
    # Crear nuevos subtítulos
    result = []
    time_per_sentence = duration / len(sentences)
    current_time = subtitle.start
    
    for i, sentence in enumerate(sentences):
        if not sentence.strip():
            continue
            
        next_time = current_time + time_per_sentence
        if i == len(sentences) - 1:  # Último segmento
            next_time = subtitle.end
        
        result.append(SimpleNamespace(
            index=subtitle.index,
            start=current_time,
            end=next_time,
            text=sentence.strip()
        ))
        
        current_time = next_time
    
    return result

def write_srt(subtitles, file_path):
    """Escribe lista de subtítulos a archivo SRT"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            start_str = format_srt_time(sub.start)
            end_str = format_srt_time(sub.end)
            f.write(f"{i}\n{start_str} --> {end_str}\n{sub.text}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Dividir subtítulos largos en segmentos más pequeños")
    parser.add_argument('input', help='Archivo SRT de entrada')
    parser.add_argument('output', help='Archivo SRT de salida')
    parser.add_argument('--max-duration', type=float, default=3.0, 
                       help='Duración máxima por subtítulo en segundos (default: 3.0)')
    parser.add_argument('--max-chars', type=int, default=80,
                       help='Caracteres máximos por subtítulo (default: 80)')
    args = parser.parse_args()
    
    print(f"📖 Leyendo: {args.input}")
    subtitles = read_srt(args.input)
    print(f"📊 Subtítulos originales: {len(subtitles)}")
    
    # Procesar cada subtítulo
    new_subtitles = []
    for sub in subtitles:
        split_subs = split_long_subtitle(sub, args.max_duration, args.max_chars)
        new_subtitles.extend(split_subs)
    
    print(f"📊 Subtítulos después de dividir: {len(new_subtitles)}")
    
    print(f"💾 Guardando: {args.output}")
    write_srt(new_subtitles, args.output)
    
    print("✅ ¡Proceso completado!")
    print(f"📈 Mejora: {len(new_subtitles) - len(subtitles)} subtítulos adicionales")
    
    # Estadísticas
    avg_duration_before = sum(s.end - s.start for s in subtitles) / len(subtitles)
    avg_duration_after = sum(s.end - s.start for s in new_subtitles) / len(new_subtitles)
    
    print(f"📊 Duración promedio antes: {avg_duration_before:.2f}s")
    print(f"📊 Duración promedio después: {avg_duration_after:.2f}s")

if __name__ == '__main__':
    main()