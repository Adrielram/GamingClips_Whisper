#!/usr/bin/env python3
"""
TRANSCRIPCIÓN CON MÚLTIPLES PASADAS ADAPTATIVAS
===============================================

Script avanzado que realiza múltiples pasadas de transcripción con diferentes
configuraciones para maximizar la cobertura y precisión. Combina resultados
de pasadas conservadoras y agresivas para cubrir tiempos muertos y mejorar
la detección de speech en condiciones difíciles.

Características:
- Pasada 1: Conservadora (alta confianza, speech claro)
- Pasada 2: Agresiva (baja confianza, cubre tiempos muertos)
- Pasada 3: Ultra-agresiva (detecta susurros y speech muy bajo)
- Merge inteligente de resultados eliminando duplicados
- Priorización por confianza y consistencia
- Chunking ultra-gradual en resultado final

Uso: python transcribe_multipass.py video.mp4
"""

import os
import sys
import subprocess
import json
import tempfile
from pathlib import Path
from datetime import timedelta
from faster_whisper import WhisperModel
import numpy as np
from collections import defaultdict

# Configuraciones para diferentes pasadas
WHISPER_BASE_CONFIG = {
    "model": "large-v3",
    "language": "es",
    "device": "cuda",
    "compute_type": "float16",
    "initial_prompt": """Esto es una conversación en español argentino sobre videojuegos. Nombres comunes: Gabriel, Adriel, Estani, wilo, corcho, ruben, erizo. Expresiones típicas: "dale", "bueno", "che", "boludo", "posta", "zafar", "hinchar", "joder".""",
    "word_timestamps": True,
    "condition_on_previous_text": True
}

# PASADA 1: Conservadora - Alta confianza
CONSERVATIVE_CONFIG = {
    **WHISPER_BASE_CONFIG,
    "beam_size": 8,
    "best_of": 8,
    "patience": 2.0,
    "length_penalty": 1.2,
    "repetition_penalty": 1.1,
    "no_repeat_ngram_size": 4,
    "temperature": [0.0],  # Solo temperatura 0 para máxima determinismo
    "compression_ratio_threshold": 2.2,
    "log_prob_threshold": -0.6,  # Más estricto
    "no_speech_threshold": 0.6,  # Más conservador
    "hallucination_silence_threshold": 1.5,
    "vad_parameters": {
        "threshold": 0.5,  # Conservador
        "min_speech_duration_ms": 300,
        "min_silence_duration_ms": 500,
        "speech_pad_ms": 100
    }
}

# PASADA 2: Agresiva - Cubre tiempos muertos
AGGRESSIVE_CONFIG = {
    **WHISPER_BASE_CONFIG,
    "beam_size": 5,
    "best_of": 5,
    "patience": 1.5,
    "length_penalty": 1.0,
    "repetition_penalty": 1.05,
    "no_repeat_ngram_size": 3,
    "temperature": [0.0, 0.2, 0.4],
    "compression_ratio_threshold": 2.4,
    "log_prob_threshold": -0.8,  # Más permisivo
    "no_speech_threshold": 0.4,  # Más agresivo
    "hallucination_silence_threshold": 2.0,
    "vad_parameters": {
        "threshold": 0.35,  # Más sensible
        "min_speech_duration_ms": 150,
        "min_silence_duration_ms": 200,
        "speech_pad_ms": 150
    }
}

# PASADA 3: Ultra-agresiva - Detecta susurros
ULTRA_AGGRESSIVE_CONFIG = {
    **WHISPER_BASE_CONFIG,
    "beam_size": 3,
    "best_of": 3,
    "patience": 1.0,
    "length_penalty": 0.8,
    "repetition_penalty": 1.0,
    "no_repeat_ngram_size": 2,
    "temperature": [0.0, 0.2, 0.4, 0.6],
    "compression_ratio_threshold": 2.6,
    "log_prob_threshold": -1.0,  # Muy permisivo
    "no_speech_threshold": 0.3,  # Muy agresivo
    "hallucination_silence_threshold": 2.5,
    "vad_parameters": {
        "threshold": 0.25,  # Muy sensible
        "min_speech_duration_ms": 100,
        "min_silence_duration_ms": 100,
        "speech_pad_ms": 200
    }
}

