#!/usr/bin/env python3
"""
🧠 Sistema de Aprendizaje Adaptativo para GameClipping
======================================================

Sistema avanzado de machine learning que aprende continuamente de:
- Patrones de uso del usuario
- Feedback de calidad de transcripción
- Contextos gaming específicos
- Optimizaciones automáticas de parámetros
- Detección de nuevos escenarios

Características principales:
- Aprendizaje online continuo
- Optimización automática de parámetros VAD
- Detección de patrones gaming personalizados
- Sistema de recompensas basado en calidad
- Adaptación automática a nuevos juegos/contextos

Autor: GameClipping Team
Fecha: Septiembre 2025
Versión: 1.0
"""

import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict, field
import json
import time
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import threading
import queue

# Machine Learning imports
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn no disponible. Install: pip install scikit-learn")

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️ Optuna no disponible. Install: pip install optuna")

from vad_hybrid import HybridVADConfig
from vad_contextual import GamingContext, GamingContextResult

class LearningObjective(Enum):
    """Objetivos de aprendizaje del sistema"""
    TRANSCRIPTION_ACCURACY = "transcription_accuracy"
    VAD_PRECISION = "vad_precision" 
    PROCESSING_SPEED = "processing_speed"
    CONTEXT_RECOGNITION = "context_recognition"
    USER_SATISFACTION = "user_satisfaction"
    ENERGY_EFFICIENCY = "energy_efficiency"

