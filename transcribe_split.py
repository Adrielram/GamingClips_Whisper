#!/usr/bin/env python3
"""
Script de transcripción con división automática de subtítulos largos.
Combina transcripción + post-procesamiento en un solo paso.

Uso:
    python transcribe_split.py video.mp4
    
Genera:
    - video.srt (con subtítulos divididos automáticamente)
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("❌ Error: Debes especificar el archivo de video a transcribir")
        print()
        print("📖 Uso:")
        print("    python transcribe_split.py video.mp4")
        print()
        print("🎯 Genera subtítulos divididos automáticamente (máx 3s por línea)")
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
    temp_output = video_file.with_suffix('.temp.srt')
    final_output = video_file.with_suffix('.srt')
    
    print("🎮 Transcriptor con División Automática")
    print("=" * 50)
    print(f"📹 Video: {video_path}")
    print(f"📝 Salida: {final_output}")
    print()
    
    # Paso 1: Transcripción inicial
    print("🚀 Paso 1/2: Transcribiendo video...")
    main_script = script_dir / "main.py"
    cmd1 = [
        sys.executable,
        str(main_script),
        video_path,
        "--model-size", "large-v3",
        "--beam-size", "5",
        "--compute-type", "float16",
        "--output", str(temp_output),
        "--use-argentine-prompt",
        "--vad-split"
    ]
    
    try:
        subprocess.run(cmd1, check=True)
        print("✅ Transcripción completada")
    except subprocess.CalledProcessError:
        print("❌ Error en la transcripción")
        sys.exit(1)
    
    # Paso 2: División de subtítulos largos
    print("🔄 Paso 2/2: Dividiendo subtítulos largos...")
    split_script = script_dir / "tools" / "split_long_subs.py"
    cmd2 = [
        sys.executable,
        str(split_script),
        str(temp_output),
        str(final_output),
        "--max-duration", "3.0",
        "--max-chars", "75"
    ]
    
    try:
        subprocess.run(cmd2, check=True)
        print("✅ División completada")
    except subprocess.CalledProcessError:
        print("❌ Error en la división")
        sys.exit(1)
    
    # Limpiar archivo temporal
    try:
        os.remove(temp_output)
    except:
        pass
    
    print()
    print("🎉 ¡Proceso completado!")
    print(f"📁 Archivo final: {final_output}")
    print()
    print("✨ Características del archivo generado:")
    print("    • Subtítulos divididos (máx 3 segundos)")
    print("    • Líneas cortas (máx 75 caracteres)")
    print("    • Optimizado para gaming argentino")

if __name__ == "__main__":
    main()