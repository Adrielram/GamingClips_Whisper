#!/usr/bin/env python3
"""
🧠 VAD Contextual con Gaming Intelligence
==========================================

Sistema VAD inteligente que adapta su comportamiento basado en:
- Análisis de contenido gaming en tiempo real
- Patrones de usuario aprendidos
- Contexto dinámico del juego
- Machine Learning para optimización continua

Características principales:
- Detección de diferentes tipos de contenido gaming
- Adaptación automática de parámetros VAD
- Sistema de aprendizaje de patrones de usuario
- Análisis de contexto gaming (combate, exploración, menús, etc.)

Autor: GameClipping Team
Fecha: Septiembre 2025
Versión: 1.0
"""

import numpy as np
import torch
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
import json
import time
from collections import defaultdict, deque
from enum import Enum
import pickle
import threading
from datetime import datetime

# Machine Learning imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn no disponible. Install: pip install scikit-learn")

# Audio analysis imports
try:
    import librosa
    import librosa.feature
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️ Librosa no disponible. Install: pip install librosa")

from vad_hybrid import VADResult, HybridVAD, HybridVADConfig

class GamingContext(Enum):
    """Tipos de contexto gaming detectados"""
    COMBAT = "combat"           # Combate activo
    EXPLORATION = "exploration" # Exploración
    DIALOGUE = "dialogue"       # Diálogos/cutscenes
    MENU = "menu"              # Menús del juego
    LOADING = "loading"        # Pantallas de carga
    AMBIENT = "ambient"        # Audio ambiental
    MULTIPLAYER = "multiplayer" # Comunicación multijugador
    STREAMING = "streaming"    # Streaming/grabación
    UNKNOWN = "unknown"        # Contexto desconocido

@dataclass
class AudioFeatures:
    """Características extraídas del audio para análisis contextual"""
    # Características espectrales
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    zero_crossing_rate: float
    
    # Características de energía
    rms_energy: float
    energy_variance: float
    
    # Características de frecuencia
    mfcc_features: List[float]  # 13 coefficients
    chroma_features: List[float] # 12 coefficients
    
    # Características temporales
    tempo: float
    onset_rate: float
    
    # Gaming-specific features
    periodic_energy: float      # Para detectar efectos repetitivos
    transient_density: float    # Densidad de transientes (explosiones, etc.)
    harmonic_ratio: float       # Ratio harmónico vs percusivo

@dataclass
class GamingContextResult:
    """Resultado del análisis de contexto gaming"""
    context_type: GamingContext
    confidence: float
    audio_features: AudioFeatures
    recommended_vad_config: Dict[str, Any]
    adaptation_suggestions: List[str]
    timestamp: float

@dataclass
class UserPattern:
    """Patrón de usuario aprendido"""
    user_id: str
    gaming_preferences: Dict[GamingContext, float]  # Preferencias por contexto
    speech_patterns: Dict[str, float]               # Patrones de habla
    optimal_vad_params: Dict[str, float]            # Parámetros VAD óptimos
    learning_sessions: int
    last_updated: datetime