# PASADA 4: Especializada en palabras cortas y exclamaciones
MICRO_SPEECH_CONFIG = {
    **WHISPER_BASE_CONFIG,
    "beam_size": 3,
    "best_of": 3,
    "patience": 0.8,
    "length_penalty": 0.5,  # Favorece segmentos cortos
    "repetition_penalty": 0.95,  # Permite más repeticiones
    "no_repeat_ngram_size": 2,
    "temperature": [0.0, 0.3, 0.6, 0.9],  # Más exploración
    "compression_ratio_threshold": 3.0,  # Más permisivo
    "log_prob_threshold": -1.2,  # Muy permisivo
    "no_speech_threshold": 0.2,  # Extremadamente agresivo
    "hallucination_silence_threshold": 3.0,
    "vad_parameters": {
        "threshold": 0.2,  # Extremadamente sensible
        "min_speech_duration_ms": 50,  # Detecta speech muy corto
        "min_silence_duration_ms": 50,
        "speech_pad_ms": 250
    }
}

# PASADA 5: Especializada en speech superpuesto y ruido
NOISE_ROBUST_CONFIG = {
    **WHISPER_BASE_CONFIG,
    "beam_size": 10,  # Más exploración
    "best_of": 10,
    "patience": 3.0,  # Muy paciente
    "length_penalty": 1.5,  # Favorece segmentos más largos
    "repetition_penalty": 1.2,  # Evita repeticiones en ruido
    "no_repeat_ngram_size": 5,
    "temperature": [0.1, 0.3],  # Temperaturas medias
    "compression_ratio_threshold": 2.0,  # Más estricto
    "log_prob_threshold": -0.9,
    "no_speech_threshold": 0.7,  # Conservador para evitar ruido
    "hallucination_silence_threshold": 1.0,  # Más estricto
    "vad_parameters": {
        "threshold": 0.45,  # Moderado
        "min_speech_duration_ms": 400,  # Segmentos más largos
        "min_silence_duration_ms": 300,
        "speech_pad_ms": 100
    }
}

# Configuración de chunking para resultado final
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

class MultipassConfig:
    """
    Configuración para transcripción multipass
    """
    
    def __init__(self, 
                 model_name="large-v3", 
                 device="cuda", 
                 compute_type="float16",
                 passes=["conservative", "aggressive", "ultra_aggressive"]):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.passes = passes
        
    def get_config_for_pass(self, pass_name):
        """Obtener configuración para una pasada específica"""
        if pass_name == "conservative":
            return CONSERVATIVE_CONFIG
        elif pass_name == "aggressive":
            return AGGRESSIVE_CONFIG
        elif pass_name == "ultra_aggressive":
            return ULTRA_AGGRESSIVE_CONFIG
        elif pass_name == "micro_speech":
            return MICRO_SPEECH_CONFIG
        elif pass_name == "noise_robust":
            return NOISE_ROBUST_CONFIG
        else:
            return CONSERVATIVE_CONFIG

