#!/usr/bin/env python3
"""
🧠 VAD Híbrido Inteligente para GameClipping
==================================================

Sistema VAD avanzado que combina múltiples modelos para máxima precisión:
- Silero VAD v6.0 (primario)
- PyAnnote Audio 3.4 (secundario) 
- WebRTC VAD (respaldo)
- Fusión inteligente con voting ponderado
- Optimizaciones específicas para gaming

Autor: GameClipping Team
Fecha: Septiembre 2025
Versión: 1.0
"""

import numpy as np
import torch
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import json
import time
from collections import defaultdict

# Imports para diferentes VAD models
try:
    import silero_vad
    SILERO_AVAILABLE = True
except ImportError:
    SILERO_AVAILABLE = False
    print("⚠️ Silero VAD no disponible. Install: pip install silero-vad")

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    print("⚠️ PyAnnote Audio no disponible. Install: pip install pyannote.audio")

try:
    import webrtcvad
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    print("⚠️ WebRTC VAD no disponible. Install: pip install webrtcvad")

@dataclass
class VADResult:
    """Resultado de detección VAD"""
    start_time: float
    end_time: float
    confidence: float
    model_source: str
    is_speech: bool
    audio_quality: float = 0.0
    context_info: Dict = None

@dataclass
class HybridVADConfig:
    """Configuración para VAD Híbrido"""
    # Configuración general
    sample_rate: int = 16000
    chunk_duration: float = 0.03  # 30ms chunks
    
    # Thresholds por modelo
    silero_threshold: float = 0.5
    pyannote_threshold: float = 0.5
    webrtc_aggressiveness: int = 2  # 0-3, más alto = más agresivo
    
    # Pesos para fusión (deben sumar 1.0)
    silero_weight: float = 0.5
    pyannote_weight: float = 0.3
    webrtc_weight: float = 0.2
    
    # Gaming-specific optimizations
    gaming_mode: bool = True
    music_suppression: bool = True
    rapid_speech_detection: bool = True
    background_noise_tolerance: float = 0.3
    
    # Filtros y post-procesamiento
    min_speech_duration: float = 0.1  # Mínimo 100ms para considerar speech
    min_silence_duration: float = 0.5  # Mínimo 500ms para considerar silencio
    merge_close_segments: bool = True
    merge_threshold: float = 0.3  # Fusionar segmentos cercanos <300ms