class FeedbackType(Enum):
    """Tipos de feedback del usuario"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"
    PARAMETER_ADJUSTMENT = "parameter_adjustment"
    CONTEXT_CORRECTION = "context_correction"
    QUALITY_RATING = "quality_rating"

@dataclass
class LearningSession:
    """Sesión de aprendizaje individual"""
    session_id: str
    user_id: str
    timestamp: datetime
    
    # Datos de entrada
    audio_features: Dict[str, float]
    gaming_context: GamingContext
    vad_parameters: Dict[str, float]
    transcription_config: Dict[str, Any]
    
    # Resultados obtenidos
    transcription_quality: float
    vad_accuracy: float
    processing_time: float
    context_confidence: float
    
    # Feedback del usuario
    user_feedback: List[Dict[str, Any]] = field(default_factory=list)
    quality_rating: Optional[float] = None
    
    # Métricas calculadas
    overall_score: float = 0.0
    improvement_suggestions: List[str] = field(default_factory=list)

@dataclass
class OptimizationResult:
    """Resultado de una optimización de parámetros"""
    objective: LearningObjective
    original_score: float
    optimized_score: float
    improvement: float
    optimized_parameters: Dict[str, float]
    optimization_time: float
    confidence_level: float

@dataclass 
class UserProfile:
    """Perfil de usuario con patrones aprendidos"""
    user_id: str
    creation_date: datetime
    last_updated: datetime
    
    # Preferencias aprendidas
    preferred_gaming_contexts: Dict[GamingContext, float]
    optimal_vad_parameters: Dict[str, float]
    transcription_preferences: Dict[str, Any]
    
    # Patrones de uso
    usage_patterns: Dict[str, List[float]]  # patterns por hora del día, día semana, etc.
    frequent_words: Dict[str, int]
    speech_characteristics: Dict[str, float]
    
    # Métricas de aprendizaje
    total_sessions: int = 0
    improvement_rate: float = 0.0
    satisfaction_score: float = 0.5
    learning_effectiveness: float = 0.0

class AdaptiveLearningSystem:
    """
    🧠 Sistema de Aprendizaje Adaptativo
    
    Aprende continuamente de los datos de uso para:
    - Optimizar parámetros automáticamente
    - Detectar nuevos patrones gaming
    - Personalizar experiencia por usuario
    - Mejorar la calidad general del sistema
    """
    
    def __init__(self, model_path: str = "learning_models", enable_online_learning: bool = True):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        self.enable_online_learning = enable_online_learning
        
        # Modelos de aprendizaje
        self.parameter_optimizer = None
        self.context_predictor = None
        self.quality_predictor = None
        self.user_profiler = None
        
        # Datos de entrenamiento
        self.learning_sessions = deque(maxlen=10000)  # Buffer circular
        self.user_profiles = {}
        self.optimization_history = []
        
        # Sistema de feedback
        self.feedback_queue = queue.Queue()
        self.learning_thread = None
        self.learning_active = False
        
        # Métricas y estadísticas
        self.performance_metrics = defaultdict(list)
        self.optimization_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'average_improvement': 0.0,
            'best_configurations': {}
        }
        
        print("🧠 Inicializando Sistema de Aprendizaje Adaptativo...")
        self._initialize_system()
    
    def _initialize_system(self):
        """Inicializa todos los componentes del sistema de aprendizaje"""
        
        # 1. Cargar modelos existentes
        self._load_models()
        
        # 2. Cargar perfiles de usuario
        self._load_user_profiles()
        
        # 3. Cargar historial de optimizaciones
        self._load_optimization_history()
        
        # 4. Inicializar thread de aprendizaje si está habilitado
        if self.enable_online_learning:
            self._start_learning_thread()
        
        print("✅ Sistema de aprendizaje inicializado")
    
    def _load_models(self):
        """Carga modelos de ML existentes"""
        
        model_files = {
            'parameter_optimizer': 'parameter_optimizer.pkl',
            'context_predictor': 'context_predictor.pkl', 
            'quality_predictor': 'quality_predictor.pkl',
            'user_profiler': 'user_profiler.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_path = self.model_path / filename
            if model_path.exists() and SKLEARN_AVAILABLE:
                try:
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    setattr(self, model_name, model)
                    print(f"   ✅ Cargado {model_name}")
                except Exception as e:
                    print(f"   ⚠️ Error cargando {model_name}: {e}")
        
        # Crear modelos por defecto si no existen
        if not hasattr(self, 'parameter_optimizer') or self.parameter_optimizer is None:
            self._create_default_models()
    
    def _create_default_models(self):
        """Crea modelos por defecto si no existen"""
        
        if not SKLEARN_AVAILABLE:
            print("⚠️ Scikit-learn no disponible, usando heurísticas")
            return
        
        print("🔧 Creando modelos por defecto...")
        
        # Optimizador de parámetros
        self.parameter_optimizer = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        # Predictor de contexto
        self.context_predictor = GradientBoostingRegressor(
            n_estimators=100,
            random_state=42,
            learning_rate=0.1
        )
        
        # Predictor de calidad
        self.quality_predictor = RandomForestRegressor(
            n_estimators=50,
            random_state=42
        )
        
        # Profiler de usuario (clustering)
        self.user_profiler = KMeans(n_clusters=5, random_state=42)
        
        print("✅ Modelos por defecto creados")
    
    def _load_user_profiles(self):
        """Carga perfiles de usuario existentes"""
        
        profiles_path = self.model_path / "user_profiles.json"
        if profiles_path.exists():
            try:
                with open(profiles_path, 'r') as f:
                    profiles_data = json.load(f)
                
                for user_id, profile_data in profiles_data.items():
                    # Convertir fechas
                    profile_data['creation_date'] = datetime.fromisoformat(profile_data['creation_date'])
                    profile_data['last_updated'] = datetime.fromisoformat(profile_data['last_updated'])
                    
                    # Convertir gaming contexts
                    preferred_contexts = {}
                    for context_str, value in profile_data['preferred_gaming_contexts'].items():
                        try:
                            context_enum = GamingContext(context_str)
                            preferred_contexts[context_enum] = value
                        except ValueError:
                            continue
                    profile_data['preferred_gaming_contexts'] = preferred_contexts
                    
                    # Crear perfil
                    profile = UserProfile(**profile_data)
                    self.user_profiles[user_id] = profile
                
                print(f"👤 Cargados {len(self.user_profiles)} perfiles de usuario")
                
            except Exception as e:
                print(f"⚠️ Error cargando perfiles: {e}")
    
    def _load_optimization_history(self):
        """Carga historial de optimizaciones"""
        
        history_path = self.model_path / "optimization_history.json"
        if history_path.exists():
            try:
                with open(history_path, 'r') as f:
                    history_data = json.load(f)
                
                for entry in history_data:
                    # Reconstruir objetos
                    entry['objective'] = LearningObjective(entry['objective'])
                    result = OptimizationResult(**entry)
                    self.optimization_history.append(result)
                
                print(f"📈 Cargado historial de {len(self.optimization_history)} optimizaciones")
                
            except Exception as e:
                print(f"⚠️ Error cargando historial: {e}")
    
    def _start_learning_thread(self):
        """Inicia el thread de aprendizaje continuo"""
        
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_worker, daemon=True)
        self.learning_thread.start()
        print("🔄 Thread de aprendizaje continuo iniciado")
    
    def _learning_worker(self):
        """Worker thread para aprendizaje continuo"""
        
        while self.learning_active:
            try:
                # Procesar feedback pendiente
                while not self.feedback_queue.empty():
                    feedback_data = self.feedback_queue.get(timeout=1)
                    self._process_feedback(feedback_data)
                
                # Optimización periódica (cada 10 minutos)
                time.sleep(600)
                if len(self.learning_sessions) >= 20:  # Mínimo para optimización
                    self._periodic_optimization()
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Error en learning worker: {e}")
                time.sleep(30)  # Pausa antes de reintentar
    
    def add_learning_session(self, session: LearningSession):
        """
        📊 Añade una nueva sesión de aprendizaje
        
        Args:
            session: Datos de la sesión de aprendizaje
        """
        
        # Calcular score general
        session.overall_score = self._calculate_overall_score(session)
        
        # Añadir al buffer
        self.learning_sessions.append(session)
        
        # Actualizar perfil de usuario
        self._update_user_profile(session)
        
        # Añadir a métricas
        self.performance_metrics['overall_scores'].append(session.overall_score)
        self.performance_metrics['processing_times'].append(session.processing_time)
        self.performance_metrics['quality_scores'].append(session.transcription_quality)
        
        print(f"📊 Sesión de aprendizaje añadida - Score: {session.overall_score:.3f}")
        
        # Trigger optimización si tenemos suficientes datos
        if len(self.learning_sessions) % 50 == 0:  # Cada 50 sesiones
            self._queue_optimization()
    
    def _calculate_overall_score(self, session: LearningSession) -> float:
        """Calcula el score general de una sesión"""
        
        # Pesos para diferentes objetivos
        weights = {
            'transcription_quality': 0.4,
            'vad_accuracy': 0.3,
            'processing_speed': 0.15,
            'context_confidence': 0.15
        }
        
        # Normalizar processing time (menor es mejor)
        speed_score = max(0, 1.0 - (session.processing_time / 60.0))  # Penalizar >60s
        
        # Calcular score ponderado
        overall_score = (
            session.transcription_quality * weights['transcription_quality'] +
            session.vad_accuracy * weights['vad_accuracy'] +
            speed_score * weights['processing_speed'] +
            session.context_confidence * weights['context_confidence']
        )
        
        # Bonus por feedback positivo del usuario
        if session.user_feedback:
            positive_feedback = sum(1 for fb in session.user_feedback 
                                  if fb.get('type') == FeedbackType.POSITIVE.value)
            feedback_bonus = min(0.1, positive_feedback * 0.05)
            overall_score += feedback_bonus
        
        # Bonus por rating del usuario
        if session.quality_rating:
            rating_bonus = (session.quality_rating - 0.5) * 0.1  # ±0.1 based on rating
            overall_score += rating_bonus
        
        return max(0.0, min(1.0, overall_score))
    
    def _update_user_profile(self, session: LearningSession):
        """Actualiza el perfil del usuario con datos de la sesión"""
        
        user_id = session.user_id
        
        # Crear perfil si no existe
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                creation_date=datetime.now(),
                last_updated=datetime.now(),
                preferred_gaming_contexts={},
                optimal_vad_parameters={},
                transcription_preferences={},
                usage_patterns={},
                frequent_words={},
                speech_characteristics={}
            )
        
        profile = self.user_profiles[user_id]
        
        # Actualizar contextos preferidos
        context = session.gaming_context
        if context not in profile.preferred_gaming_contexts:
            profile.preferred_gaming_contexts[context] = 0.5
        
        # Promedio móvil exponencial para preferencias
        alpha = 0.1  # Factor de aprendizaje
        current_pref = profile.preferred_gaming_contexts[context]
        new_score = session.overall_score
        profile.preferred_gaming_contexts[context] = (1 - alpha) * current_pref + alpha * new_score
        
        # Actualizar parámetros VAD óptimos
        if session.overall_score > 0.7:  # Solo usar sesiones exitosas
            for param, value in session.vad_parameters.items():
                if param not in profile.optimal_vad_parameters:
                    profile.optimal_vad_parameters[param] = value
                else:
                    # Promedio ponderado por calidad
                    current_value = profile.optimal_vad_parameters[param]
                    weight = session.overall_score
                    profile.optimal_vad_parameters[param] = (
                        (1 - weight) * current_value + weight * value
                    )
        
        # Actualizar estadísticas
        profile.total_sessions += 1
        profile.last_updated = datetime.now()
        
        # Calcular rate de mejora
        recent_scores = [s.overall_score for s in list(self.learning_sessions)[-10:] 
                        if s.user_id == user_id]
        if len(recent_scores) >= 2:
            profile.improvement_rate = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        
        # Actualizar satisfaction score
        if session.quality_rating:
            profile.satisfaction_score = (
                0.8 * profile.satisfaction_score + 0.2 * session.quality_rating
            )
    
    def _queue_optimization(self):
        """Encola una optimización para el thread de aprendizaje"""
        
        if self.enable_online_learning:
            optimization_task = {
                'type': 'optimization',
                'timestamp': datetime.now(),
                'objective': LearningObjective.TRANSCRIPTION_ACCURACY  # Por defecto
            }
            self.feedback_queue.put(optimization_task)
    
    def _periodic_optimization(self):
        """Ejecuta optimización periódica automática"""
        
        print("🔧 Ejecutando optimización periódica...")
        
        # Rotar entre diferentes objetivos
        objectives = list(LearningObjective)
        current_objective = objectives[len(self.optimization_history) % len(objectives)]
        
        # Ejecutar optimización
        try:
            result = self.optimize_parameters(
                objective=current_objective,
                max_evaluations=20,  # Optimización rápida
                timeout_minutes=5
            )
            
            if result and result.improvement > 0.05:  # Mejora significativa
                print(f"✅ Optimización exitosa: {result.improvement:.3f} mejora")
                self._apply_optimization_result(result)
            else:
                print("📊 Sin mejoras significativas en optimización")
                
        except Exception as e:
            print(f"⚠️ Error en optimización periódica: {e}")
    
    def optimize_parameters(self, objective: LearningObjective, user_id: str = None, 
                          max_evaluations: int = 100, timeout_minutes: int = 30) -> OptimizationResult:
        """
        🎯 Optimiza parámetros para un objetivo específico
        
        Args:
            objective: Objetivo a optimizar
            user_id: Usuario específico (None para optimización general)
            max_evaluations: Máximo número de evaluaciones
            timeout_minutes: Timeout en minutos
            
        Returns:
            OptimizationResult con los resultados de la optimización
        """
        
        start_time = time.time()
        
        print(f"🎯 Optimizando parámetros para objetivo: {objective.value}")
        if user_id:
            print(f"   Usuario específico: {user_id}")
        
        # Filtrar sesiones relevantes
        relevant_sessions = self._get_relevant_sessions(user_id, objective)
        
        if len(relevant_sessions) < 10:
            print("⚠️ Insuficientes datos para optimización")
            return None
        
        # Usar Optuna si está disponible, sino usar grid search básico
        if OPTUNA_AVAILABLE:
            result = self._optimize_with_optuna(objective, relevant_sessions, max_evaluations, timeout_minutes)
        else:
            result = self._optimize_with_grid_search(objective, relevant_sessions)
        
        optimization_time = time.time() - start_time
        
        if result:
            result.optimization_time = optimization_time
            self.optimization_history.append(result)
            self._update_optimization_stats(result)
            
            print(f"✅ Optimización completada en {optimization_time:.2f}s")
            print(f"   Mejora: {result.improvement:.3f}")
            print(f"   Confianza: {result.confidence_level:.3f}")
        
        return result
    
    def _get_relevant_sessions(self, user_id: str, objective: LearningObjective) -> List[LearningSession]:
        """Filtra sesiones relevantes para optimización"""
        
        sessions = list(self.learning_sessions)
        
        # Filtrar por usuario si se especifica
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        
        # Filtrar por calidad mínima (evitar datos ruidosos)
        sessions = [s for s in sessions if s.overall_score > 0.3]
        
        # Priorizar sesiones recientes
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_sessions = [s for s in sessions if s.timestamp > cutoff_date]
        
        if len(recent_sessions) >= 10:
            return recent_sessions
        else:
            return sessions
    
    def _optimize_with_optuna(self, objective: LearningObjective, sessions: List[LearningSession], 
                            max_evaluations: int, timeout_minutes: int) -> OptimizationResult:
        """Optimización usando Optuna"""
        
        def objective_function(trial):
            # Definir espacio de parámetros
            params = {
                'silero_threshold': trial.suggest_float('silero_threshold', 0.1, 0.9),
                'pyannote_threshold': trial.suggest_float('pyannote_threshold', 0.1, 0.9),
                'webrtc_aggressiveness': trial.suggest_int('webrtc_aggressiveness', 0, 3),
                'min_speech_duration': trial.suggest_float('min_speech_duration', 0.05, 0.5),
                'min_silence_duration': trial.suggest_float('min_silence_duration', 0.1, 1.0),
                'merge_threshold': trial.suggest_float('merge_threshold', 0.1, 0.5),
                'silero_weight': trial.suggest_float('silero_weight', 0.1, 0.8),
                'pyannote_weight': trial.suggest_float('pyannote_weight', 0.1, 0.6),
                'webrtc_weight': trial.suggest_float('webrtc_weight', 0.1, 0.5)
            }
            
            # Normalizar pesos (deben sumar ~1.0)
            weight_sum = params['silero_weight'] + params['pyannote_weight'] + params['webrtc_weight']
            params['silero_weight'] /= weight_sum
            params['pyannote_weight'] /= weight_sum
            params['webrtc_weight'] /= weight_sum
            
            # Evaluar configuración con sesiones históricas
            return self._evaluate_parameter_config(params, sessions, objective)
        
        # Crear study
        study = optuna.create_study(direction='maximize')
        
        # Optimizar con timeout
        study.optimize(
            objective_function, 
            n_trials=max_evaluations,
            timeout=timeout_minutes * 60
        )
        
        # Evaluar resultado
        best_params = study.best_params
        original_score = self._evaluate_current_config(sessions, objective)
        optimized_score = study.best_value
        improvement = optimized_score - original_score
        
        # Calcular confianza basada en número de trials
        confidence = min(1.0, len(study.trials) / max_evaluations)
        
        return OptimizationResult(
            objective=objective,
            original_score=original_score,
            optimized_score=optimized_score,
            improvement=improvement,
            optimized_parameters=best_params,
            optimization_time=0.0,  # Se establecerá después
            confidence_level=confidence
        )
    
    def _optimize_with_grid_search(self, objective: LearningObjective, sessions: List[LearningSession]) -> OptimizationResult:
        """Optimización básica con grid search cuando Optuna no está disponible"""
        
        print("🔍 Usando grid search básico...")
        
        # Definir grid de parámetros simplificado
        param_grid = {
            'silero_threshold': [0.3, 0.4, 0.5, 0.6, 0.7],
            'pyannote_threshold': [0.3, 0.4, 0.5, 0.6, 0.7],
            'webrtc_aggressiveness': [1, 2, 3],
            'min_speech_duration': [0.05, 0.1, 0.15, 0.2],
            'merge_threshold': [0.2, 0.3, 0.4]
        }
        
        best_score = 0
        best_params = {}
        original_score = self._evaluate_current_config(sessions, objective)
        
        # Grid search simple
        for silero_th in param_grid['silero_threshold']:
            for pyannote_th in param_grid['pyannote_threshold']:
                for webrtc_agg in param_grid['webrtc_aggressiveness']:
                    for min_speech in param_grid['min_speech_duration']:
                        for merge_th in param_grid['merge_threshold']:
                            
                            params = {
                                'silero_threshold': silero_th,
                                'pyannote_threshold': pyannote_th,
                                'webrtc_aggressiveness': webrtc_agg,
                                'min_speech_duration': min_speech,
                                'merge_threshold': merge_th,
                                'silero_weight': 0.5,
                                'pyannote_weight': 0.3,
                                'webrtc_weight': 0.2
                            }
                            
                            score = self._evaluate_parameter_config(params, sessions, objective)
                            
                            if score > best_score:
                                best_score = score
                                best_params = params.copy()
        
        improvement = best_score - original_score
        
        return OptimizationResult(
            objective=objective,
            original_score=original_score,
            optimized_score=best_score,
            improvement=improvement,
            optimized_parameters=best_params,
            optimization_time=0.0,
            confidence_level=0.7  # Confianza media para grid search
        )
    
    def _evaluate_parameter_config(self, params: Dict[str, float], sessions: List[LearningSession], 
                                 objective: LearningObjective) -> float:
        """Evalúa una configuración de parámetros con sesiones históricas"""
        
        scores = []
        
        for session in sessions:
            # Simular el score que habría obtenido con estos parámetros
            simulated_score = self._simulate_session_score(session, params, objective)
            scores.append(simulated_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _simulate_session_score(self, session: LearningSession, params: Dict[str, float], 
                               objective: LearningObjective) -> float:
        """Simula el score de una sesión con parámetros específicos"""
        
        # Heurística simple para simular impacto de parámetros
        base_score = session.overall_score
        
        # Analizar diferencias de parámetros
        param_diff_score = 0.0
        
        for param, value in params.items():
            if param in session.vad_parameters:
                original_value = session.vad_parameters[param]
                
                # Penalizar diferencias grandes
                diff = abs(value - original_value)
                
                if param in ['silero_threshold', 'pyannote_threshold']:
                    # Thresholds: diferencias moderadas pueden ser buenas
                    penalty = min(0.1, diff * 0.2)
                elif param == 'webrtc_aggressiveness':
                    # Aggressiveness: diferencias grandes son más penalizantes
                    penalty = min(0.15, diff * 0.05)
                else:
                    # Otros parámetros
                    penalty = min(0.05, diff * 0.1)
                
                param_diff_score -= penalty
        
        # Ajustes específicos por objetivo
        if objective == LearningObjective.TRANSCRIPTION_ACCURACY:
            # Favorecer thresholds moderados para precisión
            if 0.4 <= params.get('silero_threshold', 0.5) <= 0.6:
                param_diff_score += 0.05
        
        elif objective == LearningObjective.VAD_PRECISION:
            # Favorecer configuraciones más conservadoras
            if params.get('silero_threshold', 0.5) > 0.5:
                param_diff_score += 0.03
        
        elif objective == LearningObjective.PROCESSING_SPEED:
            # Favorecer configuraciones más agresivas (menos procesamiento)
            if params.get('webrtc_aggressiveness', 2) >= 2:
                param_diff_score += 0.02
        
        return max(0.0, min(1.0, base_score + param_diff_score))
    
    def _evaluate_current_config(self, sessions: List[LearningSession], objective: LearningObjective) -> float:
        """Evalúa la configuración actual promedio"""
        
        scores = []
        
        for session in sessions:
            if objective == LearningObjective.TRANSCRIPTION_ACCURACY:
                scores.append(session.transcription_quality)
            elif objective == LearningObjective.VAD_PRECISION:
                scores.append(session.vad_accuracy)
            elif objective == LearningObjective.PROCESSING_SPEED:
                # Invertir tiempo (menor es mejor)
                speed_score = max(0, 1.0 - (session.processing_time / 60.0))
                scores.append(speed_score)
            elif objective == LearningObjective.CONTEXT_RECOGNITION:
                scores.append(session.context_confidence)
            else:
                scores.append(session.overall_score)
        
        return np.mean(scores) if scores else 0.0
    
    def _apply_optimization_result(self, result: OptimizationResult):
        """Aplica los resultados de optimización al sistema"""
        
        # Guardar configuración óptima
        config_path = self.model_path / f"optimal_config_{result.objective.value}.json"
        
        config_data = {
            'objective': result.objective.value,
            'parameters': result.optimized_parameters,
            'improvement': result.improvement,
            'confidence': result.confidence_level,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Actualizar estadísticas de mejores configuraciones
        self.optimization_stats['best_configurations'][result.objective.value] = {
            'parameters': result.optimized_parameters,
            'score': result.optimized_score,
            'improvement': result.improvement
        }
        
        print(f"💾 Configuración óptima guardada para {result.objective.value}")
    
    def _update_optimization_stats(self, result: OptimizationResult):
        """Actualiza estadísticas de optimización"""
        
        self.optimization_stats['total_optimizations'] += 1
        
        if result.improvement > 0:
            self.optimization_stats['successful_optimizations'] += 1
        
        # Promedio móvil de mejoras
        current_avg = self.optimization_stats['average_improvement']
        n = self.optimization_stats['total_optimizations']
        new_avg = ((current_avg * (n-1)) + result.improvement) / n
        self.optimization_stats['average_improvement'] = new_avg
    
    def _process_feedback(self, feedback_data: Dict[str, Any]):
        """Procesa feedback del usuario para aprendizaje"""
        
        feedback_type = feedback_data.get('type')
        
        if feedback_type == 'optimization':
            # Trigger optimización
            objective = feedback_data.get('objective', LearningObjective.TRANSCRIPTION_ACCURACY)
            try:
                self.optimize_parameters(objective, max_evaluations=30, timeout_minutes=10)
            except Exception as e:
                print(f"⚠️ Error en optimización automática: {e}")
        
        elif feedback_type == 'user_feedback':
            # Procesar feedback específico del usuario
            user_id = feedback_data.get('user_id')
            session_id = feedback_data.get('session_id')
            
            # Buscar sesión correspondiente
            for session in self.learning_sessions:
                if session.session_id == session_id and session.user_id == user_id:
                    session.user_feedback.append(feedback_data)
                    # Recalcular score con nuevo feedback
                    session.overall_score = self._calculate_overall_score(session)
                    break
    
    def get_user_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        💡 Obtiene recomendaciones personalizadas para un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con recomendaciones personalizadas
        """
        
        if user_id not in self.user_profiles:
            return {'message': 'Usuario no encontrado, usando configuración por defecto'}
        
        profile = self.user_profiles[user_id]
        
        # Recomendaciones de parámetros VAD
        vad_recommendations = profile.optimal_vad_parameters.copy()
        
        # Contextos gaming recomendados
        best_contexts = sorted(
            profile.preferred_gaming_contexts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Sugerencias de mejora
        improvement_suggestions = []
        
        if profile.improvement_rate < 0:
            improvement_suggestions.append("Considerar ajustar thresholds VAD para mejor precisión")
        
        if profile.satisfaction_score < 0.6:
            improvement_suggestions.append("Probar configuración más conservadora")
        
        if profile.total_sessions < 10:
            improvement_suggestions.append("Continuar usando el sistema para mejor personalización")
        
        return {
            'user_profile': {
                'total_sessions': profile.total_sessions,
                'satisfaction_score': profile.satisfaction_score,
                'improvement_rate': profile.improvement_rate,
                'learning_effectiveness': profile.learning_effectiveness
            },
            'vad_recommendations': vad_recommendations,
            'best_gaming_contexts': [(ctx.value, score) for ctx, score in best_contexts],
            'improvement_suggestions': improvement_suggestions,
            'next_optimization_ready': profile.total_sessions >= 20
        }
    
    def save_all_data(self):
        """Guarda todos los datos del sistema de aprendizaje"""
        
        print("💾 Guardando datos del sistema de aprendizaje...")
        
        # 1. Guardar modelos
        if SKLEARN_AVAILABLE:
            model_files = {
                'parameter_optimizer': self.parameter_optimizer,
                'context_predictor': self.context_predictor,
                'quality_predictor': self.quality_predictor,
                'user_profiler': self.user_profiler
            }
            
            for model_name, model in model_files.items():
                if model is not None:
                    model_path = self.model_path / f"{model_name}.pkl"
                    try:
                        with open(model_path, 'wb') as f:
                            pickle.dump(model, f)
                    except Exception as e:
                        print(f"⚠️ Error guardando {model_name}: {e}")
        
        # 2. Guardar perfiles de usuario
        profiles_data = {}
        for user_id, profile in self.user_profiles.items():
            # Convertir a formato serializable
            profile_dict = asdict(profile)
            profile_dict['creation_date'] = profile.creation_date.isoformat()
            profile_dict['last_updated'] = profile.last_updated.isoformat()
            
            # Convertir gaming contexts
            preferred_contexts = {}
            for context, value in profile.preferred_gaming_contexts.items():
                preferred_contexts[context.value] = value
            profile_dict['preferred_gaming_contexts'] = preferred_contexts
            
            profiles_data[user_id] = profile_dict
        
        profiles_path = self.model_path / "user_profiles.json"
        with open(profiles_path, 'w') as f:
            json.dump(profiles_data, f, indent=2)
        
        # 3. Guardar historial de optimizaciones
        history_data = []
        for result in self.optimization_history:
            result_dict = asdict(result)
            result_dict['objective'] = result.objective.value
            history_data.append(result_dict)
        
        history_path = self.model_path / "optimization_history.json"
        with open(history_path, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        # 4. Guardar estadísticas
        stats_path = self.model_path / "learning_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(self.optimization_stats, f, indent=2)
        
        print("✅ Datos guardados exitosamente")
    
    def shutdown(self):
        """Cierra el sistema de aprendizaje limpiamente"""
        
        print("🔄 Cerrando sistema de aprendizaje...")
        
        # Detener thread de aprendizaje
        if self.learning_active:
            self.learning_active = False
            if self.learning_thread:
                self.learning_thread.join(timeout=5)
        
        # Guardar todos los datos
        self.save_all_data()
        
        print("✅ Sistema de aprendizaje cerrado")

# Función de conveniencia para crear sesión de aprendizaje
def create_learning_session(user_id: str, audio_features: Dict, gaming_context: GamingContext,
                          vad_params: Dict, transcription_quality: float, 
                          vad_accuracy: float, processing_time: float,
                          context_confidence: float, user_feedback: List = None) -> LearningSession:
    """Crea una sesión de aprendizaje fácilmente"""
    
    session_id = f"{user_id}_{int(time.time())}"
    
    return LearningSession(
        session_id=session_id,
        user_id=user_id,
        timestamp=datetime.now(),
        audio_features=audio_features,
        gaming_context=gaming_context,
        vad_parameters=vad_params,
        transcription_config={},
        transcription_quality=transcription_quality,
        vad_accuracy=vad_accuracy,
        processing_time=processing_time,
        context_confidence=context_confidence,
        user_feedback=user_feedback or []
    )

if __name__ == "__main__":
    # Demo y testing
    print("🧠 Demo Sistema de Aprendizaje Adaptativo")
    print("=" * 60)
    
    try:
        # Crear sistema de aprendizaje
        learning_system = AdaptiveLearningSystem(enable_online_learning=False)
        print("✅ Sistema de aprendizaje inicializado")
        
        # Simular sesiones de aprendizaje
        for i in range(5):
            session = create_learning_session(
                user_id="demo_user",
                audio_features={'spectral_centroid': 2000 + i*100, 'rms_energy': 0.3 + i*0.1},
                gaming_context=GamingContext.COMBAT,
                vad_params={'silero_threshold': 0.5, 'pyannote_threshold': 0.5},
                transcription_quality=0.7 + i*0.05,
                vad_accuracy=0.8 + i*0.03,
                processing_time=10.0 - i*0.5,
                context_confidence=0.75 + i*0.04
            )
            
            learning_system.add_learning_session(session)
        
        print(f"📊 Añadidas {len(learning_system.learning_sessions)} sesiones de demo")
        
        # Obtener recomendaciones
        recommendations = learning_system.get_user_recommendations("demo_user")
        print(f"💡 Recomendaciones: {recommendations}")
        
        # Simular optimización
        if SKLEARN_AVAILABLE and len(learning_system.learning_sessions) >= 3:
            print("🎯 Ejecutando optimización demo...")
            result = learning_system.optimize_parameters(
                LearningObjective.TRANSCRIPTION_ACCURACY,
                max_evaluations=5,
                timeout_minutes=1
            )
            
            if result:
                print(f"✅ Optimización demo completada - Mejora: {result.improvement:.3f}")
        
        # Guardar datos
        learning_system.save_all_data()
        learning_system.shutdown()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Para uso completo instala: pip install scikit-learn optuna")