class TranscriptionResult:
    """
    Resultado de transcripción multipass
    """
    
    def __init__(self, segments, metadata=None):
        self.segments = segments
        self.metadata = metadata or {}
        
    def to_text(self):
        """Convertir a texto plano"""
        return " ".join([seg['text'] for seg in self.segments])
    
    def to_srt(self):
        """Convertir a formato SRT"""
        srt_lines = []
        for i, seg in enumerate(self.segments, 1):
            start_time = self.format_srt_time(seg['start'])
            end_time = self.format_srt_time(seg['end'])
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(seg['text'])
            srt_lines.append("")
        return "\n".join(srt_lines)
    
    def format_srt_time(self, seconds):
        """Formatear tiempo para SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def format_timestamp(seconds):
    """Convierte segundos a formato SRT (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int((td.total_seconds() % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_with_config(model, audio_path, config, pass_name):
    """Realiza transcripción con configuración específica"""
    print(f"🔄 Ejecutando {pass_name}...")
    
    try:
        segments, info = model.transcribe(
            str(audio_path),
            language=config["language"],
            beam_size=config["beam_size"],
            best_of=config["best_of"],
            patience=config["patience"],
            length_penalty=config["length_penalty"],
            repetition_penalty=config["repetition_penalty"],
            no_repeat_ngram_size=config["no_repeat_ngram_size"],
            temperature=config["temperature"],
            compression_ratio_threshold=config["compression_ratio_threshold"],
            log_prob_threshold=config["log_prob_threshold"],
            no_speech_threshold=config["no_speech_threshold"],
            condition_on_previous_text=config["condition_on_previous_text"],
            initial_prompt=config["initial_prompt"],
            word_timestamps=config["word_timestamps"],
            hallucination_silence_threshold=config["hallucination_silence_threshold"],
            vad_filter=True,
            vad_parameters=config["vad_parameters"]
        )
        
        # Convertir a lista con información de confianza
        segments_list = []
        for segment in segments:
            avg_logprob = getattr(segment, 'avg_logprob', -1.0)
            no_speech_prob = getattr(segment, 'no_speech_prob', 0.0)
            
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "avg_logprob": avg_logprob,
                "no_speech_prob": no_speech_prob,
                "confidence": calculate_confidence(avg_logprob, no_speech_prob),
                "pass_source": pass_name,
                "words": []
            }
            
            # Capturar word timestamps si están disponibles
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    word_prob = getattr(word, 'probability', 1.0)
                    segment_data["words"].append({
                        "word": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "probability": word_prob
                    })
            
            segments_list.append(segment_data)
        
        print(f"✅ {pass_name} completada: {len(segments_list)} segmentos")
        return segments_list
        
    except Exception as e:
        print(f"❌ Error en {pass_name}: {e}")
        return []

def calculate_confidence(avg_logprob, no_speech_prob):
    """Calcula score de confianza combinado"""
    # Normalizar avg_logprob (típicamente -3.0 a 0.0)
    logprob_score = max(0, (avg_logprob + 3.0) / 3.0)
    
    # Invertir no_speech_prob (menos probabilidad de no-speech = más confianza)
    speech_score = 1.0 - no_speech_prob
    
    # Combinar scores
    confidence = (logprob_score * 0.7) + (speech_score * 0.3)
    return min(1.0, max(0.0, confidence))

def detect_overlaps(segments):
    """Detecta segmentos que se superponen temporalmente"""
    overlaps = []
    
    for i, seg1 in enumerate(segments):
        for j, seg2 in enumerate(segments[i+1:], i+1):
            # Verificar superposición temporal
            overlap_start = max(seg1["start"], seg2["start"])
            overlap_end = min(seg1["end"], seg2["end"])
            
            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                seg1_duration = seg1["end"] - seg1["start"]
                seg2_duration = seg2["end"] - seg2["start"]
                
                # Calcular porcentaje de superposición
                overlap_pct1 = overlap_duration / seg1_duration
                overlap_pct2 = overlap_duration / seg2_duration
                
                overlaps.append({
                    "seg1_idx": i,
                    "seg2_idx": j,
                    "overlap_start": overlap_start,
                    "overlap_end": overlap_end,
                    "overlap_duration": overlap_duration,
                    "overlap_pct1": overlap_pct1,
                    "overlap_pct2": overlap_pct2,
                    "seg1": seg1,
                    "seg2": seg2
                })
    
    return overlaps

def merge_multipass_results(conservative_segments, aggressive_segments, ultra_aggressive_segments):
    """Merge inteligente de resultados de múltiples pasadas"""
    print("🔄 Realizando merge inteligente de múltiples pasadas...")
    
    # Combinar todos los segmentos
    all_segments = []
    all_segments.extend(conservative_segments)
    all_segments.extend(aggressive_segments)
    all_segments.extend(ultra_aggressive_segments)
    
    # Ordenar por tiempo de inicio
    all_segments.sort(key=lambda x: x["start"])
    
    print(f"📊 Segmentos totales antes del merge: {len(all_segments)}")
    print(f"   • Conservadora: {len(conservative_segments)}")
    print(f"   • Agresiva: {len(aggressive_segments)}")
    print(f"   • Ultra-agresiva: {len(ultra_aggressive_segments)}")
    
    # Detectar superposiciones
    overlaps = detect_overlaps(all_segments)
    print(f"⚠️ Detectadas {len(overlaps)} superposiciones")
    
    # Resolver conflictos priorizando por confianza y fuente
    merged_segments = []
    used_indices = set()
    
    for i, segment in enumerate(all_segments):
        if i in used_indices:
            continue
            
        # Buscar segmentos superpuestos con este
        conflicting_segments = [segment]
        conflicting_indices = [i]
        
        for overlap in overlaps:
            if overlap["seg1_idx"] == i and overlap["seg2_idx"] not in used_indices:
                conflicting_segments.append(overlap["seg2"])
                conflicting_indices.append(overlap["seg2_idx"])
            elif overlap["seg2_idx"] == i and overlap["seg1_idx"] not in used_indices:
                conflicting_segments.append(overlap["seg1"])
                conflicting_indices.append(overlap["seg1_idx"])
        
        # Elegir el mejor segmento del grupo conflictivo
        best_segment = choose_best_segment(conflicting_segments)
        merged_segments.append(best_segment)
        
        # Marcar todos los índices como usados
        used_indices.update(conflicting_indices)
    
    # Agregar segmentos sin conflictos
    for i, segment in enumerate(all_segments):
        if i not in used_indices:
            merged_segments.append(segment)
    
    # Ordenar resultado final
    merged_segments.sort(key=lambda x: x["start"])
    
    print(f"✅ Merge completado: {len(merged_segments)} segmentos finales")
    return merged_segments

def choose_best_segment(conflicting_segments):
    """Elige el mejor segmento de un grupo conflictivo"""
    # Prioridades:
    # 1. Conservadora con alta confianza
    # 2. Agresiva con confianza decente
    # 3. Ultra-agresiva solo si las otras fallan
    
    conservative = [s for s in conflicting_segments if s["pass_source"] == "CONSERVADORA"]
    aggressive = [s for s in conflicting_segments if s["pass_source"] == "AGRESIVA"]
    ultra_aggressive = [s for s in conflicting_segments if s["pass_source"] == "ULTRA-AGRESIVA"]
    
    # Priorizar conservadora si tiene buena confianza
    if conservative:
        best_conservative = max(conservative, key=lambda x: x["confidence"])
        if best_conservative["confidence"] > 0.7:
            return best_conservative
    
    # Sino, usar agresiva si tiene confianza decente
    if aggressive:
        best_aggressive = max(aggressive, key=lambda x: x["confidence"])
        if best_aggressive["confidence"] > 0.5:
            return best_aggressive
    
    # Como último recurso, usar ultra-agresiva
    if ultra_aggressive:
        best_ultra = max(ultra_aggressive, key=lambda x: x["confidence"])
        return best_ultra
    
    # Fallback: el de mayor confianza general
    return max(conflicting_segments, key=lambda x: x["confidence"])

def fill_gaps_with_lower_confidence(merged_segments, all_segments, min_gap_duration=1.0):
    """Rellena gaps con segmentos de menor confianza"""
    print("🔄 Rellenando gaps con segmentos de menor confianza...")
    
    final_segments = []
    
    for i, segment in enumerate(merged_segments):
        final_segments.append(segment)
        
        # Verificar gap hasta el siguiente segmento
        if i < len(merged_segments) - 1:
            next_segment = merged_segments[i + 1]
            gap_start = segment["end"]
            gap_end = next_segment["start"]
            gap_duration = gap_end - gap_start
            
            if gap_duration >= min_gap_duration:
                # Buscar segmentos de menor confianza que puedan llenar este gap
                gap_fillers = []
                for other_seg in all_segments:
                    if (other_seg["start"] >= gap_start and 
                        other_seg["end"] <= gap_end and
                        other_seg not in merged_segments):
                        gap_fillers.append(other_seg)
                
                # Agregar los mejores gap fillers
                gap_fillers.sort(key=lambda x: x["confidence"], reverse=True)
                for filler in gap_fillers[:2]:  # Máximo 2 fillers por gap
                    if filler["confidence"] > 0.3:  # Umbral mínimo
                        final_segments.append(filler)
    
    # Reordenar por tiempo
    final_segments.sort(key=lambda x: x["start"])
    
    gaps_filled = len(final_segments) - len(merged_segments)
    print(f"✅ Se rellenaron {gaps_filled} gaps adicionales")
    
    return final_segments

def merge_multipass_results_v2(conservative_segments, aggressive_segments, ultra_aggressive_segments,
                               micro_speech_segments, noise_robust_segments):
    """Merge inteligente de resultados de 5 pasadas con priorización especializada"""
    print("Realizando merge inteligente de 5 pasadas...")
    
    # Combinar todos los segmentos
    all_segments = []
    all_segments.extend(conservative_segments)
    all_segments.extend(aggressive_segments)
    all_segments.extend(ultra_aggressive_segments)
    all_segments.extend(micro_speech_segments)
    all_segments.extend(noise_robust_segments)
    
    # Ordenar por tiempo de inicio
    all_segments.sort(key=lambda x: x["start"])
    
    print(f"Segmentos totales antes del merge: {len(all_segments)}")
    print(f"   • Conservadora: {len(conservative_segments)}")
    print(f"   • Agresiva: {len(aggressive_segments)}")
    print(f"   • Ultra-agresiva: {len(ultra_aggressive_segments)}")
    print(f"   • Micro-speech: {len(micro_speech_segments)}")
    print(f"   • Noise-robust: {len(noise_robust_segments)}")
    
    # Detectar superposiciones
    overlaps = detect_overlaps(all_segments)
    print(f"Detectadas {len(overlaps)} superposiciones")
    
    # Resolver conflictos con priorización especializada
    merged_segments = []
    used_indices = set()
    
    for i, segment in enumerate(all_segments):
        if i in used_indices:
            continue
            
        # Buscar segmentos superpuestos con este
        conflicting_segments = [segment]
        conflicting_indices = [i]
        
        for overlap in overlaps:
            if overlap["seg1_idx"] == i and overlap["seg2_idx"] not in used_indices:
                conflicting_segments.append(overlap["seg2"])
                conflicting_indices.append(overlap["seg2_idx"])
            elif overlap["seg2_idx"] == i and overlap["seg1_idx"] not in used_indices:
                conflicting_segments.append(overlap["seg1"])
                conflicting_indices.append(overlap["seg1_idx"])
        
        # Elegir el mejor segmento del grupo conflictivo
        best_segment = choose_best_segment_v2(conflicting_segments)
        merged_segments.append(best_segment)
        
        # Marcar todos los índices como usados
        used_indices.update(conflicting_indices)
    
    # Agregar segmentos sin conflictos
    for i, segment in enumerate(all_segments):
        if i not in used_indices:
            merged_segments.append(segment)
    
    # Ordenar resultado final
    merged_segments.sort(key=lambda x: x["start"])
    
    print(f"Merge completado: {len(merged_segments)} segmentos finales")
    return merged_segments

def choose_best_segment_v2(conflicting_segments):
    """Elige el mejor segmento de un grupo conflictivo con 5 pasadas"""
    # Nueva priorización especializada:
    # 1. Conservadora con alta confianza (>0.8)
    # 2. Noise-robust para speech largo y claro (>0.7)
    # 3. Agresiva con confianza decente (>0.6)
    # 4. Micro-speech para segmentos muy cortos (<1s) con confianza >0.5
    # 5. Ultra-agresiva como último recurso
    
    conservative = [s for s in conflicting_segments if s["pass_source"] == "CONSERVADORA"]
    aggressive = [s for s in conflicting_segments if s["pass_source"] == "AGRESIVA"]
    ultra_aggressive = [s for s in conflicting_segments if s["pass_source"] == "ULTRA-AGRESIVA"]
    micro_speech = [s for s in conflicting_segments if s["pass_source"] == "MICRO-SPEECH"]
    noise_robust = [s for s in conflicting_segments if s["pass_source"] == "NOISE-ROBUST"]
    
    # Prioridad 1: Conservadora con alta confianza
    if conservative:
        best_conservative = max(conservative, key=lambda x: x["confidence"])
        if best_conservative["confidence"] > 0.8:
            return best_conservative
    
    # Prioridad 2: Noise-robust para speech largo y claro
    if noise_robust:
        best_noise_robust = max(noise_robust, key=lambda x: x["confidence"])
        duration = best_noise_robust["end"] - best_noise_robust["start"]
        if best_noise_robust["confidence"] > 0.7 and duration > 1.0:
            return best_noise_robust
    
    # Prioridad 3: Agresiva con confianza decente
    if aggressive:
        best_aggressive = max(aggressive, key=lambda x: x["confidence"])
        if best_aggressive["confidence"] > 0.6:
            return best_aggressive
    
    # Prioridad 4: Micro-speech para segmentos muy cortos
    if micro_speech:
        best_micro = max(micro_speech, key=lambda x: x["confidence"])
        duration = best_micro["end"] - best_micro["start"]
        if best_micro["confidence"] > 0.5 and duration < 1.0:
            return best_micro
    
    # Prioridad 5: Ultra-agresiva como último recurso
    if ultra_aggressive:
        best_ultra = max(ultra_aggressive, key=lambda x: x["confidence"])
        if best_ultra["confidence"] > 0.4:
            return best_ultra
    
    # Fallback: el de mayor confianza general
    return max(conflicting_segments, key=lambda x: x["confidence"])

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

def process_segments_with_precise_timing(segments):
    """Procesa segmentos aplicando chunking ultra-gradual"""
    if not segments:
        return []
    
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
                
                chunked_segments.append({
                    "start": chunk_start,
                    "end": chunk_end,
                    "text": chunk_text,
                    "source_confidence": segment.get("confidence", 0.5),
                    "source_pass": segment.get("pass_source", "UNKNOWN")
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
                    "text": chunk,
                    "source_confidence": segment.get("confidence", 0.5),
                    "source_pass": segment.get("pass_source", "UNKNOWN")
                })
    
    return chunked_segments

def transcribe_multipass(video_path):
    """Transcribe video con múltiples pasadas adaptativas"""
    print("🎯 INICIANDO TRANSCRIPCIÓN MULTIPASS ADAPTATIVA")
    print("   📝 5 Pasadas + Merge inteligente + Chunking ultra-gradual")
    print(f"📹 Video: {video_path}")
    
    # Configurar rutas
    video_name = Path(video_path).stem
    output_dir = Path(video_path).parent
    srt_path = output_dir / f"{video_name}_multipass.srt"
    json_path = output_dir / f"{video_name}_multipass.json"
    
    print("🔄 Inicializando modelo Whisper...")
    try:
        # Inicializar modelo una vez
        model = WhisperModel(
            WHISPER_BASE_CONFIG["model"],
            device=WHISPER_BASE_CONFIG["device"],
            compute_type=WHISPER_BASE_CONFIG["compute_type"]
        )
        
        print("🎯 EJECUTANDO MÚLTIPLES PASADAS")
        print("=" * 50)
        
        # PASADA 1: Conservadora
        conservative_segments = transcribe_with_config(
            model, video_path, CONSERVATIVE_CONFIG, "CONSERVADORA"
        )
        
        # PASADA 2: Agresiva
        aggressive_segments = transcribe_with_config(
            model, video_path, AGGRESSIVE_CONFIG, "AGRESIVA"
        )
        
        # PASADA 3: Ultra-agresiva
        ultra_aggressive_segments = transcribe_with_config(
            model, video_path, ULTRA_AGGRESSIVE_CONFIG, "ULTRA-AGRESIVA"
        )
        
        # PASADA 4: Micro-speech
        micro_speech_segments = transcribe_with_config(
            model, video_path, MICRO_SPEECH_CONFIG, "MICRO-SPEECH"
        )
        
        # PASADA 5: Noise-robust
        noise_robust_segments = transcribe_with_config(
            model, video_path, NOISE_ROBUST_CONFIG, "NOISE-ROBUST"
        )
        
        print("=" * 50)
        
        # Merge inteligente de resultados
        merged_segments = merge_multipass_results_v2(
            conservative_segments, aggressive_segments, ultra_aggressive_segments,
            micro_speech_segments, noise_robust_segments
        )
        
        # Rellenar gaps con segmentos de menor confianza
        all_segments = (conservative_segments + aggressive_segments + ultra_aggressive_segments + 
                       micro_speech_segments + noise_robust_segments)
        final_segments = fill_gaps_with_lower_confidence(merged_segments, all_segments)
        
        print(f"✅ Multipass completado: {len(final_segments)} segmentos finales")
        
    except Exception as e:
        print(f"❌ Error en transcripción multipass: {e}")
        return False
    
    print("📝 Aplicando chunking ultra-gradual...")
    
    try:
        # Procesar con chunking
        chunked_segments = process_segments_with_precise_timing(final_segments)
        
        # Generar SRT
        srt_content = ""
        for i, segment in enumerate(chunked_segments, 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"]
            
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        
        # Guardar SRT
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        # Estadísticas por pasada
        pass_stats = {}
        for segment in final_segments:
            pass_name = segment.get("pass_source", "UNKNOWN")
            if pass_name not in pass_stats:
                pass_stats[pass_name] = {"count": 0, "avg_confidence": 0.0}
            pass_stats[pass_name]["count"] += 1
            pass_stats[pass_name]["avg_confidence"] += segment.get("confidence", 0.0)
        
        for pass_name, stats in pass_stats.items():
            if stats["count"] > 0:
                stats["avg_confidence"] /= stats["count"]
        
        # Guardar JSON con estadísticas detalladas
        multipass_result = {
            "segments": chunked_segments,
            "config": {
                "conservative": CONSERVATIVE_CONFIG,
                "aggressive": AGGRESSIVE_CONFIG,
                "ultra_aggressive": ULTRA_AGGRESSIVE_CONFIG,
                "micro_speech": MICRO_SPEECH_CONFIG,
                "noise_robust": NOISE_ROBUST_CONFIG,
                "chunking": CHUNK_CONFIG
            },
            "stats": {
                "total_segments": len(final_segments),
                "chunked_segments": len(chunked_segments),
                "chunking_ratio": len(chunked_segments) / len(final_segments) if final_segments else 0,
                "pass_contributions": pass_stats,
                "multipass_enabled": True
            }
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(multipass_result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ TRANSCRIPCIÓN MULTIPASS COMPLETADA:")
        print(f"   📄 SRT: {srt_path}")
        print(f"   📊 JSON: {json_path}")
        print(f"   🎯 Segmentos finales: {len(final_segments)}")
        print(f"   🧩 Segmentos chunked: {len(chunked_segments)}")
        print(f"   📈 Ratio chunking: {len(chunked_segments) / len(final_segments):.1f}x")
        print(f"   📝 Máximo 3 palabras por subtítulo")
        
        # Mostrar contribución por pasada
        print(f"   📊 Contribución por pasada:")
        for pass_name, stats in pass_stats.items():
            conf_avg = stats["avg_confidence"]
            print(f"      • {pass_name}: {stats['count']} segs (conf: {conf_avg:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando multipass: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("❌ Uso: python transcribe_multipass.py video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"❌ Archivo no encontrado: {video_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("🎯 TRANSCRIPTOR MULTIPASS ADAPTATIVO")
    print("   3 Pasadas + Merge inteligente + Chunking ultra-gradual")
    print("=" * 60)
    
    success = transcribe_multipass(video_path)
    
    if success:
        print("🎉 ¡TRANSCRIPCIÓN MULTIPASS EXITOSA!")
        print("🎯 Máxima cobertura con múltiples estrategias")
        print("📝 Subtítulos optimizados de 3 palabras")
        print("🧠 Merge inteligente aplicado")
    else:
        print("💥 Error en la transcripción multipass")
        sys.exit(1)

class MultipassTranscriber:
    """
    Clase para transcripción multipass compatible con sistema avanzado
    """
    
    def __init__(self, model_name="large-v3", device="cuda", compute_type="float16"):
        """Inicializar transcriptor multipass"""
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
    def load_model(self):
        """Cargar modelo Whisper"""
        if self.model is None:
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
    
    def transcribe_file(self, audio_path, config_name="conservative"):
        """
        Transcribir archivo usando configuración específica
        
        Args:
            audio_path: Ruta al archivo de audio
            config_name: Nombre de configuración (conservative, aggressive, ultra_aggressive)
            
        Returns:
            Lista de segmentos transcriptos
        """
        self.load_model()
        
        # Seleccionar configuración
        if config_name == "conservative":
            config = CONSERVATIVE_CONFIG
        elif config_name == "aggressive":
            config = AGGRESSIVE_CONFIG
        elif config_name == "ultra_aggressive":
            config = ULTRA_AGGRESSIVE_CONFIG
        else:
            config = CONSERVATIVE_CONFIG
        
        # Ejecutar transcripción
        # Filtrar parámetros que no son para transcribe()
        transcribe_params = {k: v for k, v in config.items() 
                           if k not in ['model', 'device', 'compute_type']}
        
        segments, info = self.model.transcribe(audio_path, **transcribe_params)
        
        # Convertir a lista
        result_segments = []
        for segment in segments:
            result_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip(),
                'confidence': getattr(segment, 'avg_logprob', 0.0),
                'config': config_name
            })
        
        return result_segments
    
    def multipass_transcribe(self, audio_path, output_path=None):
        """
        Ejecutar transcripción multipass completa
        
        Args:
            audio_path: Ruta al archivo de audio
            output_path: Ruta de salida (opcional)
            
        Returns:
            Segmentos finales fusionados
        """
        print("🚀 Iniciando transcripción multipass...")
        
        # Ejecutar todas las pasadas (5 en total)
        conservative_segments = transcribe_with_config(self.model, audio_path, CONSERVATIVE_CONFIG, "CONSERVADORA")
        aggressive_segments = transcribe_with_config(self.model, audio_path, AGGRESSIVE_CONFIG, "AGRESIVA") 
        ultra_segments = transcribe_with_config(self.model, audio_path, ULTRA_AGGRESSIVE_CONFIG, "ULTRA-AGRESIVA")
        micro_speech_segments = transcribe_with_config(self.model, audio_path, MICRO_SPEECH_CONFIG, "MICRO-SPEECH")
        noise_robust_segments = transcribe_with_config(self.model, audio_path, NOISE_ROBUST_CONFIG, "NOISE-ROBUST")
        
        print(f"📊 Conservadora: {len(conservative_segments)} segmentos")
        print(f"📊 Agresiva: {len(aggressive_segments)} segmentos")
        print(f"📊 Ultra-agresiva: {len(ultra_segments)} segmentos")
        print(f"📊 Micro-speech: {len(micro_speech_segments)} segmentos")
        print(f"📊 Noise-robust: {len(noise_robust_segments)} segmentos")
        
        # Fusionar resultados de las 5 pasadas
        final_segments = merge_multipass_results_v2(
            conservative_segments,
            aggressive_segments, 
            ultra_segments,
            micro_speech_segments,
            noise_robust_segments
        )
        
        print(f"📊 Final: {len(final_segments)} segmentos")
        
        # Guardar si se especifica salida
        if output_path:
            self._save_segments_to_file(final_segments, output_path)
        
        return final_segments
    
    def _save_segments_to_file(self, segments, output_path):
        """Guardar segmentos a archivo"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for segment in segments:
                f.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}\n")

if __name__ == "__main__":
    main()