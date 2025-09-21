#!/usr/bin/env python3
"""
🚀 Transcripción Avanzada con VAD Híbrido y Contextual
======================================================

Sistema de transcripción de última generación que combina:
- VAD Híbrido (Silero v6.0 + PyAnnote + WebRTC)
- Análisis Contextual Gaming
- Sistema Multipass avanzado
- Aprendizaje Adaptativo
- Optimizaciones específicas para gaming

Características principales:
- Detección inteligente de speech con contexto gaming
- Transcripción multipass con VAD adaptativo
- Aprendizaje de patrones de usuario
- Compatibilidad backward con sistema existente
- Configuración automática basada en contenido

Autor: GameClipping Team
Fecha: Septiembre 2025
Versión: 2.0
"""

import numpy as np
import torch
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
import json
import time
import argparse
from datetime import datetime

# Imports del sistema existente
from transcribe_multipass import (
    MultipassTranscriber, MultipassConfig, 
    TranscriptionResult, merge_multipass_results_v2
)

# Imports del nuevo sistema VAD
from vad_hybrid import HybridVAD, HybridVADConfig, VADResult, create_gaming_vad_config
from vad_contextual import ContextualVAD, GamingContext, GamingContextResult

# Audio processing
try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Librosa/soundfile no disponible. Install: pip install librosa soundfile")

@dataclass
class SimpleTranscriptionSegment:
    """Segmento simple de transcripción para uso interno"""
    text: str
    start_time: float
    end_time: float
    confidence: float = 0.8
    language: str = "es"
    model_name: str = "whisper"

@dataclass
class AdvancedTranscriptionConfig:
    """Configuración para transcripción avanzada con VAD"""
    
    # Configuración VAD
    enable_hybrid_vad: bool = True
    enable_contextual_analysis: bool = True
    vad_preprocessing: bool = True  # Pre-filtrar audio con VAD antes de transcripción
    
    # Configuración multipass
    enable_multipass: bool = True
    multipass_passes: List[str] = None  # None = usar todas las configuraciones
    
    # Configuración Whisper
    whisper_model: str = "large-v3"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "es"
    
    # Configuración contextual
    enable_adaptive_learning: bool = True
    user_id: str = "default_user"
    save_learning_data: bool = True
    
    # Audio preprocessing
    enable_noise_reduction: bool = True
    normalize_audio: bool = True
    apply_high_pass_filter: bool = True
    high_pass_cutoff: float = 80.0  # Hz
    
    # Optimizaciones gaming
    gaming_mode: bool = True
    detect_game_events: bool = True
    prioritize_voice_chat: bool = True
    suppress_game_audio: bool = True
    
    # Output configuration
    include_vad_info: bool = True
    include_context_info: bool = True
    include_confidence_scores: bool = True
    export_detailed_results: bool = False
    
    # Performance
    parallel_processing: bool = True
    chunk_processing: bool = True
    chunk_duration: float = 30.0  # Procesar en chunks de 30s
    
    # Paths
    model_cache_dir: str = "models_cache"
    output_dir: str = "output"
    temp_dir: str = "temp"

@dataclass 
class AdvancedTranscriptionResult:
    """Resultado completo de transcripción avanzada"""
    
    # Transcripción principal
    transcription: str
    segments: List[TranscriptionResult]
    
    # Información VAD
    vad_segments: List[VADResult]
    speech_ratio: float  # Ratio de speech vs silencio
    
    # Información contextual
    gaming_contexts: List[GamingContextResult]
    dominant_context: GamingContext
    context_confidence: float
    
    # Métricas de calidad
    overall_confidence: float
    processing_time: float
    audio_quality_score: float
    
    # Metadatos
    audio_duration: float
    model_used: str
    vad_models_used: List[str]
    timestamp: datetime
    user_id: str
    
    # Configuraciones aplicadas
    final_vad_config: Dict[str, Any]
    multipass_config: Dict[str, Any]

