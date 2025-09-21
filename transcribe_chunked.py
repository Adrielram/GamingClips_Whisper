#!/usr/bin/env python3
"""
TRANSCRIPCIÓN CON SEGMENTACIÓN ULTRA-GRADUAL
============================================

Soluciona el problema de subtítulos largos mostrando máximo 3 palabras
a la vez, creando una experiencia de lectura ultra-gradual y natural
perfectamente sincronizada con el audio.

Características:
- Máximo 3 palabras por subtítulo
- Segmentación inteligente por pausas naturales
- Distribución temporal proporcional
- Mantiene precisión de palabras lograda
- Lectura ultra-fluida y natural

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

# VAD optimizado para detectar silencios
VAD_CONFIG = {
    "threshold": 0.35,  # Más sensible para detectar silencios
    "min_speech_duration_ms": 200,
    "min_silence_duration_ms": 300,  # Detecta pausas de 300ms+
    "speech_pad_ms": 50
}

# Configuración de chunking
CHUNK_CONFIG = {
    "max_words": 3,  # Máximo 3 palabras por subtítulo
    "max_chars": 35,  # Máximo caracteres (reducido para 3 palabras)
    "min_chars": 5,   # Mínimo para evitar fragmentos muy cortos
    "max_duration": 2.5,  # Máximo segundos por subtítulo (reducido)
    "min_duration": 0.8,  # Mínimo duración (aumentado para sync)
    "natural_breaks": ['.', '!', '?', ',', ';', ':', ' y ', ' o ', ' pero ', ' aunque '],
    "prefer_breaks": ['.', '!', '?'],  # Preferir estos para cortar
    "word_distribution": True,  # Distribuir palabras temporalmente
    "sync_conservative": True,   # Modo conservador para mantener sincronización
    "silence_detection": True,   # Detectar y respetar silencios
    "min_silence_gap": 0.3,     # Mínimo silencio para crear pausa (300ms)
    "max_silence_extend": 0.5    # Máximo silencio a extender en subtítulo
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

def split_text_intelligently(text, max_words=3):
    """
    Divide texto de forma inteligente considerando:
    - Máximo 3 palabras por fragmento
    - Puntuación natural
    - Palabras completas
    - Flujo natural del habla
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]
    
    chunks = []
    current_chunk_words = []
    
    for word in words:
        current_chunk_words.append(word)
        
        # Si llegamos al máximo de palabras
        if len(current_chunk_words) >= max_words:
            chunk_text = " ".join(current_chunk_words)
            chunks.append(chunk_text)
            current_chunk_words = []
        
        # O si encontramos puntuación natural para cortar
        elif any(punct in word for punct in CHUNK_CONFIG["prefer_breaks"]):
            if len(current_chunk_words) >= 1:  # Al menos 1 palabra
                chunk_text = " ".join(current_chunk_words)
                chunks.append(chunk_text)
                current_chunk_words = []
    
    # Agregar último chunk si existe
    if current_chunk_words:
        chunk_text = " ".join(current_chunk_words)
        chunks.append(chunk_text)
    
    return chunks

def distribute_chunks_temporally(chunks, start_time, end_time):
    """
    Distribuye chunks de texto manteniendo sincronización perfecta
    Los chunks aparecen gradualmente pero respetando el timing original
    """
    if not chunks:
        return []
    
    total_duration = end_time - start_time
    segments = []
    
    # Para mantener sincronización, distribuir uniformemente
    # pero con overlap para que no aparezcan antes de tiempo
    chunk_duration = total_duration / len(chunks)
    
    # Asegurar duración mínima y máxima
    chunk_duration = max(CHUNK_CONFIG["min_duration"], 
                        min(CHUNK_CONFIG["max_duration"], chunk_duration))
    
    current_time = start_time
    for i, chunk in enumerate(chunks):
        # Para el último chunk, usar exactamente el tiempo final
        if i == len(chunks) - 1:
            chunk_end = end_time
        else:
            chunk_end = current_time + chunk_duration
            # No exceder el tiempo final
            chunk_end = min(chunk_end, end_time)
        
        # CLAVE: No adelantar el inicio, mantener timing natural
        # Los chunks posteriores pueden tener overlap controlado
        if i > 0:
            # Pequeño overlap para transición suave, pero no adelantar
            overlap = min(0.2, chunk_duration * 0.1)
            chunk_start = max(current_time - overlap, start_time)
        else:
            chunk_start = current_time
        
        segments.append({
            "start": chunk_start,
            "end": chunk_end,
            "text": chunk
        })
        
        # Avanzar tiempo para el siguiente chunk
        current_time = chunk_start + (chunk_duration * 0.9)  # 90% para overlap controlado
    
    return segments

