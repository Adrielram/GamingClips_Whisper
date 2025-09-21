#!/usr/bin/env python3
"""
TRANSCRIPCIÓN CON PRE-PROCESAMIENTO DE AUDIO AVANZADO
====================================================

Script especializado que aplica múltiples técnicas de mejora de audio
antes de la transcripción para maximizar la precisión en contenido gaming.

Características:
- Pre-procesamiento FFmpeg con filtros especializados
- Separación de fuentes de audio (voz vs efectos/música)
- Normalización adaptativa de voz
- Reducción de ruido específica para gaming
- Amplificación inteligente de frecuencias de habla
- Compresión dinámica para voces sobre efectos

Uso: python transcribe_enhanced.py video.mp4
"""

import os
import sys
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from datetime import timedelta
from faster_whisper import WhisperModel
import numpy as np

# Configuración optimizada para gaming argentino
WHISPER_CONFIG = {
    "model": "large-v3",
    "language": "es",
    "device": "cpu",
    "compute_type": "int8",
    "beam_size": 5,
    "best_of": 5,
    "patience": 1.5,
    "length_penalty": 1.0,
    "repetition_penalty": 1.05,
    "no_repeat_ngram_size": 3,
    "temperature": [0.0, 0.2, 0.4],
    "compression_ratio_threshold": 2.4,
    "log_prob_threshold": -0.8,
    "no_speech_threshold": 0.35,
    "condition_on_previous_text": True,
    "prompt_reset_on_temperature": 0.5,
    "initial_prompt": """Esto es una conversación en español argentino sobre videojuegos. Nombres comunes: Gabriel, Adriel, Estani, wilo, corcho, ruben, erizo. Expresiones típicas: "dale", "bueno", "che", "boludo", "posta", "zafar", "hinchar", "joder".""",
    "word_timestamps": True,
    "hallucination_silence_threshold": 2.0
}

# VAD optimizado para audio mejorado
VAD_CONFIG = {
    "threshold": 0.3,  # Más sensible con audio limpio
    "min_speech_duration_ms": 150,
    "min_silence_duration_ms": 250,
    "speech_pad_ms": 50
}

# Configuración de chunking
CHUNK_CONFIG = {
    "max_words": 3,
    "max_chars": 35,
    "min_chars": 5,
    "max_duration": 2.5,
    "min_duration": 0.8,
    "natural_breaks": ['.', '!', '?', ',', ';', ':', ' y ', ' o ', ' pero ', ' aunque '],
    "prefer_breaks": ['.', '!', '?'],
    "word_distribution": True,
    "sync_conservative": True,
    "silence_detection": True,
    "min_silence_gap": 0.3,
    "max_silence_extend": 0.5
}

# Configuración de pre-procesamiento de audio
AUDIO_ENHANCEMENT_CONFIG = {
    "target_sample_rate": 16000,
    "target_channels": 1,
    "voice_freq_range": (80, 7000),      # Rango de frecuencias de voz humana
    "noise_reduction": True,
    "voice_enhancement": True,
    "dynamic_compression": True,
    "adaptive_normalization": True,
    "gaming_filters": True
}

def format_timestamp(seconds):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def extract_audio_from_video(video_path, output_path):
    """Extrae audio del video sin procesamiento"""
    print("🎵 Extrayendo audio del video...")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",  # Mantener estéreo inicialmente
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Audio extraído: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error extrayendo audio: {e.stderr}")
        return False

def apply_noise_reduction(input_path, output_path):
    """Aplica reducción de ruido específica para gaming"""
    print("🔇 Aplicando reducción de ruido...")
    
    # Filtro de reducción de ruido adaptativa (corregido)
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", (
            "highpass=f=80,"                    # Eliminar ruido grave
            "lowpass=f=8000,"                   # Eliminar agudos extremos
            "afftdn=nr=20:nf=-40:tn=1,"        # Reducción de ruido FFT
            "adeclip"                          # Eliminar clipping (sin parámetros problemáticos)
        ),
        "-acodec", "pcm_s16le",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Ruido reducido: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en reducción de ruido: {e.stderr}")
        return False

def enhance_voice_frequencies(input_path, output_path):
    """Mejora frecuencias específicas de voz humana"""
    print("🗣️ Mejorando frecuencias de voz...")
    
    # Ecualización específica para voz
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", (
            "equalizer=f=200:width_type=o:width=1:g=2,"    # Boost graves de voz
            "equalizer=f=1000:width_type=o:width=1:g=3,"   # Boost medios de voz  
            "equalizer=f=3000:width_type=o:width=1:g=2,"   # Boost agudos de voz
            "equalizer=f=6000:width_type=o:width=1:g=-2"   # Reducir sibilantes
        ),
        "-acodec", "pcm_s16le",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Voz mejorada: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error mejorando voz: {e.stderr}")
        return False