class AdvancedTranscriber:
    """
    🚀 Transcriptor Avanzado con VAD Híbrido y Contextual
    
    Combina lo mejor de ambos mundos:
    - Sistema multipass existente para máxima precisión
    - VAD híbrido para detección inteligente de speech
    - Análisis contextual para adaptación automática
    - Aprendizaje continuo para mejora personalizada
    """
    
    def __init__(self, config: AdvancedTranscriptionConfig = None):
        self.config = config or AdvancedTranscriptionConfig()
        
        # Crear directorios necesarios
        for directory in [self.config.model_cache_dir, self.config.output_dir, self.config.temp_dir]:
            Path(directory).mkdir(exist_ok=True)
        
        # Inicializar componentes
        self.multipass_transcriber = None
        self.hybrid_vad = None
        self.contextual_vad = None
        
        # Estadísticas y métricas
        self.processing_stats = {
            'total_files_processed': 0,
            'total_processing_time': 0,
            'average_speech_ratio': 0,
            'context_distribution': {},
            'vad_accuracy_feedback': []
        }
        
        print(f"Inicializando Transcriptor Avanzado...")
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa todos los componentes del sistema"""
        
        # 1. Inicializar sistema multipass existente
        if self.config.enable_multipass:
            print("🔵 Inicializando sistema multipass...")
            self.multipass_transcriber = MultipassTranscriber(
                model_name=self.config.whisper_model,
                device=self.config.device,
                compute_type=self.config.compute_type
            )
            print("✅ Sistema multipass listo")
        
        # 2. Inicializar VAD híbrido
        if self.config.enable_hybrid_vad:
            print("🟡 Inicializando VAD híbrido...")
            vad_config = create_gaming_vad_config()
            self.hybrid_vad = HybridVAD(vad_config)
            print("✅ VAD híbrido listo")
        
        # 3. Inicializar VAD contextual
        if self.config.enable_contextual_analysis:
            print("🟢 Inicializando VAD contextual...")
            self.contextual_vad = ContextualVAD(
                user_id=self.config.user_id,
                model_path=self.config.model_cache_dir
            )
            print("✅ VAD contextual listo")
        
        print("🎯 Transcriptor Avanzado inicializado completamente")
    
    def transcribe_file(self, audio_file: str, output_file: str = None) -> AdvancedTranscriptionResult:
        """
        🎤 Transcribe un archivo de audio con análisis avanzado
        
        Args:
            audio_file: Ruta al archivo de audio
            output_file: Ruta de salida opcional
            
        Returns:
            AdvancedTranscriptionResult con toda la información
        """
        start_time = time.time()
        audio_path = Path(audio_file)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_file}")
        
        print(f"🎤 Transcribiendo: {audio_path.name}")
        print("=" * 60)
        
        # 1. Cargar y preprocesar audio
        audio_data, sample_rate, duration = self._load_and_preprocess_audio(audio_file)
        
        # 2. Análisis VAD y contextual (si están habilitados)
        vad_results, context_results = self._analyze_audio_content(audio_data, sample_rate)
        
        # 3. Preprocesamiento con VAD (opcional)
        if self.config.vad_preprocessing and vad_results:
            audio_data = self._preprocess_with_vad(audio_data, vad_results, sample_rate)
        
        # 4. Transcripción principal (multipass o simple)
        transcription_segments = self._perform_transcription(audio_data, sample_rate, context_results)
        
        # 5. Post-procesamiento y mejoras
        enhanced_segments = self._enhance_transcription_results(transcription_segments, vad_results, context_results)
        
        # 6. Generar resultado final
        final_result = self._create_final_result(
            enhanced_segments, vad_results, context_results,
            duration, start_time, audio_file
        )
        
        # 7. Guardar resultados si se especifica
        if output_file:
            self._save_results(final_result, output_file)
        
        # 8. Actualizar estadísticas y aprendizaje
        self._update_learning_data(final_result)
        
        processing_time = time.time() - start_time
        print(f"⚡ Transcripción completada en {processing_time:.2f}s")
        print(f"📝 Transcripción: {len(final_result.transcription)} caracteres")
        print(f"🎯 Contexto dominante: {final_result.dominant_context.value}")
        print(f"📊 Ratio de speech: {final_result.speech_ratio:.2f}")
        
        return final_result
    
    def _load_and_preprocess_audio(self, audio_file: str) -> Tuple[np.ndarray, int, float]:
        """Carga y preprocesa el archivo de audio"""
        
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Librosa no disponible para cargar audio")
        
        print("📁 Cargando audio...")
        
        # Cargar audio con librosa
        audio, sample_rate = librosa.load(audio_file, sr=16000)  # Estandarizar a 16kHz
        duration = len(audio) / sample_rate
        
        print(f"   Duración: {duration:.2f}s")
        print(f"   Sample rate: {sample_rate}Hz")
        print(f"   Samples: {len(audio)}")
        
        # Preprocesamiento opcional
        if self.config.normalize_audio:
            # Normalizar audio
            audio = librosa.util.normalize(audio)
            print("   ✅ Audio normalizado")
        
        if self.config.apply_high_pass_filter:
            # Aplicar filtro pasa-altos para eliminar ruido de baja frecuencia
            from scipy.signal import butter, filtfilt
            nyquist = sample_rate / 2
            cutoff_normalized = self.config.high_pass_cutoff / nyquist
            if cutoff_normalized < 1.0:
                b, a = butter(4, cutoff_normalized, btype='high')
                audio = filtfilt(b, a, audio)
                print(f"   ✅ Filtro pasa-altos aplicado ({self.config.high_pass_cutoff}Hz)")
        
        return audio, sample_rate, duration
    
    def _analyze_audio_content(self, audio: np.ndarray, sample_rate: int) -> Tuple[List[VADResult], List[GamingContextResult]]:
        """Analiza el contenido del audio con VAD y contexto"""
        
        vad_results = []
        context_results = []
        
        # Análisis VAD híbrido
        if self.hybrid_vad:
            print("🔍 Ejecutando análisis VAD híbrido...")
            vad_results = self.hybrid_vad.detect_speech_activity(audio, sample_rate)
            print(f"   Detectados {len(vad_results)} segmentos de speech")
        
        # Análisis contextual
        if self.contextual_vad:
            print("🧠 Ejecutando análisis contextual...")
            
            # Procesar en chunks para análisis contextual detallado
            chunk_duration = 10.0  # 10 segundos por chunk para análisis contextual
            chunk_samples = int(chunk_duration * sample_rate)
            
            for i in range(0, len(audio), chunk_samples):
                chunk = audio[i:i+chunk_samples]
                if len(chunk) < sample_rate:  # Skip chunks muy pequeños
                    continue
                
                chunk_start_time = i / sample_rate
                
                # Análizar chunk con VAD contextual
                chunk_vad_results, chunk_context = self.contextual_vad.analyze_speech_with_context(chunk, sample_rate)
                
                # Ajustar timestamps
                chunk_context.timestamp = chunk_start_time
                context_results.append(chunk_context)
                
                # Opcional: combinar resultados VAD si no se usa híbrido
                if not self.hybrid_vad:
                    for vad_result in chunk_vad_results:
                        vad_result.start_time += chunk_start_time
                        vad_result.end_time += chunk_start_time
                        vad_results.append(vad_result)
            
            print(f"   Analizados {len(context_results)} chunks contextuales")
        
        return vad_results, context_results
    
    def _preprocess_with_vad(self, audio: np.ndarray, vad_results: List[VADResult], sample_rate: int) -> np.ndarray:
        """Preprocesa el audio usando resultados VAD para optimizar transcripción"""
        
        if not vad_results:
            return audio
        
        print("🎛️ Aplicando preprocesamiento VAD...")
        
        # Crear máscara de speech
        speech_mask = np.zeros(len(audio), dtype=bool)
        
        for vad_result in vad_results:
            start_idx = int(vad_result.start_time * sample_rate)
            end_idx = int(vad_result.end_time * sample_rate)
            
            # Asegurar índices válidos
            start_idx = max(0, start_idx)
            end_idx = min(len(audio), end_idx)
            
            speech_mask[start_idx:end_idx] = True
        
        # Expandir regiones de speech con padding
        padding_samples = int(0.1 * sample_rate)  # 100ms padding
        
        # Dilatar máscara
        from scipy.ndimage import binary_dilation
        structure = np.ones(padding_samples * 2)
        speech_mask_expanded = binary_dilation(speech_mask, structure=structure)
        
        # Aplicar máscara con suavizado en los bordes
        processed_audio = audio.copy()
        
        # Atenuar regiones no-speech en lugar de eliminarlas completamente
        non_speech_mask = ~speech_mask_expanded
        processed_audio[non_speech_mask] *= 0.1  # Atenuar a 10%
        
        speech_ratio = np.sum(speech_mask) / len(speech_mask)
        print(f"   Ratio de speech detectado: {speech_ratio:.2f}")
        
        return processed_audio
    
    def _perform_transcription(self, audio: np.ndarray, sample_rate: int, context_results: List[GamingContextResult]) -> List[TranscriptionResult]:
        """Ejecuta la transcripción principal usando el mejor método disponible"""
        
        if self.config.enable_multipass and self.multipass_transcriber:
            return self._multipass_transcription(audio, sample_rate, context_results)
        else:
            return self._simple_transcription(audio, sample_rate, context_results)
    
    def _multipass_transcription(self, audio: np.ndarray, sample_rate: int, context_results: List[GamingContextResult]) -> List[TranscriptionResult]:
        """Transcripción multipass con adaptación contextual"""
        
        print("🔄 Ejecutando transcripción multipass adaptativa...")
        
        # Adaptar configuración multipass basada en contexto
        adapted_config = self._adapt_multipass_config(context_results)
        
        # Guardar audio temporal para multipass
        temp_audio_path = Path(self.config.temp_dir) / f"temp_audio_{int(time.time())}.wav"
        
        try:
            sf.write(temp_audio_path, audio, sample_rate)
            
            # Ejecutar transcripción multipass
            dict_results = self.multipass_transcriber.multipass_transcribe(str(temp_audio_path))
            
            # Convertir diccionarios a objetos SimpleTranscriptionSegment
            results = []
            for segment_dict in dict_results:
                result = SimpleTranscriptionSegment(
                    text=segment_dict.get("text", "").strip(),
                    start_time=segment_dict.get("start", 0.0),
                    end_time=segment_dict.get("end", 0.0),
                    confidence=segment_dict.get("confidence", 0.8),
                    language="es",
                    model_name="multipass"
                )
                results.append(result)
            
            return results
            
        finally:
            # Limpiar archivo temporal
            if temp_audio_path.exists():
                temp_audio_path.unlink()
    
    def _simple_transcription(self, audio: np.ndarray, sample_rate: int, context_results: List[GamingContextResult]) -> List[SimpleTranscriptionSegment]:
        """Transcripción simple usando faster-whisper directamente"""
        
        print("🎯 Ejecutando transcripción simple...")
        
        # Implementación básica con faster-whisper
        try:
            from faster_whisper import WhisperModel
            
            # Inicializar modelo
            model = WhisperModel("medium", device="cpu")
            
            # Guardar audio temporal
            temp_audio_path = Path(self.config.temp_dir) / f"temp_audio_{int(time.time())}.wav"
            sf.write(temp_audio_path, audio, sample_rate)
            
            try:
                # Transcribir
                segments, info = model.transcribe(str(temp_audio_path), language="es")
                
                # Convertir a formato SimpleTranscriptionSegment
                results = []
                for segment in segments:
                    result = SimpleTranscriptionSegment(
                        text=segment.text.strip(),
                        start_time=segment.start,
                        end_time=segment.end,
                        confidence=getattr(segment, 'avg_logprob', 0.8),
                        language=info.language,
                        model_name="medium_simple"
                    )
                    results.append(result)
                
                return results
                
            finally:
                if temp_audio_path.exists():
                    temp_audio_path.unlink()
                
        except ImportError:
            print("⚠️ faster-whisper no disponible")
            return []
    
    def _adapt_multipass_config(self, context_results: List[GamingContextResult]) -> MultipassConfig:
        """Adapta la configuración multipass basada en el contexto gaming"""
        
        # Crear configuración base
        config = MultipassConfig()
        
        if not context_results:
            return config
        
        # Analizar contextos dominantes
        context_counts = {}
        for context_result in context_results:
            context_type = context_result.context_type
            context_counts[context_type] = context_counts.get(context_type, 0) + 1
        
        dominant_context = max(context_counts, key=context_counts.get) if context_counts else GamingContext.UNKNOWN
        
        print(f"🎮 Adaptando multipass para contexto: {dominant_context.value}")
        
        # Adaptaciones específicas por contexto
        if dominant_context == GamingContext.COMBAT:
            # En combate: priorizar velocidad y sensibilidad
            config.enable_ultra_aggressive = True
            config.enable_micro_speech = True
            config.conservative_weight = 0.15
            config.aggressive_weight = 0.25
            config.ultra_aggressive_weight = 0.35
            config.micro_speech_weight = 0.25
            
        elif dominant_context == GamingContext.DIALOGUE:
            # En diálogos: priorizar precisión
            config.enable_conservative = True
            config.enable_aggressive = True
            config.conservative_weight = 0.4
            config.aggressive_weight = 0.4
            config.ultra_aggressive_weight = 0.1
            config.micro_speech_weight = 0.1
            
        elif dominant_context == GamingContext.MULTIPLAYER:
            # Multijugador: balance entre velocidad y precisión
            config.enable_all_passes = True
            config.enable_noise_robust = True
            config.noise_robust_weight = 0.3
            
        return config
    
    def _enhance_transcription_results(self, segments: List[TranscriptionResult], vad_results: List[VADResult], context_results: List[GamingContextResult]) -> List[TranscriptionResult]:
        """Mejora los resultados de transcripción con información VAD y contextual"""
        
        if not segments:
            return segments
        
        print("✨ Mejorando resultados con información contextual...")
        
        enhanced_segments = []
        
        for segment in segments:
            enhanced_segment = segment
            
            # Encontrar VAD results correspondientes
            corresponding_vad = [
                vad for vad in vad_results 
                if self._segments_overlap(segment.start_time, segment.end_time, vad.start_time, vad.end_time)
            ]
            
            # Encontrar contexto correspondiente
            corresponding_context = None
            for context in context_results:
                context_start = context.timestamp
                context_end = context.timestamp + 10.0  # Chunks de 10s
                if self._segments_overlap(segment.start_time, segment.end_time, context_start, context_end):
                    corresponding_context = context
                    break
            
            # Ajustar confianza basada en VAD
            if corresponding_vad:
                avg_vad_confidence = np.mean([vad.confidence for vad in corresponding_vad])
                # Combinar confianza de transcripción con VAD
                enhanced_segment.confidence = (segment.confidence + avg_vad_confidence) / 2
            
            # Añadir información contextual si está disponible
            if self.config.include_context_info and corresponding_context:
                if not hasattr(enhanced_segment, 'context_info'):
                    enhanced_segment.context_info = {}
                
                enhanced_segment.context_info.update({
                    'gaming_context': corresponding_context.context_type.value,
                    'context_confidence': corresponding_context.confidence,
                    'vad_segments': len(corresponding_vad)
                })
            
            enhanced_segments.append(enhanced_segment)
        
        return enhanced_segments
    
    def _segments_overlap(self, start1: float, end1: float, start2: float, end2: float) -> bool:
        """Verifica si dos segmentos temporales se superponen"""
        return not (end1 < start2 or end2 < start1)
    
    def _create_final_result(self, segments: List[TranscriptionResult], vad_results: List[VADResult], 
                           context_results: List[GamingContextResult], duration: float, 
                           start_time: float, audio_file: str) -> AdvancedTranscriptionResult:
        """Crea el resultado final combinando toda la información"""
        
        # Transcripción completa
        full_transcription = " ".join([seg.text for seg in segments])
        
        # Calcular ratio de speech
        total_speech_duration = sum([vad.end_time - vad.start_time for vad in vad_results])
        speech_ratio = total_speech_duration / duration if duration > 0 else 0
        
        # Contexto dominante
        if context_results:
            context_counts = {}
            for context in context_results:
                ctx = context.context_type
                context_counts[ctx] = context_counts.get(ctx, 0) + 1
            dominant_context = max(context_counts, key=context_counts.get)
            context_confidence = np.mean([ctx.confidence for ctx in context_results])
        else:
            dominant_context = GamingContext.UNKNOWN
            context_confidence = 0.0
        
        # Confianza general
        if segments:
            overall_confidence = np.mean([seg.confidence for seg in segments])
        else:
            overall_confidence = 0.0
        
        # Calidad de audio (simplificada)
        audio_quality_score = min(1.0, speech_ratio * 2)  # Heurística simple
        
        # Modelos utilizados
        vad_models_used = []
        if self.hybrid_vad:
            vad_models_used.extend(list(self.hybrid_vad.models.keys()))
        
        model_used = segments[0].model_name if segments else "unknown"
        
        # Configuraciones finales
        final_vad_config = {}
        if self.hybrid_vad:
            final_vad_config = asdict(self.hybrid_vad.config)
        
        multipass_config = {}
        if self.multipass_transcriber:
            multipass_config = {
                "model_name": self.multipass_transcriber.model_name,
                "device": self.multipass_transcriber.device,
                "compute_type": self.multipass_transcriber.compute_type
            }
        
        return AdvancedTranscriptionResult(
            transcription=full_transcription,
            segments=segments,
            vad_segments=vad_results,
            speech_ratio=speech_ratio,
            gaming_contexts=context_results,
            dominant_context=dominant_context,
            context_confidence=context_confidence,
            overall_confidence=overall_confidence,
            processing_time=time.time() - start_time,
            audio_quality_score=audio_quality_score,
            audio_duration=duration,
            model_used=model_used,
            vad_models_used=vad_models_used,
            timestamp=datetime.now(),
            user_id=self.config.user_id,
            final_vad_config=final_vad_config,
            multipass_config=multipass_config
        )
    
    def _save_results(self, result: AdvancedTranscriptionResult, output_file: str):
        """Guarda los resultados en diferentes formatos"""
        
        output_path = Path(output_file)
        base_name = output_path.stem
        output_dir = output_path.parent
        
        # 1. Guardar transcripción simple (.txt)
        txt_path = output_dir / f"{base_name}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result.transcription)
        
        # 2. Guardar SRT con información contextual
        srt_path = output_dir / f"{base_name}_advanced.srt"
        self._save_advanced_srt(result, srt_path)
        
        # 3. Guardar JSON completo si se solicita
        if self.config.export_detailed_results:
            json_path = output_dir / f"{base_name}_detailed.json"
            self._save_detailed_json(result, json_path)
        
        print(f"💾 Resultados guardados en: {output_dir}")
    
    def _save_advanced_srt(self, result: AdvancedTranscriptionResult, srt_path: Path):
        """Guarda SRT con información contextual y VAD"""
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result.segments, 1):
                # Formatear timestamps
                start_time = self._format_srt_time(segment.start_time)
                end_time = self._format_srt_time(segment.end_time)
                
                # Texto base
                text = segment.text
                
                # Añadir información contextual si está habilitada
                if self.config.include_context_info and hasattr(segment, 'context_info'):
                    context_info = segment.context_info
                    if 'gaming_context' in context_info:
                        text += f" [CTX: {context_info['gaming_context']}]"
                
                # Añadir confianza si está habilitada
                if self.config.include_confidence_scores:
                    text += f" [CONF: {segment.confidence:.2f}]"
                
                # Escribir entrada SRT
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
    
    def _format_srt_time(self, seconds: float) -> str:
        """Formatea tiempo en formato SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _save_detailed_json(self, result: AdvancedTranscriptionResult, json_path: Path):
        """Guarda resultados detallados en JSON"""
        
        # Convertir a formato serializable
        result_dict = {
            'transcription': result.transcription,
            'segments': [asdict(seg) for seg in result.segments],
            'vad_segments': [asdict(vad) for vad in result.vad_segments],
            'speech_ratio': result.speech_ratio,
            'gaming_contexts': [asdict(ctx) for ctx in result.gaming_contexts],
            'dominant_context': result.dominant_context.value,
            'context_confidence': result.context_confidence,
            'overall_confidence': result.overall_confidence,
            'processing_time': result.processing_time,
            'audio_quality_score': result.audio_quality_score,
            'audio_duration': result.audio_duration,
            'model_used': result.model_used,
            'vad_models_used': result.vad_models_used,
            'timestamp': result.timestamp.isoformat(),
            'user_id': result.user_id,
            'final_vad_config': result.final_vad_config,
            'multipass_config': result.multipass_config
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
    
    def _update_learning_data(self, result: AdvancedTranscriptionResult):
        """Actualiza datos de aprendizaje y estadísticas"""
        
        # Actualizar estadísticas generales
        self.processing_stats['total_files_processed'] += 1
        self.processing_stats['total_processing_time'] += result.processing_time
        
        # Actualizar ratio promedio de speech
        current_avg = self.processing_stats['average_speech_ratio']
        n = self.processing_stats['total_files_processed']
        new_avg = ((current_avg * (n-1)) + result.speech_ratio) / n
        self.processing_stats['average_speech_ratio'] = new_avg
        
        # Actualizar distribución de contextos
        context_dist = self.processing_stats['context_distribution']
        context_key = result.dominant_context.value
        context_dist[context_key] = context_dist.get(context_key, 0) + 1
        
        # Aprendizaje adaptativo (si está habilitado)
        if self.config.enable_adaptive_learning and self.contextual_vad:
            learning_data = {
                'transcription_quality': result.overall_confidence,
                'context_accuracy': result.context_confidence,
                'speech_detection_accuracy': result.speech_ratio,
                'processing_efficiency': 1.0 / result.processing_time if result.processing_time > 0 else 1.0
            }
            
            # Simular feedback positivo si la calidad es alta
            if result.overall_confidence > 0.8 and result.context_confidence > 0.7:
                feedback = {
                    'context_corrections': [],  # No hay correcciones
                    'vad_adjustments': [],      # No hay ajustes necesarios
                    'positive_feedback': True
                }
                self.contextual_vad.learn_from_feedback(feedback)
        
        # Guardar estadísticas si se solicita
        if self.config.save_learning_data:
            stats_path = Path(self.config.model_cache_dir) / "processing_stats.json"
            with open(stats_path, 'w') as f:
                json.dump(self.processing_stats, f, indent=2)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumen de rendimiento del sistema"""
        
        stats = self.processing_stats.copy()
        
        if stats['total_files_processed'] > 0:
            stats['average_processing_time'] = stats['total_processing_time'] / stats['total_files_processed']
        else:
            stats['average_processing_time'] = 0
        
        # Añadir estadísticas de componentes
        if self.hybrid_vad:
            stats['vad_stats'] = self.hybrid_vad.get_performance_stats()
        
        if self.contextual_vad:
            stats['context_stats'] = self.contextual_vad.get_context_summary()
        
        return stats

def create_advanced_config(profile: str = "gaming") -> AdvancedTranscriptionConfig:
    """Crea configuraciones predefinidas para diferentes casos de uso"""
    
    config = AdvancedTranscriptionConfig()
    
    if profile == "gaming":
        # Configuración optimizada para gaming
        config.gaming_mode = True
        config.enable_hybrid_vad = True
        config.enable_contextual_analysis = True
        config.enable_multipass = True
        config.vad_preprocessing = True
        config.detect_game_events = True
        config.prioritize_voice_chat = True
        
    elif profile == "streaming":
        # Configuración para streaming/grabación
        config.enable_adaptive_learning = True
        config.chunk_processing = True
        config.parallel_processing = True
        config.include_context_info = True
        config.export_detailed_results = True
        
    elif profile == "fast":
        # Configuración rápida
        config.enable_multipass = False
        config.enable_contextual_analysis = False
        config.chunk_processing = False
        config.parallel_processing = True
        
    elif profile == "precision":
        # Configuración de máxima precisión
        config.enable_multipass = True
        config.enable_hybrid_vad = True
        config.enable_contextual_analysis = True
        config.vad_preprocessing = True
        config.enable_adaptive_learning = True
        config.include_confidence_scores = True
        
    return config

def main():
    """Función principal para uso desde línea de comandos"""
    
    parser = argparse.ArgumentParser(description="Transcripción Avanzada con VAD Híbrido")
    parser.add_argument("input_file", help="Archivo de audio a transcribir")
    parser.add_argument("-o", "--output", help="Archivo de salida (opcional)")
    parser.add_argument("-p", "--profile", choices=["gaming", "streaming", "fast", "precision"], 
                       default="gaming", help="Perfil de configuración")
    parser.add_argument("-u", "--user", default="default_user", help="ID de usuario para personalización")
    parser.add_argument("--no-vad", action="store_true", help="Deshabilitar VAD híbrido")
    parser.add_argument("--no-context", action="store_true", help="Deshabilitar análisis contextual")
    parser.add_argument("--no-multipass", action="store_true", help="Deshabilitar multipass")
    parser.add_argument("--verbose", action="store_true", help="Salida detallada")
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    
    # Crear configuración
    config = create_advanced_config(args.profile)
    config.user_id = args.user
    
    # Aplicar overrides de argumentos
    if args.no_vad:
        config.enable_hybrid_vad = False
    if args.no_context:
        config.enable_contextual_analysis = False
    if args.no_multipass:
        config.enable_multipass = False
    
    # Crear transcriptor y procesar
    try:
        transcriber = AdvancedTranscriber(config)
        
        # Determinar archivo de salida
        if args.output:
            output_file = args.output
        else:
            input_path = Path(args.input_file)
            output_file = input_path.parent / f"{input_path.stem}_transcribed.txt"
        
        # Transcribir
        result = transcriber.transcribe_file(args.input_file, str(output_file))
        
        # Mostrar resumen
        print("\n📊 Resumen de transcripción:")
        print(f"   Texto: {len(result.transcription)} caracteres")
        print(f"   Segmentos: {len(result.segments)}")
        print(f"   Confianza: {result.overall_confidence:.2f}")
        print(f"   Contexto: {result.dominant_context.value}")
        print(f"   Speech ratio: {result.speech_ratio:.2f}")
        print(f"   Tiempo: {result.processing_time:.2f}s")
        
        # Mostrar estadísticas del sistema
        if args.verbose:
            performance = transcriber.get_performance_summary()
            print(f"\n🔧 Estadísticas del sistema:")
            print(f"   Archivos procesados: {performance['total_files_processed']}")
            print(f"   Tiempo promedio: {performance.get('average_processing_time', 0):.2f}s")
        
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())