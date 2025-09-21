#!/usr/bin/env python3
"""
SISTEMA DE LOGGING CENTRALIZADO PARA TRANSCRIPCIÓN
================================================

Módulo para logging detallado de todos los procesos de transcripción.
Permite depurar errores y monitorear el progreso de cada método.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import json

class TranscriptionLogger:
    def __init__(self, log_dir="logs", console_level=logging.INFO, file_level=logging.DEBUG):
        """
        Inicializa el sistema de logging
        
        Args:
            log_dir: Directorio para archivos de log
            console_level: Nivel de logging para consola
            file_level: Nivel de logging para archivos
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Crear timestamp para esta sesión
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Configurar logging
        self.setup_logging(console_level, file_level)
        
        # Contadores
        self.method_stats = {}
        
    def setup_logging(self, console_level, file_level):
        """Configura el sistema de logging"""
        
        # Crear formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        
        detailed_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Logger principal
        self.logger = logging.getLogger('transcription')
        self.logger.setLevel(logging.DEBUG)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para archivo general
        general_log_file = self.log_dir / f"transcription_{self.session_timestamp}.log"
        file_handler = logging.FileHandler(general_log_file, encoding='utf-8')
        file_handler.setLevel(file_level)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para errores únicamente
        error_log_file = self.log_dir / f"errors_{self.session_timestamp}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)
        
        self.logger.info(f"🚀 Sistema de logging inicializado")
        self.logger.info(f"📁 Logs en: {self.log_dir.absolute()}")
        self.logger.info(f"📝 Archivo general: {general_log_file.name}")
        self.logger.info(f"❌ Archivo errores: {error_log_file.name}")
    
    def log_session_start(self, video_path, selected_methods):
        """Registra el inicio de una sesión de transcripción"""
        self.logger.info("=" * 80)
        self.logger.info("🎯 NUEVA SESIÓN DE TRANSCRIPCIÓN INICIADA")
        self.logger.info("=" * 80)
        self.logger.info(f"📹 Video: {os.path.basename(video_path)}")
        self.logger.info(f"📂 Ruta completa: {video_path}")
        self.logger.info(f"📊 Tamaño: {self.get_file_size_mb(video_path):.1f} MB")
        self.logger.info(f"🔧 Métodos seleccionados: {len(selected_methods)}")
        
        for i, method in enumerate(selected_methods, 1):
            self.logger.info(f"   {i}. {method}")
        
        # Información del sistema
        self.logger.debug(f"💻 Python: {sys.version}")
        self.logger.debug(f"📁 Directorio trabajo: {os.getcwd()}")
        self.logger.debug(f"🕐 Timestamp sesión: {self.session_timestamp}")
        
        # Verificar dependencias críticas
        self.check_dependencies()
    
    def log_method_start(self, method_name, script_path, video_path):
        """Registra el inicio de un método específico"""
        self.logger.info("-" * 60)
        self.logger.info(f"🔄 INICIANDO MÉTODO: {method_name}")
        self.logger.info(f"📄 Script: {script_path}")
        self.logger.info(f"📹 Video: {os.path.basename(video_path)}")
        
        # Verificar que el script existe
        if not os.path.exists(script_path):
            self.logger.error(f"❌ Script no encontrado: {script_path}")
            return False
        
        # Verificar que el video existe
        if not os.path.exists(video_path):
            self.logger.error(f"❌ Video no encontrado: {video_path}")
            return False
        
        # Verificar permisos de escritura en directorio de salida
        output_dir = os.path.dirname(video_path)
        if not os.access(output_dir, os.W_OK):
            self.logger.error(f"❌ Sin permisos de escritura en: {output_dir}")
            return False
        
        self.logger.debug(f"✅ Verificaciones iniciales completadas")
        
        # Inicializar estadísticas para este método
        self.method_stats[method_name] = {
            'start_time': datetime.now(),
            'script': script_path,
            'status': 'running'
        }
        
        return True
    
    def log_command_execution(self, cmd, cwd=None):
        """Registra la ejecución de un comando"""
        self.logger.debug(f"🚀 Ejecutando comando:")
        self.logger.debug(f"   Comando: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        if cwd:
            self.logger.debug(f"   Directorio: {cwd}")
    
    def log_method_progress(self, method_name, message, level=logging.INFO):
        """Registra progreso de un método"""
        self.logger.log(level, f"[{method_name}] {message}")
    
    def log_method_result(self, method_name, success, elapsed_time, output_file=None, error_info=None):
        """Registra el resultado de un método"""
        
        # Actualizar estadísticas
        if method_name in self.method_stats:
            self.method_stats[method_name].update({
                'end_time': datetime.now(),
                'elapsed_time': elapsed_time,
                'success': success,
                'output_file': output_file,
                'error_info': error_info,
                'status': 'completed'
            })
        
        if success:
            self.logger.info(f"✅ {method_name} - COMPLETADO en {elapsed_time:.1f}s")
            if output_file and os.path.exists(output_file):
                size_kb = os.path.getsize(output_file) / 1024
                self.logger.info(f"   📁 Archivo: {os.path.basename(output_file)} ({size_kb:.1f} KB)")
                
                # Verificar contenido del archivo
                self.verify_srt_file(output_file)
            else:
                self.logger.warning(f"   ⚠️ Archivo de salida no encontrado: {output_file}")
        else:
            self.logger.error(f"❌ {method_name} - FALLÓ después de {elapsed_time:.1f}s")
            if error_info:
                self.logger.error(f"   🔧 Error: {error_info}")
    
    def verify_srt_file(self, srt_path):
        """Verifica la validez de un archivo SRT"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = content.strip().split('\n')
            if len(lines) < 4:
                self.logger.warning(f"   ⚠️ Archivo SRT muy pequeño ({len(lines)} líneas)")
                return
            
            # Contar subtítulos
            subtitle_count = content.count('\n\n') + 1
            self.logger.debug(f"   📊 Subtítulos encontrados: {subtitle_count}")
            
            # Verificar formato básico
            if '-->' in content:
                self.logger.debug(f"   ✅ Formato SRT válido")
            else:
                self.logger.warning(f"   ⚠️ Formato SRT posiblemente inválido")
                
        except Exception as e:
            self.logger.error(f"   ❌ Error verificando SRT: {e}")
    
    def log_session_summary(self):
        """Genera un resumen de la sesión"""
        self.logger.info("=" * 80)
        self.logger.info("📊 RESUMEN DE SESIÓN")
        self.logger.info("=" * 80)
        
        total_methods = len(self.method_stats)
        successful_methods = sum(1 for stats in self.method_stats.values() if stats.get('success', False))
        
        self.logger.info(f"🔧 Métodos ejecutados: {total_methods}")
        self.logger.info(f"✅ Métodos exitosos: {successful_methods}")
        self.logger.info(f"❌ Métodos fallidos: {total_methods - successful_methods}")
        
        if self.method_stats:
            # Mostrar detalles de cada método
            self.logger.info("")
            self.logger.info("📋 DETALLE POR MÉTODO:")
            for method_name, stats in self.method_stats.items():
                status = "✅ OK" if stats.get('success', False) else "❌ FALLO"
                elapsed = stats.get('elapsed_time', 0)
                self.logger.info(f"   {method_name}: {status} ({elapsed:.1f}s)")
                
                if not stats.get('success', False) and stats.get('error_info'):
                    self.logger.info(f"      Error: {stats['error_info'][:100]}...")
        
        # Guardar resumen en JSON
        self.save_session_summary()
    
    def save_session_summary(self):
        """Guarda resumen de la sesión en JSON"""
        summary_file = self.log_dir / f"session_summary_{self.session_timestamp}.json"
        
        summary_data = {
            'session_timestamp': self.session_timestamp,
            'total_methods': len(self.method_stats),
            'successful_methods': sum(1 for stats in self.method_stats.values() if stats.get('success', False)),
            'methods': {}
        }
        
        for method_name, stats in self.method_stats.items():
            # Convertir datetime a string para JSON
            stats_copy = stats.copy()
            for key in ['start_time', 'end_time']:
                if key in stats_copy and stats_copy[key]:
                    stats_copy[key] = stats_copy[key].isoformat()
            
            summary_data['methods'][method_name] = stats_copy
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Resumen guardado: {summary_file.name}")
        except Exception as e:
            self.logger.error(f"❌ Error guardando resumen: {e}")
    
    def check_dependencies(self):
        """Verifica dependencias críticas"""
        self.logger.debug("🔍 Verificando dependencias...")
        
        dependencies = [
            'faster_whisper',
            'torch',
            'subprocess',
            'pathlib'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep)
                self.logger.debug(f"   ✅ {dep}")
            except ImportError:
                self.logger.warning(f"   ⚠️ {dep} no disponible")
    
    def get_file_size_mb(self, file_path):
        """Obtiene el tamaño de archivo en MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0
    
    def get_log_files(self):
        """Retorna lista de archivos de log de esta sesión"""
        return {
            'general': self.log_dir / f"transcription_{self.session_timestamp}.log",
            'errors': self.log_dir / f"errors_{self.session_timestamp}.log",
            'summary': self.log_dir / f"session_summary_{self.session_timestamp}.json"
        }

# Instancia global del logger
_transcription_logger = None

def get_logger():
    """Obtiene la instancia global del logger"""
    global _transcription_logger
    if _transcription_logger is None:
        _transcription_logger = TranscriptionLogger()
    return _transcription_logger

def setup_logging(log_dir="logs", console_level=logging.INFO, file_level=logging.DEBUG):
    """Configura el sistema de logging global"""
    global _transcription_logger
    _transcription_logger = TranscriptionLogger(log_dir, console_level, file_level)
    return _transcription_logger