def detect_silence_gaps(segments):
    """
    Detecta gaps de silencio entre segmentos
    """
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
    """
    Procesa segmentos usando timing preciso y respetando silencios
    """
    if not segments:
        return []
    
    # Detectar gaps de silencio
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
        
        # Si tenemos timing de palabras, usarlo para sincronización perfecta
        if words_timing and len(words_timing) > 0:
            # Agrupar palabras en chunks de máximo 3
            word_chunks = []
            current_chunk = []
            
            for word_info in words_timing:
                current_chunk.append(word_info)
                
                if len(current_chunk) >= CHUNK_CONFIG["max_words"]:
                    word_chunks.append(current_chunk)
                    current_chunk = []
            
            # Agregar último chunk si existe
            if current_chunk:
                word_chunks.append(current_chunk)
            
            # Crear segmentos con timing preciso Y control de silencios
            for i, chunk in enumerate(word_chunks):
                chunk_start = chunk[0]["start"]
                chunk_end = chunk[-1]["end"]
                chunk_text = " ".join([w["word"] for w in chunk])
                
                # CONTROL DE SILENCIOS: No extender subtítulos durante gaps largos
                if CHUNK_CONFIG["silence_detection"]:
                    # Verificar si hay gap de silencio después de este chunk
                    next_chunk_start = None
                    if i < len(word_chunks) - 1:
                        next_chunk_start = word_chunks[i + 1][0]["start"]
                    else:
                        # Es el último chunk del segmento
                        next_chunk_start = end_time
                    
                    # Si hay un gap grande, no extender el subtítulo
                    silence_gap = next_chunk_start - chunk_end
                    if silence_gap > CHUNK_CONFIG["min_silence_gap"]:
                        # Limitar la extensión del subtítulo
                        max_extend = min(CHUNK_CONFIG["max_silence_extend"], silence_gap * 0.3)
                        chunk_end = min(chunk_end + max_extend, next_chunk_start - 0.1)
                
                chunked_segments.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk_text
                })
        
        else:
            # Fallback: usar método anterior si no hay timing de palabras
            chunks = split_text_intelligently(text, CHUNK_CONFIG["max_words"])
            chunk_segments = distribute_chunks_temporally(chunks, start_time, end_time)
            chunked_segments.extend(chunk_segments)
    
    return chunked_segments

def transcribe_with_chunking(video_path):
    """Transcribe video con segmentación inteligente"""
    print("🎯 INICIANDO TRANSCRIPCIÓN CON CHUNKING ULTRA-GRADUAL")
    print("   📝 Máximo 3 palabras por subtítulo")
    print(f"📹 Video: {video_path}")
    
    # Configurar rutas
    video_name = Path(video_path).stem
    output_dir = Path(video_path).parent
    srt_path = output_dir / f"{video_name}_chunked.srt"
    json_path = output_dir / f"{video_name}_chunked.json"
    
    print("echo 🔄 Iniciando transcripción ultra-gradual con control de silencios...")
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
        
        # Convertir segmentos a lista CON timing de palabras
        segments_list = []
        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": []
            }
            
            # Capturar timing de palabras individuales si están disponibles
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    segment_data["words"].append({
                        "word": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "probability": getattr(word, 'probability', 1.0)
                    })
            
            segments_list.append(segment_data)
        
        print(f"✅ Transcripción base completada: {len(segments_list)} segmentos")
        print(f"🎯 Detectados word timestamps: {sum(1 for s in segments_list if s.get('words', []))}/{len(segments_list)} segmentos")
        
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return False
    
    print("📝 Aplicando chunking ultra-gradual con control de silencios...")
    
    try:
        # Procesar segmentos con chunking usando timing preciso
        chunked_segments = process_segments_with_precise_timing(segments_list)
        
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
        
        print(f"✅ CHUNKING ULTRA-GRADUAL CON CONTROL DE SILENCIOS COMPLETADO:")
        print(f"   📄 SRT: {srt_path}")
        print(f"   📊 JSON: {json_path}")
        print(f"   🧩 Segmentos originales: {len(segments_list)}")
        print(f"   🎯 Segmentos chunked: {len(chunked_segments)}")
        print(f"   📈 Ratio chunking: {len(chunked_segments) / len(segments_list):.1f}x")
        print(f"   📝 Máximo 3 palabras por subtítulo")
        print(f"   🔇 Control de silencios activado")
        
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
    print("🎯 TRANSCRIPTOR CON CHUNKING ULTRA-GRADUAL")
    print("   Máximo 3 palabras por subtítulo - Lectura ultra-fluida")
    print("=" * 60)
    
    success = transcribe_with_chunking(video_path)
    
    if success:
        print("🎉 ¡TRANSCRIPCIÓN ULTRA-GRADUAL EXITOSA!")
    else:
        print("💥 Error en la transcripción")
        sys.exit(1)

if __name__ == "__main__":
    main()