def apply_dynamic_compression(input_path, output_path):
    """Aplica compresión dinámica para voces sobre efectos"""
    print("🎚️ Aplicando compresión dinámica...")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", (
            "compand=0.01:1:"                 # Attack:Decay
            "-30/-30|-20/-15|-10/-5|0/0:"     # Puntos de compresión
            "6:0.1"                           # Gain post y delay
        ),
        "-acodec", "pcm_s16le",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Compresión aplicada: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en compresión: {e.stderr}")
        return False

def apply_gaming_filters(input_path, output_path):
    """Aplica filtros específicos para audio de gaming"""
    print("🎮 Aplicando filtros específicos de gaming...")
    
    # Intentar filtros avanzados primero
    cmd_advanced = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", (
            "highpass=f=100,"                  # Eliminar ruido de ventiladores
            "equalizer=f=60:width_type=h:width=20:g=-10,"   # Reducir hum 60Hz
            "equalizer=f=120:width_type=h:width=20:g=-8,"   # Reducir armónico 120Hz
            "bandpass=f=300:width_type=h:width=6000"        # Enfocar en rango de voz amplio
        ),
        "-acodec", "pcm_s16le",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd_advanced, capture_output=True, text=True, check=True)
        print(f"✅ Filtros gaming aplicados: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Filtros avanzados fallaron, usando básicos...")
        
        # Fallback: solo filtros básicos
        cmd_basic = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-af", (
                "highpass=f=80,"               # Eliminar ruido grave
                "lowpass=f=7000"               # Eliminar agudos extremos
            ),
            "-acodec", "pcm_s16le",
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd_basic, capture_output=True, text=True, check=True)
            print(f"✅ Filtros gaming básicos aplicados: {output_path}")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Error en filtros gaming: {e2.stderr}")
            return False

def normalize_and_finalize(input_path, output_path):
    """Normalización final y conversión a formato óptimo para Whisper"""
    print("📊 Normalizando audio final...")
    
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-af", (
            "loudnorm=I=-23:LRA=7:tp=-2,"     # Normalización de volumen estándar
            "volume=1.5"                       # Amplificación adicional
        ),
        "-ar", str(AUDIO_ENHANCEMENT_CONFIG["target_sample_rate"]),
        "-ac", str(AUDIO_ENHANCEMENT_CONFIG["target_channels"]),
        "-acodec", "pcm_s16le",
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Audio finalizado: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en normalización: {e.stderr}")
        return False

def enhance_audio_quality(video_path, temp_dir):
    """Pipeline completo de mejora de audio"""
    print("🎵 INICIANDO PIPELINE DE MEJORA DE AUDIO")
    print("=" * 50)
    
    video_name = Path(video_path).stem
    
    # Rutas temporales
    raw_audio = temp_dir / f"{video_name}_raw.wav"
    noise_reduced = temp_dir / f"{video_name}_noise_reduced.wav"
    voice_enhanced = temp_dir / f"{video_name}_voice_enhanced.wav"
    compressed = temp_dir / f"{video_name}_compressed.wav"
    gaming_filtered = temp_dir / f"{video_name}_gaming_filtered.wav"
    final_audio = temp_dir / f"{video_name}_enhanced_final.wav"
    
    # Pipeline de procesamiento
    steps = [
        ("Extracción", extract_audio_from_video, video_path, raw_audio),
        ("Reducción ruido", apply_noise_reduction, raw_audio, noise_reduced),
        ("Mejora voz", enhance_voice_frequencies, noise_reduced, voice_enhanced),
        ("Compresión", apply_dynamic_compression, voice_enhanced, compressed),
        ("Filtros gaming", apply_gaming_filters, compressed, gaming_filtered),
        ("Normalización", normalize_and_finalize, gaming_filtered, final_audio)
    ]
    
    for step_name, func, input_file, output_file in steps:
        print(f"🔄 {step_name}...")
        if not func(input_file, output_file):
            print(f"❌ Error en {step_name}")
            return None
    
    print("✅ PIPELINE DE AUDIO COMPLETADO")
    print(f"📄 Audio mejorado: {final_audio}")
    return final_audio