class ContextualVAD:
    """
    🎯 VAD Contextual con Gaming Intelligence
    
    Sistema avanzado que adapta el comportamiento VAD basado en:
    - Análisis en tiempo real del contenido gaming
    - Patrones de usuario aprendidos
    - Contexto dinámico del juego
    """
    
    def __init__(self, user_id: str = "default_user", model_path: str = None):
        self.user_id = user_id
        self.model_path = model_path or "contextual_vad_models"
        
        # Crear directorio para modelos si no existe
        Path(self.model_path).mkdir(exist_ok=True)
        
        # Inicializar componentes
        self.hybrid_vad = None
        self.context_classifier = None
        self.feature_scaler = None
        self.user_patterns = {}
        
        # Buffers para análisis temporal
        self.context_history = deque(maxlen=50)  # Últimos 50 contextos
        self.audio_buffer = deque(maxlen=1000)   # Buffer de audio para análisis
        
        # Estadísticas y métricas
        self.stats = defaultdict(int)
        self.adaptation_history = []
        
        print(f"🧠 Inicializando VAD Contextual para usuario: {user_id}")
        self._initialize_system()
    
    def _initialize_system(self):
        """Inicializa todos los componentes del sistema"""
        
        # 1. Cargar o crear modelo de clasificación de contexto
        self._load_or_create_context_classifier()
        
        # 2. Cargar patrones de usuario
        self._load_user_patterns()
        
        # 3. Inicializar VAD híbrido con configuración base
        base_config = HybridVADConfig()
        self.hybrid_vad = HybridVAD(base_config)
        
        print("✅ VAD Contextual inicializado")
    
    def _load_or_create_context_classifier(self):
        """Carga o crea el clasificador de contexto gaming"""
        classifier_path = Path(self.model_path) / "context_classifier.pkl"
        scaler_path = Path(self.model_path) / "feature_scaler.pkl"
        
        if classifier_path.exists() and scaler_path.exists() and SKLEARN_AVAILABLE:
            try:
                # Cargar modelos existentes
                with open(classifier_path, 'rb') as f:
                    self.context_classifier = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.feature_scaler = pickle.load(f)
                print("📈 Modelos de clasificación cargados")
            except Exception as e:
                print(f"⚠️ Error cargando modelos: {e}")
                self._create_default_classifier()
        else:
            self._create_default_classifier()
    
    def _create_default_classifier(self):
        """Crea clasificador por defecto con datos sintéticos"""
        if not SKLEARN_AVAILABLE:
            print("⚠️ Scikit-learn no disponible, usando clasificación basada en reglas")
            return
        
        print("🔧 Creando clasificador por defecto...")
        
        # Crear datos sintéticos para entrenamiento inicial
        training_data = self._generate_synthetic_training_data()
        
        # Entrenar modelo
        if training_data:
            X, y = training_data
            
            # Scaler para normalización
            self.feature_scaler = StandardScaler()
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Clasificador RandomForest
            self.context_classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            self.context_classifier.fit(X_scaled, y)
            
            # Guardar modelos
            self._save_models()
            print("✅ Clasificador creado y entrenado")
    
    def _generate_synthetic_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Genera datos sintéticos para entrenamiento inicial"""
        print("🎲 Generando datos sintéticos de entrenamiento...")
        
        # Definir características típicas por contexto
        context_profiles = {
            GamingContext.COMBAT: {
                'spectral_centroid': (2000, 4000),
                'rms_energy': (0.3, 0.8),
                'zero_crossing_rate': (0.15, 0.35),
                'transient_density': (0.6, 0.9),
                'tempo': (120, 180)
            },
            GamingContext.DIALOGUE: {
                'spectral_centroid': (800, 2000),
                'rms_energy': (0.1, 0.4),
                'zero_crossing_rate': (0.05, 0.15),
                'transient_density': (0.1, 0.3),
                'tempo': (60, 100)
            },
            GamingContext.EXPLORATION: {
                'spectral_centroid': (1000, 3000),
                'rms_energy': (0.05, 0.3),
                'zero_crossing_rate': (0.08, 0.20),
                'transient_density': (0.2, 0.5),
                'tempo': (80, 120)
            },
            GamingContext.MENU: {
                'spectral_centroid': (500, 1500),
                'rms_energy': (0.02, 0.15),
                'zero_crossing_rate': (0.03, 0.10),
                'transient_density': (0.1, 0.2),
                'tempo': (40, 80)
            }
        }
        
        X = []
        y = []
        
        # Generar muestras para cada contexto
        for context, profile in context_profiles.items():
            for _ in range(50):  # 50 muestras por contexto
                # Generar características aleatorias dentro de los rangos
                features = []
                
                # Características básicas
                features.append(np.random.uniform(*profile['spectral_centroid']))
                features.append(np.random.uniform(*profile['rms_energy']))
                features.append(np.random.uniform(*profile['zero_crossing_rate']))
                features.append(np.random.uniform(*profile['transient_density']))
                features.append(np.random.uniform(*profile['tempo']))
                
                # Características adicionales (simuladas)
                features.extend([np.random.uniform(0, 1) for _ in range(10)])  # MFCC simulados
                features.extend([np.random.uniform(0, 1) for _ in range(5)])   # Otros features
                
                X.append(features)
                y.append(context.value)
        
        return np.array(X), np.array(y)
    
    def _save_models(self):
        """Guarda los modelos entrenados"""
        if self.context_classifier and self.feature_scaler:
            classifier_path = Path(self.model_path) / "context_classifier.pkl"
            scaler_path = Path(self.model_path) / "feature_scaler.pkl"
            
            with open(classifier_path, 'wb') as f:
                pickle.dump(self.context_classifier, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.feature_scaler, f)
            
            print("💾 Modelos guardados")
    
    def _load_user_patterns(self):
        """Carga patrones de usuario desde archivo"""
        user_patterns_path = Path(self.model_path) / f"user_patterns_{self.user_id}.json"
        
        if user_patterns_path.exists():
            try:
                with open(user_patterns_path, 'r') as f:
                    data = json.load(f)
                
                # Convertir de vuelta a UserPattern
                for user_id, pattern_data in data.items():
                    # Convertir string keys de vuelta a enum
                    gaming_prefs = {}
                    for context_str, value in pattern_data['gaming_preferences'].items():
                        try:
                            context_enum = GamingContext(context_str)
                            gaming_prefs[context_enum] = value
                        except ValueError:
                            continue
                    
                    pattern = UserPattern(
                        user_id=user_id,
                        gaming_preferences=gaming_prefs,
                        speech_patterns=pattern_data['speech_patterns'],
                        optimal_vad_params=pattern_data['optimal_vad_params'],
                        learning_sessions=pattern_data['learning_sessions'],
                        last_updated=datetime.fromisoformat(pattern_data['last_updated'])
                    )
                    self.user_patterns[user_id] = pattern
                
                print(f"👤 Patrones de usuario cargados para {len(self.user_patterns)} usuarios")
                
            except Exception as e:
                print(f"⚠️ Error cargando patrones de usuario: {e}")
    
    def extract_audio_features(self, audio: np.ndarray, sample_rate: int) -> AudioFeatures:
        """
        🔍 Extrae características del audio para análisis contextual
        
        Args:
            audio: Señal de audio
            sample_rate: Tasa de muestreo
            
        Returns:
            AudioFeatures con todas las características extraídas
        """
        if not LIBROSA_AVAILABLE:
            # Retornar características básicas si librosa no está disponible
            return AudioFeatures(
                spectral_centroid=1000.0,
                spectral_rolloff=2000.0,
                spectral_bandwidth=500.0,
                zero_crossing_rate=0.1,
                rms_energy=0.1,
                energy_variance=0.05,
                mfcc_features=[0.0] * 13,
                chroma_features=[0.0] * 12,
                tempo=100.0,
                onset_rate=5.0,
                periodic_energy=0.5,
                transient_density=0.3,
                harmonic_ratio=0.7
            )
        
        try:
            # Características espectrales
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Características de energía
            rms_energy = librosa.feature.rms(y=audio)[0]
            energy_variance = np.var(rms_energy)
            
            # MFCC (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            mfcc_features = [float(np.mean(mfcc)) for mfcc in mfccs]
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            chroma_features = [float(np.mean(chrom)) for chrom in chroma]
            
            # Características temporales
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sample_rate)
            onset_rate = len(onset_frames) / (len(audio) / sample_rate)
            
            # Gaming-specific features
            # Harmonic vs percussive separation
            harmonic, percussive = librosa.effects.hpss(audio)
            harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(harmonic)) + np.mean(np.abs(percussive)) + 1e-10)
            
            # Periodic energy (para detectar loops/efectos repetitivos)
            stft = np.abs(librosa.stft(audio))
            periodic_energy = float(np.mean(np.std(stft, axis=1)))
            
            # Transient density (densidad de transientes para explosiones, etc.)
            transient_density = float(np.mean(np.abs(percussive)))
            
            return AudioFeatures(
                spectral_centroid=float(np.mean(spectral_centroids)),
                spectral_rolloff=float(np.mean(spectral_rolloff)),
                spectral_bandwidth=float(np.mean(spectral_bandwidth)),
                zero_crossing_rate=float(np.mean(zero_crossing_rate)),
                rms_energy=float(np.mean(rms_energy)),
                energy_variance=float(energy_variance),
                mfcc_features=mfcc_features,
                chroma_features=chroma_features,
                tempo=float(tempo),
                onset_rate=float(onset_rate),
                periodic_energy=periodic_energy,
                transient_density=transient_density,
                harmonic_ratio=harmonic_ratio
            )
            
        except Exception as e:
            print(f"⚠️ Error extrayendo características: {e}")
            # Retornar características por defecto
            return AudioFeatures(
                spectral_centroid=1000.0,
                spectral_rolloff=2000.0,
                spectral_bandwidth=500.0,
                zero_crossing_rate=0.1,
                rms_energy=0.1,
                energy_variance=0.05,
                mfcc_features=[0.0] * 13,
                chroma_features=[0.0] * 12,
                tempo=100.0,
                onset_rate=5.0,
                periodic_energy=0.5,
                transient_density=0.3,
                harmonic_ratio=0.7
            )
    
    def classify_gaming_context(self, audio_features: AudioFeatures) -> GamingContextResult:
        """
        🎮 Clasifica el contexto gaming basado en características de audio
        
        Args:
            audio_features: Características extraídas del audio
            
        Returns:
            GamingContextResult con el contexto detectado y recomendaciones
        """
        if self.context_classifier and self.feature_scaler and SKLEARN_AVAILABLE:
            return self._ml_classify_context(audio_features)
        else:
            return self._rule_based_classify_context(audio_features)
    
    def _ml_classify_context(self, audio_features: AudioFeatures) -> GamingContextResult:
        """Clasificación basada en Machine Learning"""
        try:
            # Preparar features para el modelo
            feature_vector = [
                audio_features.spectral_centroid,
                audio_features.rms_energy,
                audio_features.zero_crossing_rate,
                audio_features.transient_density,
                audio_features.tempo
            ]
            feature_vector.extend(audio_features.mfcc_features[:10])  # Primeros 10 MFCC
            feature_vector.extend([
                audio_features.periodic_energy,
                audio_features.harmonic_ratio,
                audio_features.onset_rate,
                audio_features.energy_variance,
                audio_features.spectral_bandwidth
            ])
            
            # Normalizar
            feature_array = np.array([feature_vector])
            feature_scaled = self.feature_scaler.transform(feature_array)
            
            # Predecir
            prediction = self.context_classifier.predict(feature_scaled)[0]
            probabilities = self.context_classifier.predict_proba(feature_scaled)[0]
            confidence = float(max(probabilities))
            
            try:
                context_type = GamingContext(prediction)
            except ValueError:
                context_type = GamingContext.UNKNOWN
            
            # Generar recomendaciones de configuración VAD
            vad_config = self._generate_vad_recommendations(context_type, audio_features)
            adaptation_suggestions = self._generate_adaptation_suggestions(context_type, confidence)
            
            return GamingContextResult(
                context_type=context_type,
                confidence=confidence,
                audio_features=audio_features,
                recommended_vad_config=vad_config,
                adaptation_suggestions=adaptation_suggestions,
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"⚠️ Error en clasificación ML: {e}")
            return self._rule_based_classify_context(audio_features)
    
    def _rule_based_classify_context(self, audio_features: AudioFeatures) -> GamingContextResult:
        """Clasificación basada en reglas cuando ML no está disponible"""
        
        # Reglas heurísticas para clasificación
        context_type = GamingContext.UNKNOWN
        confidence = 0.6
        
        # Combat: Alta energía, muchos transientes, amplio espectro
        if (audio_features.rms_energy > 0.3 and 
            audio_features.transient_density > 0.5 and
            audio_features.spectral_centroid > 2000):
            context_type = GamingContext.COMBAT
            confidence = 0.8
        
        # Dialogue: Energía moderada, baja densidad de transientes, centroide medio-bajo
        elif (audio_features.rms_energy > 0.05 and audio_features.rms_energy < 0.4 and
              audio_features.transient_density < 0.3 and
              audio_features.spectral_centroid < 2000 and
              audio_features.harmonic_ratio > 0.6):
            context_type = GamingContext.DIALOGUE
            confidence = 0.7
        
        # Menu: Baja energía, pocos transientes
        elif (audio_features.rms_energy < 0.15 and
              audio_features.transient_density < 0.2):
            context_type = GamingContext.MENU
            confidence = 0.6
        
        # Exploration: Energía baja-media, transientes moderados
        else:
            context_type = GamingContext.EXPLORATION
            confidence = 0.5
        
        vad_config = self._generate_vad_recommendations(context_type, audio_features)
        adaptation_suggestions = self._generate_adaptation_suggestions(context_type, confidence)
        
        return GamingContextResult(
            context_type=context_type,
            confidence=confidence,
            audio_features=audio_features,
            recommended_vad_config=vad_config,
            adaptation_suggestions=adaptation_suggestions,
            timestamp=time.time()
        )
    
    def _generate_vad_recommendations(self, context_type: GamingContext, audio_features: AudioFeatures) -> Dict[str, Any]:
        """Genera recomendaciones de configuración VAD basadas en el contexto"""
        
        base_config = {
            'silero_threshold': 0.5,
            'pyannote_threshold': 0.5,
            'webrtc_aggressiveness': 2,
            'min_speech_duration': 0.1,
            'min_silence_duration': 0.5,
            'merge_threshold': 0.3
        }
        
        # Adaptaciones por contexto
        if context_type == GamingContext.COMBAT:
            # En combate: más sensible, fusión agresiva
            base_config.update({
                'silero_threshold': 0.3,
                'webrtc_aggressiveness': 3,
                'min_speech_duration': 0.05,
                'merge_threshold': 0.2
            })
        
        elif context_type == GamingContext.DIALOGUE:
            # En diálogos: precisión alta, menos fusión
            base_config.update({
                'silero_threshold': 0.4,
                'pyannote_threshold': 0.4,
                'min_speech_duration': 0.15,
                'merge_threshold': 0.4
            })
        
        elif context_type == GamingContext.MENU:
            # En menús: menos sensible (poco speech esperado)
            base_config.update({
                'silero_threshold': 0.6,
                'pyannote_threshold': 0.6,
                'webrtc_aggressiveness': 1,
                'min_speech_duration': 0.2
            })
        
        elif context_type == GamingContext.EXPLORATION:
            # Exploración: balanceado
            base_config.update({
                'silero_threshold': 0.45,
                'min_speech_duration': 0.1,
                'merge_threshold': 0.3
            })
        
        # Adaptaciones basadas en características de audio
        if audio_features.rms_energy < 0.05:
            # Audio muy bajo, ser más sensible
            base_config['silero_threshold'] -= 0.1
            base_config['pyannote_threshold'] -= 0.1
        
        if audio_features.transient_density > 0.7:
            # Muchos transientes, fusión más agresiva
            base_config['merge_threshold'] = 0.15
            base_config['min_speech_duration'] = 0.05
        
        return base_config
    
    def _generate_adaptation_suggestions(self, context_type: GamingContext, confidence: float) -> List[str]:
        """Genera sugerencias de adaptación"""
        suggestions = []
        
        if confidence < 0.6:
            suggestions.append("Confianza baja en clasificación - considerar reentrenamiento")
        
        if context_type == GamingContext.COMBAT:
            suggestions.append("Detectado combate - optimizando para speech rápido")
            suggestions.append("Incrementando sensibilidad VAD")
        
        elif context_type == GamingContext.DIALOGUE:
            suggestions.append("Detectado diálogo - priorizando precisión")
            suggestions.append("Optimizando para speech claro")
        
        elif context_type == GamingContext.UNKNOWN:
            suggestions.append("Contexto desconocido - usando configuración conservadora")
            suggestions.append("Registrando para mejorar clasificación")
        
        return suggestions
    
    def analyze_speech_with_context(self, audio: np.ndarray, sample_rate: int) -> Tuple[List[VADResult], GamingContextResult]:
        """
        🎯 Análisis principal: combina VAD híbrido con análisis contextual
        
        Args:
            audio: Señal de audio
            sample_rate: Tasa de muestreo
            
        Returns:
            Tupla con (resultados VAD, análisis de contexto)
        """
        start_time = time.time()
        
        print(f"🎯 Analizando audio con contexto: {len(audio)/sample_rate:.2f}s")
        
        # 1. Extraer características de audio
        audio_features = self.extract_audio_features(audio, sample_rate)
        
        # 2. Clasificar contexto gaming
        context_result = self.classify_gaming_context(audio_features)
        
        print(f"🎮 Contexto detectado: {context_result.context_type.value} (confianza: {context_result.confidence:.2f})")
        
        # 3. Adaptar configuración VAD basada en contexto
        adapted_config = self._adapt_vad_config(context_result)
        
        # 4. Ejecutar VAD híbrido con configuración adaptada
        self.hybrid_vad.config = adapted_config
        vad_results = self.hybrid_vad.detect_speech_activity(audio, sample_rate)
        
        # 5. Post-procesar resultados con información contextual
        enhanced_results = self._enhance_vad_results_with_context(vad_results, context_result)
        
        # 6. Actualizar historial y estadísticas
        self._update_analysis_history(context_result, enhanced_results)
        
        processing_time = time.time() - start_time
        print(f"⚡ Análisis contextual completado en {processing_time:.3f}s")
        
        return enhanced_results, context_result
    
    def _adapt_vad_config(self, context_result: GamingContextResult) -> HybridVADConfig:
        """Adapta la configuración VAD basada en el contexto"""
        
        # Crear nueva configuración basada en recomendaciones
        new_config = HybridVADConfig()
        
        # Aplicar recomendaciones del contexto
        for param, value in context_result.recommended_vad_config.items():
            if hasattr(new_config, param):
                setattr(new_config, param, value)
        
        # Aplicar patrones de usuario si están disponibles
        if self.user_id in self.user_patterns:
            user_pattern = self.user_patterns[self.user_id]
            
            # Aplicar parámetros óptimos del usuario
            for param, value in user_pattern.optimal_vad_params.items():
                if hasattr(new_config, param):
                    # Combinar recomendación contextual con preferencia de usuario
                    current_value = getattr(new_config, param)
                    adapted_value = (current_value + value) / 2  # Promedio ponderado
                    setattr(new_config, param, adapted_value)
        
        return new_config
    
    def _enhance_vad_results_with_context(self, vad_results: List[VADResult], context_result: GamingContextResult) -> List[VADResult]:
        """Mejora los resultados VAD con información contextual"""
        
        enhanced_results = []
        
        for result in vad_results:
            # Añadir información contextual a cada resultado
            enhanced_result = VADResult(
                start_time=result.start_time,
                end_time=result.end_time,
                confidence=result.confidence,
                model_source=f"{result.model_source}_contextual",
                is_speech=result.is_speech,
                audio_quality=result.audio_quality,
                context_info={
                    **result.context_info,
                    'gaming_context': context_result.context_type.value,
                    'context_confidence': context_result.confidence,
                    'adaptation_applied': True
                }
            )
            
            # Ajustar confianza basada en contexto
            if context_result.context_type == GamingContext.DIALOGUE:
                # En diálogos, incrementar confianza para speech detectado
                enhanced_result.confidence = min(1.0, enhanced_result.confidence * 1.1)
            elif context_result.context_type == GamingContext.MENU:
                # En menús, reducir confianza (menos speech esperado)
                enhanced_result.confidence = max(0.0, enhanced_result.confidence * 0.9)
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def _update_analysis_history(self, context_result: GamingContextResult, vad_results: List[VADResult]):
        """Actualiza el historial de análisis para aprendizaje"""
        
        # Añadir al historial de contexto
        self.context_history.append(context_result)
        
        # Actualizar estadísticas
        self.stats[f"context_{context_result.context_type.value}"] += 1
        self.stats['total_analyses'] += 1
        self.stats['speech_segments_detected'] += len(vad_results)
        
        # Registrar para aprendizaje adaptativo
        self.adaptation_history.append({
            'timestamp': time.time(),
            'context': context_result.context_type.value,
            'confidence': context_result.confidence,
            'vad_segments': len(vad_results),
            'audio_features': asdict(context_result.audio_features)
        })
        
        # Mantener historial limitado
        if len(self.adaptation_history) > 1000:
            self.adaptation_history = self.adaptation_history[-500:]
    
    def learn_from_feedback(self, feedback_data: Dict[str, Any]):
        """
        📚 Aprendizaje desde feedback del usuario
        
        Args:
            feedback_data: Datos de feedback con correcciones y preferencias
        """
        print("📚 Procesando feedback para aprendizaje adaptativo...")
        
        # Actualizar patrones de usuario
        if self.user_id not in self.user_patterns:
            self.user_patterns[self.user_id] = UserPattern(
                user_id=self.user_id,
                gaming_preferences={},
                speech_patterns={},
                optimal_vad_params={},
                learning_sessions=0,
                last_updated=datetime.now()
            )
        
        user_pattern = self.user_patterns[self.user_id]
        
        # Procesar feedback específico
        if 'context_corrections' in feedback_data:
            # Actualizar preferencias de contexto
            for correction in feedback_data['context_corrections']:
                predicted_context = GamingContext(correction['predicted'])
                actual_context = GamingContext(correction['actual'])
                
                # Ajustar preferencias
                if actual_context not in user_pattern.gaming_preferences:
                    user_pattern.gaming_preferences[actual_context] = 0.5
                
                # Incrementar preferencia por el contexto correcto
                user_pattern.gaming_preferences[actual_context] = min(1.0, 
                    user_pattern.gaming_preferences[actual_context] + 0.1)
        
        if 'vad_adjustments' in feedback_data:
            # Actualizar parámetros VAD óptimos
            for adjustment in feedback_data['vad_adjustments']:
                param = adjustment['parameter']
                value = adjustment['optimal_value']
                user_pattern.optimal_vad_params[param] = value
        
        # Incrementar sesiones de aprendizaje
        user_pattern.learning_sessions += 1
        user_pattern.last_updated = datetime.now()
        
        # Guardar patrones actualizados
        self._save_user_patterns()
        
        # Reentrenar modelo si hay suficientes datos
        if user_pattern.learning_sessions % 10 == 0:
            self._retrain_context_classifier()
        
        print(f"✅ Aprendizaje completado - Sesión #{user_pattern.learning_sessions}")
    
    def _save_user_patterns(self):
        """Guarda patrones de usuario"""
        user_patterns_path = Path(self.model_path) / f"user_patterns_{self.user_id}.json"
        
        # Convertir a formato serializable
        serializable_patterns = {}
        for user_id, pattern in self.user_patterns.items():
            gaming_prefs = {context.value: value for context, value in pattern.gaming_preferences.items()}
            
            serializable_patterns[user_id] = {
                'gaming_preferences': gaming_prefs,
                'speech_patterns': pattern.speech_patterns,
                'optimal_vad_params': pattern.optimal_vad_params,
                'learning_sessions': pattern.learning_sessions,
                'last_updated': pattern.last_updated.isoformat()
            }
        
        with open(user_patterns_path, 'w') as f:
            json.dump(serializable_patterns, f, indent=2)
        
        print("💾 Patrones de usuario guardados")
    
    def _retrain_context_classifier(self):
        """Reentrena el clasificador con nuevos datos"""
        if not SKLEARN_AVAILABLE or not self.adaptation_history:
            return
        
        print("🔄 Reentrenando clasificador de contexto...")
        
        # Preparar datos de entrenamiento desde historial
        X = []
        y = []
        
        for entry in self.adaptation_history:
            if entry['confidence'] > 0.7:  # Solo usar datos de alta confianza
                features = entry['audio_features']
                
                feature_vector = [
                    features['spectral_centroid'],
                    features['rms_energy'],
                    features['zero_crossing_rate'],
                    features['transient_density'],
                    features['tempo']
                ]
                feature_vector.extend(features['mfcc_features'][:10])
                feature_vector.extend([
                    features['periodic_energy'],
                    features['harmonic_ratio'],
                    features['onset_rate'],
                    features['energy_variance'],
                    features['spectral_bandwidth']
                ])
                
                X.append(feature_vector)
                y.append(entry['context'])
        
        if len(X) >= 20:  # Mínimo 20 muestras para reentrenamiento
            X_array = np.array(X)
            y_array = np.array(y)
            
            # Reentrenar scaler y clasificador
            self.feature_scaler.fit(X_array)
            X_scaled = self.feature_scaler.transform(X_array)
            
            self.context_classifier.fit(X_scaled, y_array)
            
            # Guardar modelos actualizados
            self._save_models()
            print("✅ Clasificador reentrenado con nuevos datos")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Retorna resumen del análisis contextual"""
        
        # Análisis del historial de contexto
        context_distribution = defaultdict(int)
        for context_result in self.context_history:
            context_distribution[context_result.context_type.value] += 1
        
        # Estadísticas de confianza
        confidences = [result.confidence for result in self.context_history]
        avg_confidence = np.mean(confidences) if confidences else 0
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'context_distribution': dict(context_distribution),
            'average_confidence': avg_confidence,
            'speech_segments_detected': self.stats['speech_segments_detected'],
            'user_learning_sessions': self.user_patterns.get(self.user_id, UserPattern(
                self.user_id, {}, {}, {}, 0, datetime.now())).learning_sessions
        }

