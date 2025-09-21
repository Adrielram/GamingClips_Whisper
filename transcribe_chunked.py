#!/usr/bin/env python3
"""
TRANSCRIPCIÓN CON SEGMENTACIÓN INTELIGENTE
==========================================

Soluciona el problema de subtítulos que muestran muchas palabras juntas
por mucho tiempo. Divide los subtítulos en fragmentos naturales que
aparecen gradualmente sincronizados con el audio.

Características:
- Segmentación inteligente por pausas naturales
- Máximo 40-50 caracteres por subtítulo
- Distribución temporal proporcional
- Mantiene precisión de palabras lograda
- Chunks basados en puntuación y ritmo del habla

Uso: python transcribe_chunked.py video.mp4
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from datetime import timedelta
from faster_whisper import WhisperModel

# Configuración optimizada para gaming argentino
WHISPER_CONFIG = {
    "model": "large-v3",
    "language": "es",
    "device": "cuda",
    "compute_type": "float16",
    "beam_size": 5,
    "best_of": 5,
    "patience": 1.5,
    "length_penalty": 1.0,
    "repetition_penalty": 1.05,
    "no_repeat_ngram_size": 3,
    "temperature": [0.0, 0.2, 0.4],
    "compression_ratio_threshold": 2.4,
    "log_prob_threshold": -0.8,
    "no_speech_threshold": 0.4,
    "condition_on_previous_text": True,
    "prompt_reset_on_temperature": 0.5,
    "initial_prompt": """Esto es una conversación en español argentino sobre videojuegos. Nombres comunes: Gabriel, Adriel, Estani, wilo, corcho, ruben, erizo. Expresiones típicas: "dale", "bueno", "che", "boludo", "posta", "zafar", "hinchar", "joder".""",
    "word_timestamps": True,
    "hallucination_silence_threshold": 2.0
}

# VAD optimizado para segmentación
VAD_CONFIG = {
    "threshold": 0.4,  # Más conservador para mejor segmentación
    "min_speech_duration_ms": 200,
    "min_silence_duration_ms": 100,  # Detecta pausas pequeñas
    "speech_pad_ms": 50
}

# Configuración de chunking
CHUNK_CONFIG = {
    "max_chars": 45,  # Máximo caracteres por subtítulo
    "min_chars": 15,  # Mínimo para evitar fragmentos muy cortos
    "max_duration": 4.0,  # Máximo segundos por subtítulo
    "min_duration": 0.8,  # Mínimo duración
    "natural_breaks": ['.', '!', '?', ',', ';', ':', ' y ', ' o ', ' pero ', ' aunque '],
    "prefer_breaks": ['.', '!', '?'],  # Preferir estos para cortar
    "word_distribution": True  # Distribuir palabras temporalmente
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

def split_text_intelligently(text, max_chars=45):
    """
    Divide texto de forma inteligente considerando:
    - Longitud máxima
    - Puntuación natural
    - Palabras completas
    - Flujo natural del habla
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    words = text.split()
    
    for word in words:
        # Probar agregar la palabra
        test_chunk = current_chunk + (" " if current_chunk else "") + word
        
        # Si excede el límite
        if len(test_chunk) > max_chars:
            # Si tenemos chunk actual, guardarlo
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                # Palabra muy larga, forzar división
                chunks.append(word)
                current_chunk = ""
        else:
            current_chunk = test_chunk
            
            # Verificar si hay puntuación natural para cortar
            if any(punct in word for punct in CHUNK_CONFIG["prefer_breaks"]):
                if len(current_chunk) >= CHUNK_CONFIG["min_chars"]:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
    
    # Agregar último chunk si existe
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def distribute_chunks_temporally(chunks, start_time, end_time):
    """
    Distribuye chunks de texto a lo largo del tiempo de forma proporcional
    """
    if not chunks:
        return []
    
    total_duration = end_time - start_time
    segments = []
    
    # Calcular duración por chunk basándose en longitud de texto
    total_chars = sum(len(chunk) for chunk in chunks)
    
    current_time = start_time
    for i, chunk in enumerate(chunks):
        # Duración proporcional al texto
        chunk_ratio = len(chunk) / total_chars if total_chars > 0 else 1.0 / len(chunks)
        chunk_duration = total_duration * chunk_ratio
        
        # Aplicar límites de duración
        chunk_duration = max(CHUNK_CONFIG["min_duration"], 
                           min(CHUNK_CONFIG["max_duration"], chunk_duration))
        
        # Para el último chunk, usar el tiempo restante
        if i == len(chunks) - 1:
            chunk_end = end_time
        else:
            chunk_end = current_time + chunk_duration
            # Asegurar que no exceda el final
            chunk_end = min(chunk_end, end_time)
        
        segments.append({
            "start": current_time,
            "end": chunk_end,
            "text": chunk
        })
        
        current_time = chunk_end
    
    return segments

