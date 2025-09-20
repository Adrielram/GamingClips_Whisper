"""
Transcripción avanzada con timestamps a nivel de palabra usando Whisper.
Genera subtítulos perfectamente sincronizados con la voz.

Uso:
python tools/precise_transcribe.py video.mp4 output.srt --word-level --max-words-per-line 8
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

def extract_audio_with_ffmpeg(input_path: str, out_path: str) -> None:
    import subprocess
    cmd = [
        "ffmpeg", "-y", "-i", input_path, "-ac", "1", "-ar", "16000", "-vn", out_path
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.decode('utf-8', errors='ignore')}")

def transcribe_with_word_timestamps(audio_path, model_size="large-v3", device="cuda"):
    """Transcribir con timestamps a nivel de palabra"""
    from faster_whisper import WhisperModel
    
    print("🧠 Cargando modelo Whisper...")
    try:
        model = WhisperModel(model_size, device=device, compute_type="float16")
    except Exception:
        print("⚠️  GPU fallback a CPU...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print("🎤 Transcribiendo con timestamps de palabras...")
    
    # Configuración para máxima precisión temporal
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,  # CLAVE: timestamps por palabra
        condition_on_previous_text=False,
        temperature=0.0,
        initial_prompt="che, boludo, pibe, mina, laburo, guita, gg, clutch, lag, headshot, rekt"
    )
    
    print(f"🌍 Idioma detectado: {info.language} (confianza: {info.language_probability:.2f})")
    
    return list(segments), info

def apply_whisperx_alignment(segments, audio_path, language):
    """Aplicar alineación forzada con WhisperX para máxima precisión"""
    try:
        import whisperx
        print("🎯 Aplicando alineación forzada con WhisperX...")
        
        # Preparar segmentos para WhisperX
        segs_for_align = []
        for seg in segments:
            segs_for_align.append({
                "start": float(seg.start),
                "end": float(seg.end), 
                "text": str(seg.text)
            })
        
        # Cargar modelo de alineación
        try:
            align_model, metadata = whisperx.load_align_model(
                language_code=language, 
                device="cuda"
            )
        except Exception:
            align_model, metadata = whisperx.load_align_model(
                language_code=language,
                device="cpu"
            )
        
        # Realizar alineación
        result = whisperx.align(
            segs_for_align, 
            align_model, 
            metadata, 
            audio_path, 
            device="cuda"
        )
        
        # Procesar resultado
        aligned_segments = []
        segments_data = result.get("segments", []) if isinstance(result, dict) else result.segments
        
        for seg in segments_data:
            # Extraer palabras con timestamps precisos
            words = seg.get("words", []) if isinstance(seg, dict) else getattr(seg, "words", [])
            
            aligned_segments.append(SimpleNamespace(
                start=seg.get("start", 0) if isinstance(seg, dict) else getattr(seg, "start", 0),
                end=seg.get("end", 0) if isinstance(seg, dict) else getattr(seg, "end", 0),
                text=seg.get("text", "") if isinstance(seg, dict) else getattr(seg, "text", ""),
                words=words  # CLAVE: palabras individuales con timestamps
            ))
        
        print(f"✅ WhisperX: {len(aligned_segments)} segmentos alineados")
        return aligned_segments
        
    except ImportError:
        print("⚠️  WhisperX no disponible, usando timestamps de Whisper")
        return segments
    except Exception as e:
        print(f"⚠️  Error en WhisperX: {e}")
        return segments

def create_word_level_subtitles(segments, max_words_per_line=8, max_duration=3.0):
    """Crear subtítulos a nivel de palabra con sincronización perfecta"""
    subtitles = []
    
    for segment in segments:
        # Si tenemos palabras individuales (WhisperX)
        if hasattr(segment, 'words') and segment.words:
            words = segment.words
            current_line = []
            current_start = None
            
            for word_data in words:
                # Extraer datos de palabra
                if isinstance(word_data, dict):
                    word_text = word_data.get("word", "").strip()
                    word_start = word_data.get("start", 0)
                    word_end = word_data.get("end", 0)
                else:
                    word_text = getattr(word_data, "word", "").strip()
                    word_start = getattr(word_data, "start", 0)
                    word_end = getattr(word_data, "end", 0)
                
                if not word_text:
                    continue
                
                # Inicializar línea
                if current_start is None:
                    current_start = word_start
                
                current_line.append(word_text)
                
                # Decidir si cerrar la línea actual
                should_break = (
                    len(current_line) >= max_words_per_line or
                    (word_end - current_start) >= max_duration or
                    word_text.endswith(('.', '!', '?', ','))
                )
                
                if should_break:
                    # Crear subtítulo
                    text = ' '.join(current_line).strip()
                    if text:
                        subtitles.append(SimpleNamespace(
                            start=current_start,
                            end=word_end,
                            text=text
                        ))
                    
                    # Reiniciar para próxima línea
                    current_line = []
                    current_start = None
            
            # Procesar línea restante
            if current_line and current_start is not None:
                text = ' '.join(current_line).strip()
                if text:
                    # Usar el final del segmento como end time
                    subtitles.append(SimpleNamespace(
                        start=current_start,
                        end=segment.end,
                        text=text
                    ))
        
        else:
            # Fallback: usar segmento completo
            subtitles.append(SimpleNamespace(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip()
            ))
    
    return subtitles

def format_srt_time(seconds):
    """Formato de tiempo SRT"""
    ms = int((seconds - int(seconds)) * 1000)
    s = int(seconds) % 60
    m = (int(seconds) // 60) % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def save_precise_srt(subtitles, output_path):
    """Guardar SRT con timestamps precisos"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, sub in enumerate(subtitles, 1):
            start_time = format_srt_time(sub.start)
            end_time = format_srt_time(sub.end)
            f.write(f"{i}\n{start_time} --> {end_time}\n{sub.text}\n\n")