# Función de conveniencia para uso directo
def analyze_gaming_audio(audio_file: str, user_id: str = "default_user") -> Tuple[List[VADResult], GamingContextResult]:
    """
    🎯 Función de conveniencia para análisis gaming completo
    
    Args:
        audio_file: Ruta al archivo de audio
        user_id: ID del usuario para personalización
        
    Returns:
        Tupla con (resultados VAD, análisis de contexto)
    """
    import librosa
    
    # Cargar audio
    audio, sample_rate = librosa.load(audio_file, sr=16000)
    
    # Crear VAD contextual y analizar
    contextual_vad = ContextualVAD(user_id)
    vad_results, context_result = contextual_vad.analyze_speech_with_context(audio, sample_rate)
    
    return vad_results, context_result

if __name__ == "__main__":
    # Demo y testing
    print("🧠 Demo VAD Contextual Gaming")
    print("=" * 50)
    
    try:
        # Crear VAD contextual
        contextual_vad = ContextualVAD("demo_user")
        print("✅ VAD Contextual inicializado")
        
        # Mostrar resumen
        summary = contextual_vad.get_context_summary()
        print(f"📊 Resumen: {summary}")
        
        # Simular feedback de aprendizaje
        feedback = {
            'context_corrections': [
                {'predicted': 'exploration', 'actual': 'combat'},
            ],
            'vad_adjustments': [
                {'parameter': 'silero_threshold', 'optimal_value': 0.35}
            ]
        }
        
        contextual_vad.learn_from_feedback(feedback)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Para usar completamente este módulo, instala:")
        print("   pip install scikit-learn librosa")