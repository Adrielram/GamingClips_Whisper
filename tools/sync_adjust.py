"""
Herramienta para ajustar manualmente la sincronización de subtítulos.
Permite adelantar, atrasar, y ajustar duración de todos los subtítulos.

Uso:
python tools/sync_adjust.py input.srt output.srt --offset 0.5 --speed 1.02
"""

import argparse
import re
from pathlib import Path

def parse_srt_time(time_str):
    """Convierte timestamp SRT a segundos"""
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def format_srt_time(seconds):
    """Convierte segundos a timestamp SRT"""
    seconds = max(0, seconds)  # No permitir tiempos negativos
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def adjust_subtitle_timing(input_file, output_file, offset=0.0, speed=1.0, min_duration=0.5):
    """
    Ajusta timing de subtítulos
    
    Args:
        offset: segundos a adelantar (+) o atrasar (-)
        speed: factor de velocidad (1.0 = normal, 1.1 = 10% más rápido)
        min_duration: duración mínima por subtítulo
    """
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex para encontrar timestamps
    time_pattern = r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    
    def adjust_time_match(match):
        start_str, end_str = match.groups()
        
        # Convertir a segundos
        start_sec = parse_srt_time(start_str)
        end_sec = parse_srt_time(end_str)
        
        # Aplicar factor de velocidad
        start_sec *= speed
        end_sec *= speed
        
        # Aplicar offset
        start_sec += offset
        end_sec += offset
        
        # Asegurar duración mínima
        if end_sec - start_sec < min_duration:
            end_sec = start_sec + min_duration
        
        # Convertir de vuelta a formato SRT
        new_start = format_srt_time(start_sec)
        new_end = format_srt_time(end_sec)
        
        return f"{new_start} --> {new_end}"
    
    # Aplicar ajustes
    adjusted_content = re.sub(time_pattern, adjust_time_match, content)
    
    # Guardar resultado
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(adjusted_content)

def main():
    parser = argparse.ArgumentParser(description="Ajustar sincronización de subtítulos")
    parser.add_argument('input', help='Archivo SRT de entrada')
    parser.add_argument('output', help='Archivo SRT de salida')
    parser.add_argument('--offset', type=float, default=0.0,
                       help='Segundos a adelantar (+) o atrasar (-) los subtítulos')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Factor de velocidad (1.0=normal, 1.1=10%% más rápido)')
    parser.add_argument('--min-duration', type=float, default=0.5,
                       help='Duración mínima por subtítulo en segundos')
    args = parser.parse_args()
    
    if not Path(args.input).exists():
        print(f"❌ Error: No se encontró {args.input}")
        return
    
    print("🔧 Ajustador de Sincronización")
    print("=" * 40)
    print(f"📥 Entrada: {args.input}")
    print(f"📤 Salida: {args.output}")
    print(f"⏰ Offset: {args.offset:+.2f} segundos")
    print(f"🚀 Velocidad: {args.speed:.2f}x")
    print(f"⏱️ Duración mínima: {args.min_duration}s")
    print()
    
    try:
        adjust_subtitle_timing(
            args.input, 
            args.output, 
            args.offset, 
            args.speed, 
            args.min_duration
        )
        
        print("✅ Ajuste completado!")
        print()
        print("💡 Consejos:")
        if args.offset > 0:
            print(f"    • Subtítulos adelantados {args.offset}s")
        elif args.offset < 0:
            print(f"    • Subtítulos atrasados {abs(args.offset)}s")
        
        if args.speed != 1.0:
            change = (args.speed - 1.0) * 100
            print(f"    • Velocidad ajustada {change:+.1f}%")
        
        print("    • Prueba el archivo en tu reproductor favorito")
        print("    • Ajusta valores si es necesario")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()