def process_segments_with_chunking(segments):
    """
    Procesa segmentos aplicando chunking inteligente
    """
    chunked_segments = []
    
    for segment in segments:
        text = segment["text"].strip()
        if not text:
            continue
            
        start_time = segment["start"]
        end_time = segment["end"]
        
        # Dividir texto inteligentemente
        chunks = split_text_intelligently(text, CHUNK_CONFIG["max_chars"])
        
        # Distribuir chunks temporalmente
        if CHUNK_CONFIG["word_distribution"]:
            chunk_segments = distribute_chunks_temporally(chunks, start_time, end_time)
        else:
            # Distribución uniforme simple
            duration_per_chunk = (end_time - start_time) / len(chunks)
            chunk_segments = []
            for i, chunk in enumerate(chunks):
                chunk_start = start_time + (i * duration_per_chunk)
                chunk_end = start_time + ((i + 1) * duration_per_chunk)
                chunk_segments.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk
                })
        
        chunked_segments.extend(chunk_segments)
    
    return chunked_segments

def transcribe_with_chunking(video_path):
    """Transcribe video con segmentación inteligente"""
    print("🎯 INICIANDO TRANSCRIPCIÓN CON CHUNKING INTELIGENTE")
    print(f"📹 Video: {video_path}")
    
    # Configurar rutas
    video_name = Path(video_path).stem
    output_dir = Path(video_path).parent
    srt_path = output_dir / f"{video_name}_chunked.srt"
    json_path = output_dir / f"{video_name}_chunked.json"
    
    print("🔄 Inicializando modelo Whisper...")
    try:
        # Inicializar modelo faster-whisper
        model = WhisperModel(
            WHISPER_CONFIG["model"],
            device=WHISPER_CONFIG["device"],
            compute_type=WHISPER_CONFIG["compute_type"]
        )
        
        print("🔄 Ejecutando transcripción base...")
        
        # Transcribir con configuración optimizada
        segments, info = model.transcribe(
            str(video_path),
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
        
        # Convertir segmentos a lista
        segments_list = []
        for segment in segments:
            segments_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
        
        print(f"✅ Transcripción base completada: {len(segments_list)} segmentos")
        
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return False
    
    print("📝 Aplicando chunking inteligente...")
    
    try:
        # Procesar segmentos con chunking
        chunked_segments = process_segments_with_chunking(segments_list)
        
        # Generar SRT con chunks
        srt_content = ""
        for i, segment in enumerate(chunked_segments, 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"]
            
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        
        # Guardar SRT
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # Guardar JSON procesado
        chunked_result = {
            "segments": chunked_segments,
            "config": {
                "whisper": WHISPER_CONFIG,
                "vad": VAD_CONFIG,
                "chunking": CHUNK_CONFIG
            },
            "stats": {
                "original_segments": len(segments_list),
                "chunked_segments": len(chunked_segments),
                "chunking_ratio": len(chunked_segments) / len(segments_list) if segments_list else 0
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chunked_result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ CHUNKING COMPLETADO:")
        print(f"   📄 SRT: {srt_path}")
        print(f"   📊 JSON: {json_path}")
        print(f"   🧩 Segmentos originales: {len(segments_list)}")
        print(f"   🎯 Segmentos chunked: {len(chunked_segments)}")
        print(f"   📈 Ratio chunking: {len(chunked_segments) / len(segments_list):.1f}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando chunking: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python transcribe_chunked.py video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Archivo no encontrado: {video_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎯 TRANSCRIPTOR CON CHUNKING INTELIGENTE")
    print("   Segmenta subtítulos para mostrar palabras gradualmente")
    print("=" * 60)
    
    success = transcribe_with_chunking(video_path)
    
    if success:
        print("🎉 ¡TRANSCRIPCIÓN CON CHUNKING EXITOSA!")
    else:
        print("💥 Error en la transcripción")
        sys.exit(1)

if __name__ == "__main__":
    main()