def split_text_intelligently(text, max_words=3):
    """Divide texto inteligentemente por palabras"""
    words = text.split()
    if len(words) <= max_words:
        return [text]
    
    chunks = []
    current_chunk_words = []
    
    for word in words:
        current_chunk_words.append(word)
        
        if len(current_chunk_words) >= max_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append(chunk_text)
            current_chunk_words = []
        elif any(punct in word for punct in CHUNK_CONFIG["prefer_breaks"]):
            if len(current_chunk_words) >= 1:
                chunk_text = " ".join(current_chunk_words)
                chunks.append(chunk_text)
                current_chunk_words = []
    
    if current_chunk_words:
        chunk_text = " ".join(current_chunk_words)
        chunks.append(chunk_text)
    
    return chunks

def detect_silence_gaps(segments):
    """Detecta gaps de silencio entre segmentos"""
    silence_gaps = []
    
    for i in range(len(segments) - 1):
        current_end = segments[i]["end"]
        next_start = segments[i + 1]["start"]
        gap_duration = next_start - current_end
        
        if gap_duration >= CHUNK_CONFIG["min_silence_gap"]:
            silence_gaps.append({
                "start": current_end,
                "end": next_start,
                "duration": gap_duration
            })
    
    return silence_gaps

def process_segments_with_precise_timing(segments):
    """Procesa segmentos usando timing preciso y respetando silencios"""
    if not segments:
        return []
    
    silence_gaps = detect_silence_gaps(segments)
    print(f"🔇 Detectados {len(silence_gaps)} gaps de silencio")
    
    chunked_segments = []
    
    for segment in segments:
        text = segment["text"].strip()
        if not text:
            continue
            
        start_time = segment["start"]
        end_time = segment["end"]
        words_timing = segment.get("words", [])
        
        if words_timing and len(words_timing) > 0:
            word_chunks = []
            current_chunk = []
            
            for word_info in words_timing:
                current_chunk.append(word_info)
                
                if len(current_chunk) >= CHUNK_CONFIG["max_words"]:
                    word_chunks.append(current_chunk)
                    current_chunk = []
            
            if current_chunk:
                word_chunks.append(current_chunk)
            
            for i, chunk in enumerate(word_chunks):
                chunk_start = chunk[0]["start"]
                chunk_end = chunk[-1]["end"]
                chunk_text = " ".join([w["word"] for w in chunk])
                
                if CHUNK_CONFIG["silence_detection"]:
                    next_chunk_start = None
                    if i < len(word_chunks) - 1:
                        next_chunk_start = word_chunks[i + 1][0]["start"]
                    else:
                        next_chunk_start = end_time
                    
                    silence_gap = next_chunk_start - chunk_end
                    if silence_gap > CHUNK_CONFIG["min_silence_gap"]:
                        max_extend = min(CHUNK_CONFIG["max_silence_extend"], silence_gap * 0.3)
                        chunk_end = min(chunk_end + max_extend, next_chunk_start - 0.1)
                
                chunked_segments.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk_text
                })
        else:
            chunks = split_text_intelligently(text, CHUNK_CONFIG["max_words"])
            duration_per_chunk = (end_time - start_time) / len(chunks)
            
            for i, chunk in enumerate(chunks):
                chunk_start = start_time + (i * duration_per_chunk)
                chunk_end = start_time + ((i + 1) * duration_per_chunk)
                chunked_segments.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk
                })
    
    return chunked_segments