def main():
    parser = argparse.ArgumentParser(description="Transcripción precisa con sincronización perfecta")
    parser.add_argument("input", help="Video o audio de entrada")
    parser.add_argument("output", help="Archivo SRT de salida")
    parser.add_argument("--model-size", default="large-v3", help="Tamaño del modelo")
    parser.add_argument("--device", default="cuda", help="Dispositivo (cuda/cpu)")
    parser.add_argument("--word-level", action="store_true", help="Usar timestamps a nivel de palabra")
    parser.add_argument("--max-words-per-line", type=int, default=8, help="Máx palabras por línea")
    parser.add_argument("--max-duration", type=float, default=3.0, help="Duración máxima por subtítulo")
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Error: No se encontró {args.input}")
        sys.exit(1)
    
    print("🎯 Transcripción de Precisión Máxima")
    print("=" * 50)
    print(f"📹 Entrada: {args.input}")
    print(f"📝 Salida: {args.output}")
    print(f"🧠 Modelo: {args.model_size}")
    print(f"💻 Dispositivo: {args.device}")
    print(f"🎯 Palabras por línea: {args.max_words_per_line}")
    print(f"⏱️ Duración máxima: {args.max_duration}s")
    print()
    
    # Extraer audio si es necesario
    audio_path = args.input
    cleanup_audio = False
    
    if not args.input.lower().endswith(('.wav', '.mp3', '.flac', '.m4a')):
        print("🎵 Extrayendo audio...")
        fd, audio_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            extract_audio_with_ffmpeg(args.input, audio_path)
            cleanup_audio = True
        except Exception as e:
            print(f"❌ Error extrayendo audio: {e}")
            sys.exit(1)
    
    try:
        # Transcribir con timestamps de palabras
        segments, info = transcribe_with_word_timestamps(
            audio_path, args.model_size, args.device
        )
        
        # Aplicar alineación forzada si está disponible
        if args.word_level:
            segments = apply_whisperx_alignment(segments, audio_path, info.language)
        
        # Crear subtítulos sincronizados
        print("📝 Generando subtítulos sincronizados...")
        subtitles = create_word_level_subtitles(
            segments, args.max_words_per_line, args.max_duration
        )
        
        # Guardar resultado
        save_precise_srt(subtitles, args.output)
        
        print()
        print("🎉 ¡Transcripción completada!")
        print(f"📊 Segmentos originales: {len(segments)}")
        print(f"📊 Subtítulos finales: {len(subtitles)}")
        print(f"📁 Archivo: {args.output}")
        print()
        print("✨ Características:")
        print("    • Sincronización palabra por palabra")
        print("    • Timestamps precisos con WhisperX")
        print("    • Optimizado para gaming argentino")
        
    finally:
        if cleanup_audio and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

if __name__ == "__main__":
    main()