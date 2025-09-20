#!/usr/bin/env python3
"""
Script de transcripción ULTRA-PRECISA con sincronización perfecta.
Combina múltiples técnicas para lograr la mejor sincronización posible.

Uso:
    python transcribe_precise.py video.mp4
    
Técnicas aplicadas:
1. Word-level timestamps de Whisper
2. Forced alignment con WhisperX 
3. VAD preciso con pyannote
4. Post-procesamiento temporal
5. Optimización para gaming argentino
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("❌ Error: Debes especificar el archivo de video a transcribir")
        print()
        print("📖 Uso:")
        print("    python transcribe_precise.py video.mp4")
        print()
        print("🎯 Genera subtítulos con sincronización ULTRA-PRECISA")
        sys.exit(1)
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    video_path = sys.argv[1]
    video_path = os.path.abspath(video_path)
    
    if not os.path.exists(video_path):
        print(f"❌ Error: No se encontró el archivo '{video_path}'")
        sys.exit(1)
    
    video_file = Path(video_path)
    output_path = video_file.with_suffix('.srt')
    
    print("🎯 TRANSCRIPCIÓN ULTRA-PRECISA")
    print("=" * 60)
    print(f"📹 Video: {video_path}")
    print(f"📝 Salida: {output_path}")
    print()
    print("🚀 Técnicas aplicadas:")
    print("    • Word-level timestamps")
    print("    • Forced alignment (WhisperX)")
    print("    • VAD preciso")
    print("    • Optimización gaming argentino")
    print("    • Post-procesamiento temporal")
    print()
    
    # Usar la herramienta de transcripción precisa
    precise_script = script_dir / "tools" / "precise_transcribe.py"
    cmd = [
        sys.executable,
        str(precise_script),
        video_path,
        str(output_path),
        "--model-size", "large-v3",
        "--device", "cuda",
        "--word-level",
        "--max-words-per-line", "6",  # Menos palabras = mejor sincronización
        "--max-duration", "2.5"      # Duración más corta = más preciso
    ]
    
    try:
        print("⏳ Procesando (esto puede tomar varios minutos)...")
        result = subprocess.run(cmd, check=True)
        
        print()
        print("🎉 ¡TRANSCRIPCIÓN ULTRA-PRECISA COMPLETADA!")
        print(f"📁 Archivo: {output_path}")
        print()
        print("✨ Características del archivo generado:")
        print("    🎯 Sincronización palabra por palabra")
        print("    ⏱️ Timestamps con precisión de milisegundos")
        print("    🎮 Optimizado para gaming argentino")
        print("    📏 Líneas cortas (máx 6 palabras)")
        print("    ⚡ Subtítulos de máximo 2.5 segundos")
        print()
        print("💡 Consejos para usar el archivo:")
        print("    • Úsalo en reproductores que soporten SRT")
        print("    • Ajusta velocidad de subtítulos si es necesario")
        print("    • Verifica sincronización en momentos clave")
        
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Error durante la transcripción ultra-precisa")
        print()
        print("🔄 Intentando método de respaldo...")
        
        # Método de respaldo con transcripción normal mejorada
        fallback_script = script_dir / "transcribe.py"
        fallback_cmd = [sys.executable, str(fallback_script), video_path]
        
        try:
            subprocess.run(fallback_cmd, check=True)
            print("✅ Transcripción de respaldo completada")
        except subprocess.CalledProcessError:
            print("❌ Error también en el método de respaldo")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print("⏹️  Transcripción cancelada por el usuario")
        sys.exit(1)

if __name__ == "__main__":
    main()