def transcribe_with_enhanced_audio(video_path):
    """Transcribe video con pre-procesamiento de audio avanzado"""
    print("🎯 INICIANDO TRANSCRIPCIÓN CON AUDIO MEJORADO")
    print("   📝 Máximo 3 palabras + Pre-procesamiento avanzado")
    print(f"📹 Video: {video_path}")
    
    # Configurar rutas
    video_name = Path(video_path).stem
    output_dir = Path(video_path).parent
    srt_path = output_dir / f"{video_name}_enhanced.srt"
    json_path = output_dir / f"{video_name}_enhanced.json"
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. Pre-procesar audio
        enhanced_audio = enhance_audio_quality(video_path, temp_path)
        if not enhanced_audio:
            print("❌ Error en pre-procesamiento de audio")
            return False
        
        print("🔄 Inicializando modelo Whisper...")
        try:
            # 2. Inicializar modelo faster-whisper
            model = WhisperModel(
                WHISPER_CONFIG["model"],
                device=WHISPER_CONFIG["device"],
                compute_type=WHISPER_CONFIG["compute_type"]
            )
            
            print("🔄 Ejecutando transcripción con audio mejorado...")
            
            # 3. Transcribir con audio mejorado
            segments, info = model.transcribe(
                str(enhanced_audio),
                language=WHISPER_CONFIG["language"],
                beam_size=WHISPER_CONFIG["beam_size"],
                best_of=WHISPER_CONFIG["best_of"],
                patience=WHISPER_CONFIG["patience"],
                length_penalty=WHISPER_CONFIG["length_penalty"],
                repetition_penalty=WHISPER_CONFIG["repetition_penalty"],
                no_repeat_ngram_size=WHISPER_CONFIG["no_repeat_ngram_size"],
                temperature=WHISPER_CONFIG["temperature"],
                compression_ratio_threshold=WHISPER_CONFIG["compression_ratio_threshold"],
                log_prob_threshold=WHISPER_CONFIG["log_prob_threshold"],
                no_speech_threshold=WHISPER_CONFIG["no_speech_threshold"],
                condition_on_previous_text=WHISPER_CONFIG["condition_on_previous_text"],
                prompt_reset_on_temperature=WHISPER_CONFIG["prompt_reset_on_temperature"],
                initial_prompt=WHISPER_CONFIG["initial_prompt"],
                word_timestamps=WHISPER_CONFIG["word_timestamps"],
                hallucination_silence_threshold=WHISPER_CONFIG["hallucination_silence_threshold"],
                vad_filter=True,
                vad_parameters=VAD_CONFIG
            )
            
            # 4. Convertir segmentos a lista CON timing de palabras
            segments_list = []
            for segment in segments:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": []
                }
                
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        segment_data["words"].append({
                            "word": word.word.strip(),
                            "start": word.start,
                            "end": word.end,
                            "probability": getattr(word, 'probability', 1.0)
                        })
                
                segments_list.append(segment_data)
            
            print(f"✅ Transcripción completada: {len(segments_list)} segmentos")
            print(f"🎯 Word timestamps: {sum(1 for s in segments_list if s.get('words', []))}/{len(segments_list)} segmentos")
            print(f"🎵 Audio mejorado aplicado exitosamente")
            
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return False
    
    print("📝 Aplicando chunking ultra-gradual con control de silencios...")
    
    try:
        # 5. Procesar segmentos con chunking usando timing preciso
        chunked_segments = process_segments_with_precise_timing(segments_list)
        
        # 6. Generar SRT con chunks
        srt_content = ""
        for i, segment in enumerate(chunked_segments, 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"]
            
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        
        # 7. Guardar SRT
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # 8. Guardar JSON procesado
        enhanced_result = {
            "segments": chunked_segments,
            "config": {
                "whisper": WHISPER_CONFIG,
                "vad": VAD_CONFIG,
                "chunking": CHUNK_CONFIG,
                "audio_enhancement": AUDIO_ENHANCEMENT_CONFIG
            },
            "stats": {
                "original_segments": len(segments_list),
                "chunked_segments": len(chunked_segments),
                "chunking_ratio": len(chunked_segments) / len(segments_list) if segments_list else 0,
                "audio_enhanced": True
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ TRANSCRIPCIÓN CON AUDIO MEJORADO COMPLETADA:")
        print(f"   📄 SRT: {srt_path}")
        print(f"   📊 JSON: {json_path}")
        print(f"   🧩 Segmentos originales: {len(segments_list)}")
        print(f"   🎯 Segmentos chunked: {len(chunked_segments)}")
        print(f"   📈 Ratio chunking: {len(chunked_segments) / len(segments_list):.1f}x")
        print(f"   📝 Máximo 3 palabras por subtítulo")
        print(f"   🔇 Control de silencios activado")
        print(f"   🎵 Pre-procesamiento de audio aplicado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando chunking: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python transcribe_enhanced.py video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Archivo no encontrado: {video_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎵 TRANSCRIPTOR CON AUDIO MEJORADO")
    print("   Pre-procesamiento avanzado + Chunking ultra-gradual")
    print("=" * 60)
    
    success = transcribe_with_enhanced_audio(video_path)
    
    if success:
        print("🎉 ¡TRANSCRIPCIÓN CON AUDIO MEJORADO EXITOSA!")
        print("🎵 El audio fue pre-procesado con técnicas avanzadas")
        print("📝 Subtítulos optimizados para máxima precisión")
    else:
        print("💥 Error en la transcripción")
        sys.exit(1)

if __name__ == "__main__":
    main()