class HybridVAD:
    """
    🎯 VAD Híbrido Inteligente
    
    Combina múltiples modelos VAD para máxima precisión y robustez,
    especialmente optimizado para contenido gaming.
    """
    
    def __init__(self, config: HybridVADConfig = None):
        self.config = config or HybridVADConfig()
        self.models = {}
        self.performance_stats = defaultdict(list)
        
        print("🚀 Inicializando VAD Híbrido...")
        self._initialize_models()
        
    def _initialize_models(self):
        """Inicializa todos los modelos VAD disponibles"""
        
        # 1. Silero VAD v6.0 (Primario)
        if SILERO_AVAILABLE:
            try:
                print("🔵 Cargando Silero VAD v6.0...")
                self.models['silero'] = silero_vad.load_silero_vad()
                print("✅ Silero VAD listo")
            except Exception as e:
                print(f"❌ Error cargando Silero VAD: {e}")
        
        # 2. PyAnnote Audio 3.4 (Secundario)
        if PYANNOTE_AVAILABLE:
            try:
                print("🟡 Cargando PyAnnote Audio...")
                # Note: Requiere token de HuggingFace para modelos públicos
                # self.models['pyannote'] = Pipeline.from_pretrained("pyannote/voice-activity-detection")
                print("⚠️ PyAnnote requiere configuración adicional (HF token)")
            except Exception as e:
                print(f"❌ Error cargando PyAnnote: {e}")
        
        # 3. WebRTC VAD (Respaldo)
        if WEBRTC_AVAILABLE:
            try:
                print("🟢 Cargando WebRTC VAD...")
                self.models['webrtc'] = webrtcvad.Vad(self.config.webrtc_aggressiveness)
                print("✅ WebRTC VAD listo")
            except Exception as e:
                print(f"❌ Error cargando WebRTC VAD: {e}")
        
        if not self.models:
            raise RuntimeError("❌ No se pudo cargar ningún modelo VAD")
        
        print(f"🎯 VAD Híbrido listo con {len(self.models)} modelos: {list(self.models.keys())}")
    
    def detect_speech_activity(self, audio: np.ndarray, sample_rate: int = None) -> List[VADResult]:
        """
        🔍 Detección principal de actividad de voz
        
        Args:
            audio: Array de audio numpy
            sample_rate: Tasa de muestreo (opcional, usa config por defecto)
            
        Returns:
            Lista de VADResult con segmentos de voz detectados
        """
        if sample_rate is None:
            sample_rate = self.config.sample_rate
        
        print(f"🎤 Analizando audio: {len(audio)/sample_rate:.2f}s")
        start_time = time.time()
        
        # Obtener resultados de cada modelo disponible
        model_results = {}
        
        if 'silero' in self.models:
            model_results['silero'] = self._detect_with_silero(audio, sample_rate)
        
        if 'pyannote' in self.models:
            model_results['pyannote'] = self._detect_with_pyannote(audio, sample_rate)
        
        if 'webrtc' in self.models:
            model_results['webrtc'] = self._detect_with_webrtc(audio, sample_rate)
        
        # Fusión inteligente de resultados
        fused_results = self._fuse_results(model_results)
        
        # Post-procesamiento
        final_results = self._post_process_results(fused_results)
        
        processing_time = time.time() - start_time
        print(f"⚡ VAD completado en {processing_time:.3f}s - {len(final_results)} segmentos detectados")
        
        return final_results
    
    def _detect_with_silero(self, audio: np.ndarray, sample_rate: int) -> List[VADResult]:
        """Detección con Silero VAD"""
        try:
            # Convertir audio al formato que espera Silero
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Silero espera audio en torch tensor
            audio_tensor = torch.from_numpy(audio)
            
            # Detectar timestamps de speech
            speech_timestamps = silero_vad.get_speech_timestamps(
                audio_tensor, 
                self.models['silero'],
                return_seconds=True,
                threshold=self.config.silero_threshold
            )
            
            results = []
            for segment in speech_timestamps:
                result = VADResult(
                    start_time=segment['start'],
                    end_time=segment['end'], 
                    confidence=0.8,  # Silero no retorna confianza explícita
                    model_source='silero',
                    is_speech=True,
                    context_info={'method': 'neural_network'}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"⚠️ Error en Silero VAD: {e}")
            return []
    
    def _detect_with_pyannote(self, audio: np.ndarray, sample_rate: int) -> List[VADResult]:
        """Detección con PyAnnote Audio"""
        try:
            # PyAnnote requiere configuración específica
            # Placeholder implementation
            print("🟡 PyAnnote VAD (placeholder - requiere configuración)")
            return []
            
        except Exception as e:
            print(f"⚠️ Error en PyAnnote VAD: {e}")
            return []
    
    def _detect_with_webrtc(self, audio: np.ndarray, sample_rate: int) -> List[VADResult]:
        """Detección con WebRTC VAD"""
        try:
            # WebRTC requiere específicamente 16kHz
            if sample_rate != 16000:
                print(f"⚠️ WebRTC requiere 16kHz, recibido {sample_rate}Hz")
                return []
            
            # Convertir a formato requerido por WebRTC
            if audio.dtype != np.int16:
                audio_int16 = (audio * 32767).astype(np.int16)
            else:
                audio_int16 = audio
            
            # Procesar en chunks de 30ms (480 samples a 16kHz)
            chunk_size = int(0.03 * sample_rate)  # 30ms
            results = []
            current_speech_start = None
            
            for i in range(0, len(audio_int16), chunk_size):
                chunk = audio_int16[i:i+chunk_size]
                
                # WebRTC necesita chunks de tamaño exacto
                if len(chunk) != chunk_size:
                    continue
                
                chunk_bytes = chunk.tobytes()
                is_speech = self.models['webrtc'].is_speech(chunk_bytes, sample_rate)
                
                chunk_time = i / sample_rate
                
                if is_speech and current_speech_start is None:
                    # Inicio de speech
                    current_speech_start = chunk_time
                elif not is_speech and current_speech_start is not None:
                    # Fin de speech
                    result = VADResult(
                        start_time=current_speech_start,
                        end_time=chunk_time,
                        confidence=0.7,  # WebRTC no da confianza explícita
                        model_source='webrtc',
                        is_speech=True,
                        context_info={'method': 'signal_processing'}
                    )
                    results.append(result)
                    current_speech_start = None
            
            # Manejar speech que continúa hasta el final
            if current_speech_start is not None:
                result = VADResult(
                    start_time=current_speech_start,
                    end_time=len(audio_int16) / sample_rate,
                    confidence=0.7,
                    model_source='webrtc', 
                    is_speech=True,
                    context_info={'method': 'signal_processing'}
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            print(f"⚠️ Error en WebRTC VAD: {e}")
            return []
    
    def _fuse_results(self, model_results: Dict[str, List[VADResult]]) -> List[VADResult]:
        """
        🔄 Fusión inteligente de resultados de múltiples modelos
        
        Estrategia:
        1. Voting ponderado por confianza
        2. Resolución de conflictos
        3. Complementariedad entre modelos
        """
        if not model_results:
            return []
        
        # Si solo hay un modelo, retornar directamente
        if len(model_results) == 1:
            return list(model_results.values())[0]
        
        print(f"🔄 Fusionando resultados de {len(model_results)} modelos...")
        
        # Combinar todos los segmentos y ordenar por tiempo
        all_segments = []
        for model_name, segments in model_results.items():
            for segment in segments:
                all_segments.append(segment)
        
        all_segments.sort(key=lambda x: x.start_time)
        
        # Fusionar segmentos superpuestos con voting ponderado
        fused_segments = []
        i = 0
        
        while i < len(all_segments):
            current_segment = all_segments[i]
            overlapping_segments = [current_segment]
            
            # Buscar segmentos superpuestos
            j = i + 1
            while j < len(all_segments):
                next_segment = all_segments[j]
                if self._segments_overlap(current_segment, next_segment):
                    overlapping_segments.append(next_segment)
                    j += 1
                else:
                    break
            
            # Fusionar segmentos superpuestos
            if len(overlapping_segments) > 1:
                fused_segment = self._merge_overlapping_segments(overlapping_segments)
                fused_segments.append(fused_segment)
                i = j
            else:
                fused_segments.append(current_segment)
                i += 1
        
        return fused_segments
    
    def _segments_overlap(self, seg1: VADResult, seg2: VADResult) -> bool:
        """Verifica si dos segmentos se superponen"""
        return not (seg1.end_time < seg2.start_time or seg2.end_time < seg1.start_time)
    
    def _merge_overlapping_segments(self, segments: List[VADResult]) -> VADResult:
        """Fusiona múltiples segmentos superpuestos en uno solo"""
        # Calcular boundaries
        start_time = min(seg.start_time for seg in segments)
        end_time = max(seg.end_time for seg in segments)
        
        # Calcular confianza ponderada
        total_weight = 0
        weighted_confidence = 0
        
        for segment in segments:
            if segment.model_source == 'silero':
                weight = self.config.silero_weight
            elif segment.model_source == 'pyannote':
                weight = self.config.pyannote_weight
            elif segment.model_source == 'webrtc':
                weight = self.config.webrtc_weight
            else:
                weight = 0.1  # Peso por defecto
            
            weighted_confidence += segment.confidence * weight
            total_weight += weight
        
        if total_weight > 0:
            final_confidence = weighted_confidence / total_weight
        else:
            final_confidence = np.mean([seg.confidence for seg in segments])
        
        # Determinar modelo fuente primario (el de mayor confianza)
        primary_model = max(segments, key=lambda x: x.confidence).model_source
        
        return VADResult(
            start_time=start_time,
            end_time=end_time,
            confidence=final_confidence,
            model_source=f"hybrid_{primary_model}",
            is_speech=True,
            context_info={
                'source_models': [seg.model_source for seg in segments],
                'fusion_method': 'weighted_voting'
            }
        )
    
    def _post_process_results(self, results: List[VADResult]) -> List[VADResult]:
        """
        📝 Post-procesamiento de resultados
        
        - Filtrar segmentos muy cortos
        - Fusionar segmentos cercanos
        - Aplicar filtros gaming-specific
        """
        if not results:
            return results
        
        print("📝 Aplicando post-procesamiento...")
        
        # 1. Filtrar segmentos muy cortos
        filtered_results = []
        for result in results:
            duration = result.end_time - result.start_time
            if duration >= self.config.min_speech_duration:
                filtered_results.append(result)
        
        print(f"   Filtrados {len(results) - len(filtered_results)} segmentos muy cortos")
        
        # 2. Fusionar segmentos cercanos
        if self.config.merge_close_segments and len(filtered_results) > 1:
            merged_results = []
            current_segment = filtered_results[0]
            
            for next_segment in filtered_results[1:]:
                gap = next_segment.start_time - current_segment.end_time
                
                if gap <= self.config.merge_threshold:
                    # Fusionar segmentos
                    current_segment = VADResult(
                        start_time=current_segment.start_time,
                        end_time=next_segment.end_time,
                        confidence=max(current_segment.confidence, next_segment.confidence),
                        model_source=f"merged_{current_segment.model_source}",
                        is_speech=True,
                        context_info={'merged': True}
                    )
                else:
                    merged_results.append(current_segment)
                    current_segment = next_segment
            
            merged_results.append(current_segment)
            
            print(f"   Fusionados {len(filtered_results) - len(merged_results)} segmentos cercanos")
            filtered_results = merged_results
        
        # 3. Gaming-specific filters
        if self.config.gaming_mode:
            filtered_results = self._apply_gaming_filters(filtered_results)
        
        return filtered_results
    
    def _apply_gaming_filters(self, results: List[VADResult]) -> List[VADResult]:
        """Aplica filtros específicos para gaming"""
        print("🎮 Aplicando filtros gaming...")
        
        # Placeholder para filtros gaming específicos
        # Aquí se implementarían:
        # - Detección de efectos de sonido vs voz
        # - Filtrado de música de fondo
        # - Optimización para speech rápido en gaming
        
        return results
    
    def get_performance_stats(self) -> Dict:
        """Retorna estadísticas de rendimiento"""
        return dict(self.performance_stats)
    
    def save_config(self, config_path: str):
        """Guarda configuración actual"""
        config_dict = {
            'sample_rate': self.config.sample_rate,
            'chunk_duration': self.config.chunk_duration,
            'silero_threshold': self.config.silero_threshold,
            'pyannote_threshold': self.config.pyannote_threshold,
            'webrtc_aggressiveness': self.config.webrtc_aggressiveness,
            'silero_weight': self.config.silero_weight,
            'pyannote_weight': self.config.pyannote_weight,
            'webrtc_weight': self.config.webrtc_weight,
            'gaming_mode': self.config.gaming_mode,
            'music_suppression': self.config.music_suppression
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"💾 Configuración guardada en {config_path}")

def create_gaming_vad_config() -> HybridVADConfig:
    """Crea configuración optimizada para gaming"""
    config = HybridVADConfig()
    
    # Optimizaciones gaming
    config.gaming_mode = True
    config.music_suppression = True
    config.rapid_speech_detection = True
    config.background_noise_tolerance = 0.4  # Más tolerante al ruido
    
    # Ajustes de threshold más sensibles para gaming
    config.silero_threshold = 0.35
    config.pyannote_threshold = 0.4
    config.webrtc_aggressiveness = 3  # Máximo agresivo
    
    # Pesos optimizados (Silero es mejor para gaming)
    config.silero_weight = 0.6
    config.pyannote_weight = 0.25
    config.webrtc_weight = 0.15
    
    # Timing optimizado para gaming (speech rápido)
    config.min_speech_duration = 0.05  # 50ms mínimo
    config.min_silence_duration = 0.3  # 300ms mínimo silencio
    config.merge_threshold = 0.2  # Fusionar gaps <200ms
    
    return config

# Función de conveniencia para uso directo
def detect_speech_activity(audio_file: str, config: HybridVADConfig = None) -> List[VADResult]:
    """
    🎯 Función de conveniencia para detección VAD
    
    Args:
        audio_file: Ruta al archivo de audio
        config: Configuración opcional (usa gaming por defecto)
    
    Returns:
        Lista de segmentos de voz detectados
    """
    import librosa
    
    if config is None:
        config = create_gaming_vad_config()
    
    # Cargar audio
    audio, sample_rate = librosa.load(audio_file, sr=config.sample_rate)
    
    # Crear VAD y detectar
    vad = HybridVAD(config)
    results = vad.detect_speech_activity(audio, sample_rate)
    
    return results

if __name__ == "__main__":
    # Demo y testing
    print("🎮 Demo VAD Híbrido para GameClipping")
    print("=" * 50)
    
    # Crear configuración gaming
    config = create_gaming_vad_config()
    print("✅ Configuración gaming creada")
    
    # Inicializar VAD
    try:
        vad = HybridVAD(config)
        print("✅ VAD Híbrido inicializado correctamente")
        
        # Guardar configuración
        vad.save_config("vad_hybrid_config.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Para usar completamente este módulo, instala:")
        print("   pip install silero-vad webrtcvad")
        print("   pip install pyannote.audio  # Requiere configuración adicional")