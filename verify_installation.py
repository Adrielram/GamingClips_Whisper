#!/usr/bin/env python3
"""
🔍 Verificador de Instalación VAD System
========================================

Script para verificar que todos los componentes del sistema
VAD Híbrido y Contextual estén correctamente instalados.

Autor: GameClipping Team
Fecha: Septiembre 2025
Versión: 2.0
"""

import sys
import os
import importlib
from pathlib import Path
import json

def print_header():
    """Imprime header del verificador"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                🔍 Verificador VAD System v2.0                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando Python...")
    
    version = sys.version_info
    print(f"   Versión: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Error: Se requiere Python 3.8 o superior")
        return False
    else:
        print("   ✅ Versión de Python compatible")
        return True

def check_module(module_name, display_name, required=True):
    """Verifica si un módulo está disponible"""
    try:
        importlib.import_module(module_name)
        print(f"   ✅ {display_name}")
        return True
    except ImportError as e:
        if required:
            print(f"   ❌ {display_name} - {e}")
        else:
            print(f"   ⚠️ {display_name} - Opcional: {e}")
        return False

def check_basic_dependencies():
    """Verifica dependencias básicas"""
    print("📦 Verificando dependencias básicas...")
    
    basic_modules = [
        ("numpy", "NumPy", True),
        ("torch", "PyTorch", True),
        ("faster_whisper", "Faster-Whisper", False),
    ]
    
    all_ok = True
    for module, name, required in basic_modules:
        if not check_module(module, name, required) and required:
            all_ok = False
    
    return all_ok

def check_vad_models():
    """Verifica modelos VAD"""
    print("🎯 Verificando modelos VAD...")
    
    vad_modules = [
        ("silero_vad", "Silero VAD", True),
        ("webrtcvad", "WebRTC VAD", True),
        ("pyannote.audio", "PyAnnote Audio", False),
    ]
    
    vad_ok = 0
    for module, name, required in vad_modules:
        if check_module(module, name, required):
            vad_ok += 1
    
    if vad_ok >= 2:
        print(f"   ✅ {vad_ok} modelos VAD disponibles (mínimo 2 requeridos)")
        return True
    else:
        print(f"   ❌ Solo {vad_ok} modelos VAD disponibles (mínimo 2 requeridos)")
        return False

def check_audio_processing():
    """Verifica librerías de procesamiento de audio"""
    print("🎵 Verificando procesamiento de audio...")
    
    audio_modules = [
        ("librosa", "Librosa", True),
        ("soundfile", "SoundFile", True),
        ("scipy", "SciPy", False),
    ]
    
    audio_ok = True
    for module, name, required in audio_modules:
        if not check_module(module, name, required) and required:
            audio_ok = False
    
    return audio_ok

def check_machine_learning():
    """Verifica librerías de machine learning"""
    print("🧠 Verificando machine learning...")
    
    ml_modules = [
        ("sklearn", "Scikit-learn", False),
        ("optuna", "Optuna", False),
    ]
    
    for module, name, required in ml_modules:
        check_module(module, name, required)
    
    return True  # No es crítico

def check_system_files():
    """Verifica archivos del sistema"""
    print("📁 Verificando archivos del sistema...")
    
    required_files = [
        "vad_hybrid.py",
        "vad_contextual.py", 
        "transcribe_vad_advanced.py",
        "adaptive_learning.py",
    ]
    
    optional_files = [
        "transcribe_multipass.py",
        "README_VAD_ADVANCED.md",
    ]
    
    all_files_ok = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Archivo requerido faltante")
            all_files_ok = False
    
    for file in optional_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ⚠️ {file} - Archivo opcional faltante")
    
    return all_files_ok

def check_directories():
    """Verifica directorios necesarios"""
    print("📂 Verificando directorios...")
    
    required_dirs = [
        "models_cache",
        "output", 
        "temp",
        "learning_models",
    ]
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"   ✅ {directory}/")
        else:
            print(f"   ⚠️ {directory}/ - Creando directorio...")
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"      ✅ {directory}/ creado")
            except Exception as e:
                print(f"      ❌ Error creando {directory}/: {e}")
    
    return True

def test_vad_hybrid():
    """Prueba el VAD híbrido"""
    print("🔧 Probando VAD Híbrido...")
    
    try:
        from vad_hybrid import HybridVAD, create_gaming_vad_config
        
        # Crear configuración
        config = create_gaming_vad_config()
        print("   ✅ Configuración gaming creada")
        
        # Intentar inicializar VAD
        vad = HybridVAD(config)
        print(f"   ✅ VAD Híbrido inicializado con {len(vad.models)} modelos")
        
        # Probar con audio sintético
        import numpy as np
        test_audio = np.random.randn(16000)  # 1 segundo de audio
        
        results = vad.detect_speech_activity(test_audio, 16000)
        print(f"   ✅ Detección VAD funcionando ({len(results)} segmentos detectados)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en VAD Híbrido: {e}")
        return False

def test_contextual_vad():
    """Prueba el VAD contextual"""
    print("🧠 Probando VAD Contextual...")
    
    try:
        from vad_contextual import ContextualVAD, GamingContext
        
        # Crear VAD contextual
        contextual_vad = ContextualVAD("test_user")
        print("   ✅ VAD Contextual inicializado")
        
        # Probar extracción de características
        import numpy as np
        test_audio = np.random.randn(16000)  # 1 segundo
        
        features = contextual_vad.extract_audio_features(test_audio, 16000)
        print("   ✅ Extracción de características funcionando")
        
        # Probar clasificación
        context_result = contextual_vad.classify_gaming_context(features)
        print(f"   ✅ Clasificación contextual funcionando ({context_result.context_type.value})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en VAD Contextual: {e}")
        return False

def test_advanced_transcriber():
    """Prueba el transcriptor avanzado"""
    print("🚀 Probando Transcriptor Avanzado...")
    
    try:
        from transcribe_vad_advanced import AdvancedTranscriber, create_advanced_config
        
        # Crear configuración
        config = create_advanced_config("fast")  # Usar configuración rápida para prueba
        print("   ✅ Configuración avanzada creada")
        
        # Inicializar transcriptor
        transcriber = AdvancedTranscriber(config)
        print("   ✅ Transcriptor Avanzado inicializado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Transcriptor Avanzado: {e}")
        return False

def test_adaptive_learning():
    """Prueba el sistema de aprendizaje"""
    print("📚 Probando Aprendizaje Adaptativo...")
    
    try:
        from adaptive_learning import AdaptiveLearningSystem, create_learning_session
        from vad_contextual import GamingContext
        
        # Crear sistema de aprendizaje
        learning_system = AdaptiveLearningSystem(enable_online_learning=False)
        print("   ✅ Sistema de aprendizaje inicializado")
        
        # Crear sesión de prueba
        session = create_learning_session(
            user_id="test_user",
            audio_features={'spectral_centroid': 2000, 'rms_energy': 0.3},
            gaming_context=GamingContext.COMBAT,
            vad_params={'silero_threshold': 0.5},
            transcription_quality=0.8,
            vad_accuracy=0.85,
            processing_time=10.0,
            context_confidence=0.75
        )
        
        # Añadir sesión
        learning_system.add_learning_session(session)
        print("   ✅ Sesión de aprendizaje añadida")
        
        # Obtener recomendaciones
        recommendations = learning_system.get_user_recommendations("test_user")
        print("   ✅ Recomendaciones generadas")
        
        learning_system.shutdown()
        return True
        
    except Exception as e:
        print(f"   ❌ Error en Aprendizaje Adaptativo: {e}")
        return False

def check_disk_space():
    """Verifica espacio en disco"""
    print("💾 Verificando espacio en disco...")
    
    try:
        import shutil
        free_space = shutil.disk_usage('.').free / (1024**3)  # GB
        print(f"   📊 Espacio libre: {free_space:.1f} GB")
        
        if free_space < 2.0:
            print("   ⚠️ Advertencia: Poco espacio libre (mínimo 2GB recomendado)")
            return False
        else:
            print("   ✅ Espacio en disco suficiente")
            return True
            
    except Exception as e:
        print(f"   ⚠️ No se pudo verificar espacio: {e}")
        return True

def check_memory():
    """Verifica memoria disponible"""
    print("🧠 Verificando memoria...")
    
    try:
        import psutil
        available_memory = psutil.virtual_memory().available / (1024**3)  # GB
        print(f"   📊 Memoria disponible: {available_memory:.1f} GB")
        
        if available_memory < 4.0:
            print("   ⚠️ Advertencia: Poca memoria (mínimo 4GB recomendado)")
            print("      💡 Sugerencia: Usar perfil 'fast' para reducir uso de memoria")
            return False
        else:
            print("   ✅ Memoria suficiente")
            return True
            
    except ImportError:
        print("   ⚠️ psutil no disponible, no se puede verificar memoria")
        return True
    except Exception as e:
        print(f"   ⚠️ Error verificando memoria: {e}")
        return True

def generate_report(results):
    """Genera reporte de verificación"""
    print("📄 Generando reporte...")
    
    report = {
        "verification_date": str(Path(__file__).stat().st_mtime),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "system_checks": results,
        "overall_status": "OK" if all(results.values()) else "ISSUES_FOUND",
        "recommendations": []
    }
    
    # Añadir recomendaciones basadas en resultados
    if not results.get("basic_dependencies", True):
        report["recommendations"].append("Instalar dependencias básicas: pip install torch numpy")
    
    if not results.get("vad_models", True):
        report["recommendations"].append("Instalar modelos VAD: pip install silero-vad webrtcvad")
    
    if not results.get("audio_processing", True):
        report["recommendations"].append("Instalar procesamiento audio: pip install librosa soundfile")
    
    if not results.get("disk_space", True):
        report["recommendations"].append("Liberar espacio en disco (mínimo 2GB)")
    
    if not results.get("memory", True):
        report["recommendations"].append("Usar perfil 'fast' o aumentar memoria RAM")
    
    # Guardar reporte
    report_path = "verification_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"   ✅ Reporte guardado: {report_path}")
    except Exception as e:
        print(f"   ⚠️ Error guardando reporte: {e}")

def main():
    """Función principal de verificación"""
    print_header()
    
    # Diccionario para almacenar resultados
    results = {}
    
    # Verificaciones del sistema
    results["python_version"] = check_python_version()
    print()
    
    results["basic_dependencies"] = check_basic_dependencies()
    print()
    
    results["vad_models"] = check_vad_models()
    print()
    
    results["audio_processing"] = check_audio_processing()
    print()
    
    results["machine_learning"] = check_machine_learning()
    print()
    
    results["system_files"] = check_system_files()
    print()
    
    results["directories"] = check_directories()
    print()
    
    results["disk_space"] = check_disk_space()
    print()
    
    results["memory"] = check_memory()
    print()
    
    # Pruebas funcionales (solo si los básicos están OK)
    if results["basic_dependencies"] and results["vad_models"]:
        print("🧪 Ejecutando pruebas funcionales...")
        print()
        
        results["vad_hybrid_test"] = test_vad_hybrid()
        print()
        
        results["contextual_vad_test"] = test_contextual_vad()
        print()
        
        results["advanced_transcriber_test"] = test_advanced_transcriber()
        print()
        
        results["adaptive_learning_test"] = test_adaptive_learning()
        print()
    else:
        print("⚠️ Saltando pruebas funcionales debido a dependencias faltantes")
        print()
    
    # Generar reporte
    generate_report(results)
    print()
    
    # Resumen final
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                         📊 RESUMEN FINAL                        ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # Contar éxitos y fallos
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"📈 Verificaciones: {passed_checks}/{total_checks} exitosas")
    
    if passed_checks == total_checks:
        print("🎉 ¡Sistema completamente funcional!")
        print()
        print("🚀 Listo para usar:")
        print("   • python transcribe_vad_advanced.py audio.wav")
        print("   • transcribe_gaming.bat audio.wav")
        print("   • transcribe_precision.bat audio.wav")
        return 0
    else:
        print("⚠️ Se encontraron problemas que requieren atención")
        print()
        print("💡 Próximos pasos:")
        
        if not results.get("basic_dependencies", True):
            print("   1. Instalar dependencias básicas")
        
        if not results.get("vad_models", True):
            print("   2. Instalar modelos VAD")
        
        if not results.get("audio_processing", True):
            print("   3. Instalar librerías de audio")
        
        print("   4. Ejecutar nuevamente: python verify_installation.py")
        print()
        print("📚 Consultar: README_VAD_ADVANCED.md para troubleshooting")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    
    print()
    input("Presiona Enter para salir...")
    sys.exit(exit_code)