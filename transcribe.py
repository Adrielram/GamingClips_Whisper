#!/usr/bin/env python3
"""
Script simplificado para transcribir videos de gaming con configuración optimizada.

Uso:
    python transcribe.py video.mp4
    python transcribe.py path/to/video.mkv
    
El script automáticamente:
- Usa modelo large-v3 para máxima calidad
- Configura beam-size 5 para mejor precisión
- Usa compute-type float16 para velocidad óptima
- Genera archivo .srt con el mismo nombre del video
- Aplica prompt argentino optimizado para gaming
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Cambiar al directorio del script para asegurar rutas correctas
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Verificar argumentos
    if len(sys.argv) != 2:
        print("❌ Error: Debes especificar el archivo de video a transcribir")
        print()
        print("📖 Uso:")
        print("    python transcribe.py video.mp4")
        print("    python transcribe.py path/to/video.mkv")
        print()
        print("🎯 El script generará automáticamente:")
        print("    - Archivo .srt con el mismo nombre del video")
        print("    - Configuración optimizada para gaming argentino")
        print("    - Máxima calidad de transcripción")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Convertir a ruta absoluta
    video_path = os.path.abspath(video_path)
    
    # Verificar que el archivo existe
    if not os.path.exists(video_path):
        print(f"❌ Error: No se encontró el archivo '{video_path}'")
        sys.exit(1)
    
    # Generar nombre del archivo de salida (en la misma carpeta que el video)
    video_file = Path(video_path)
    output_path = video_file.with_suffix('.srt')
    
    print("🎮 Transcriptor de Gaming - Configuración Optimizada")
    print("=" * 60)
    print(f"📹 Video de entrada: {video_path}")
    print(f"📝 Subtítulos de salida: {output_path}")
    print()
    print("⚙️  Configuración:")
    print("    • Modelo: large-v3 (máxima calidad)")
    print("    • Beam size: 5 (mejor precisión)")
    print("    • Compute type: float16 (velocidad óptima)")
    print("    • Prompt argentino: activado")
    print("    • Device: cuda (GPU si está disponible)")
    print()
    
    # Construir comando con ruta absoluta al main.py
    main_script = script_dir / "main.py"
    cmd = [
        sys.executable,  # Python actual
        str(main_script),  # Ruta completa a main.py
        video_path,
        "--model-size", "large-v3",
        "--beam-size", "5",
        "--compute-type", "float16",
        "--output", str(output_path),
        "--use-argentine-prompt",
        "--vad-split"  # Agregar división por detección de silencio
    ]
    
    print("🚀 Iniciando transcripción...")
    print("⏳ Esto puede tomar varios minutos dependiendo del video...")
    print()
    
    try:
        # Ejecutar el comando
        result = subprocess.run(cmd, check=True)
        
        print()
        print("✅ ¡Transcripción completada exitosamente!")
        print(f"📁 Archivo generado: {output_path}")
        
        # Verificar que el archivo se creó
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"📊 Tamaño del archivo: {file_size} bytes")
        
        print()
        print("🎯 Consejos:")
        print("    • Revisa el archivo .srt para verificar la calidad")
        print("    • Si hay errores, usa tools/postprocess_subs.py para limpiar")
        print("    • Para evaluar calidad: tools/evaluate_wer.py")
        
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Error durante la transcripción:")
        print(f"    Código de error: {e.returncode}")
        print()
        print("🔧 Posibles soluciones:")
        print("    • Verificar que el video no esté corrupto")
        print("    • Probar con --device cpu si hay problemas de GPU")
        print("    • Revisar que FFmpeg esté instalado")
        print("    • Verificar espacio en disco disponible")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print("⏹️  Transcripción cancelada por el usuario")
        sys.exit(1)
    
    except Exception as e:
        print()
        print(f"❌ Error inesperado: {e}")
        print()
        print("🔧 Intenta ejecutar manualmente:")
        print(f"    python main.py {video_path} --output {output_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()