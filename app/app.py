#!/usr/bin/env python3
"""
Servicio F5-TTS Español usando repositorio oficial Spanish-F5
https://github.com/jpgallegoar/Spanish-F5
"""

import os
import io
import gc
import sys
import time
import uuid
import logging
import soundfile as sf
import numpy as np
from flask import Flask, request, jsonify, send_file
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables globales - usar variables de entorno
f5_model = None
device = "cuda" if os.system("nvidia-smi > /dev/null 2>&1") == 0 else "cpu"
model_name = os.getenv('F5_MODEL', 'jpgallegoar/F5-Spanish')
debug_dir = "/app/debug_audio"

# Configuración de voces españolas
SPANISH_VOICES = {
    'default': os.getenv('DEFAULT_VOICE', 'es_female'),
    'language': os.getenv('DEFAULT_LANGUAGE', 'es'),
    'model': 'spanish-f5',
    'voices': {
        'default': os.getenv('DEFAULT_VOICE', 'es_female'),
        'female': ['es_female', 'es_maria', 'es_elena', 'es_sofia'],
        'male': ['es_male', 'es_carlos', 'es_diego', 'es_pablo']
    }
}

def initialize_spanish_f5():
    """Inicializar el modelo Spanish-F5 oficial usando el método correcto"""
    global f5_model
    
    try:
        logger.info(f"🇪🇸 Inicializando Spanish-F5 oficial desde HuggingFace")
        logger.info(f"📦 Modelo: {model_name}")
        
        # Crear directorio de debug
        os.makedirs(debug_dir, exist_ok=True)
        
        # Método 1: Intentar cargar directamente desde HuggingFace
        logger.info("⏳ Método 1: Cargando desde HuggingFace Hub...")
        try:
            from huggingface_hub import hf_hub_download
            import torch
            
            # Descargar modelo español específico
            model_path = hf_hub_download(
                repo_id="jpgallegoar/F5-Spanish",
                filename="model_1200000.safetensors",
                cache_dir="/app/models"
            )
            
            logger.info(f"✅ Modelo descargado: {model_path}")
            
            # Inicializar con el modelo español
            from f5_tts.api import F5TTS
            f5_model = F5TTS(
                model_type="F5-TTS",
                ckpt_file=model_path,
                vocab_file=None,  # Usar vocab por defecto
                ode_method="euler",
                use_ema=True,
                device=device
            )
            
            logger.info("✅ Spanish-F5 inicializado con modelo HuggingFace")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Método HuggingFace falló: {e}")
            
        # Método 2: Usar CLI como fallback
        logger.info("⏳ Método 2: Usando CLI como fallback...")
        return initialize_f5_cli_method()
        
    except Exception as e:
        logger.error(f"❌ Error inicializando Spanish-F5: {e}")
        return initialize_f5_cli_method()

def initialize_f5_cli_method():
    """Método alternativo usando comandos CLI de F5-TTS"""
    global f5_model
    
    try:
        logger.info("🔧 Intentando método CLI alternativo...")
        
        # Verificar si f5-tts_infer-cli está disponible
        import subprocess
        result = subprocess.run(['which', 'f5-tts_infer-cli'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ CLI f5-tts_infer-cli disponible")
            f5_model = {"method": "cli", "available": True}
            return True
        else:
            logger.error("❌ CLI no disponible")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en método CLI: {e}")
        return False

def get_reference_audio():
    """Obtener archivo de referencia español"""
    references_dir = "/app/references"
    
    if not os.path.exists(references_dir):
        return None
        
    # Buscar archivos WAV
    import glob
    wav_files = glob.glob(os.path.join(references_dir, "*.wav"))
    
    if wav_files:
        return wav_files[0]  # Usar el primero disponible
    
    return None

def get_reference_text(audio_file):
    """Obtener el texto exacto correspondiente al archivo de referencia"""
    # Mapeo de archivos de referencia a sus textos exactos
    reference_texts = {
        "es_masc_presentacion.wav": "Hola, soy Carlos y esta es mi voz natural hablando en español castellano.",
        "es_masc_tecnico.wav": "La síntesis de texto a voz permite convertir cualquier texto escrito en audio hablado.",
        "es_masc_geografia.wav": "España, México, Argentina, Colombia, Chile, Perú, Venezuela son países hispanohablantes.",
        "es_masc_tiempo.wav": "Hoy hace sol, ayer llovió, mañana estará nublado, la temperatura es agradable.",
        "es_masc_despedida.wav": "Gracias por escuchar esta grabación de referencia para el sistema de síntesis de voz."
    }
    
    # Obtener nombre del archivo
    filename = os.path.basename(audio_file)
    
    # Devolver texto correspondiente o texto genérico
    return reference_texts.get(filename, "Esta es una voz de referencia en español con pronunciación natural.")

def improve_audio_clarity(wav_data, sample_rate):
    """Mejorar la claridad del audio sintetizado"""
    try:
        import numpy as np
        from scipy import signal
        
        logger.info("🔧 Mejorando claridad del audio...")
        
        # Convertir a numpy si no lo es
        if not isinstance(wav_data, np.ndarray):
            wav_data = np.array(wav_data)
        
        # 1. Normalización suave
        max_val = np.max(np.abs(wav_data))
        if max_val > 0:
            wav_data = wav_data / max_val * 0.9
        
        # 2. Filtro pasa-altos suave para remover ruido de baja frecuencia
        nyquist = sample_rate / 2
        low_cutoff = 80 / nyquist  # Cortar por debajo de 80Hz
        b_high, a_high = signal.butter(2, low_cutoff, btype='high')
        wav_data = signal.filtfilt(b_high, a_high, wav_data)
        
        # 3. Realce de frecuencias medias (claridad de voz)
        # Filtro pasa-banda para realzar 1-4kHz (rango de claridad vocal)
        mid_low = 1000 / nyquist
        mid_high = 4000 / nyquist
        b_mid, a_mid = signal.butter(2, [mid_low, mid_high], btype='band')
        mid_enhancement = signal.filtfilt(b_mid, a_mid, wav_data)
        wav_data = wav_data + mid_enhancement * 0.15  # Realce sutil
        
        # 4. Suavizado de picos para evitar distorsión
        wav_data = np.tanh(wav_data * 1.2) * 0.8
        
        # 5. Normalización final
        max_val = np.max(np.abs(wav_data))
        if max_val > 0:
            wav_data = wav_data / max_val * 0.85
        
        logger.info("✅ Claridad mejorada")
        return wav_data
        
    except Exception as e:
        logger.warning(f"⚠️  Error mejorando claridad: {e}, usando audio original")
        return wav_data

def synthesize_spanish_f5(text, voice="es_female", speed=1.0):
    """Sintetizar usando Spanish-F5 oficial"""
    try:
        if f5_model is None:
            raise Exception("Modelo Spanish-F5 no inicializado")
        
        logger.info(f"🎤 Sintetizando con Spanish-F5: '{text[:50]}...'")
        logger.info(f"🎭 Voz: {voice}, Velocidad: {speed}")
        
        # Obtener archivo de referencia
        ref_audio = get_reference_audio()
        if not ref_audio:
            raise Exception("No hay archivos de referencia disponibles")
        
        logger.info(f"📁 Usando referencia: {os.path.basename(ref_audio)}")
        
        # Verificar qué método usar
        if isinstance(f5_model, dict) and f5_model.get("method") == "cli":
            return synthesize_with_cli(text, ref_audio, speed)
        else:
            return synthesize_with_api(text, ref_audio, speed)
        
    except Exception as e:
        logger.error(f"❌ Error en síntesis Spanish-F5: {e}")
        raise e

def synthesize_with_api(text, ref_audio, speed=1.0):
    """Sintetizar usando API correcta de Spanish-F5"""
    try:
        # Obtener el texto exacto del archivo de referencia
        ref_text = get_reference_text(ref_audio)
        logger.info(f"📝 Texto de referencia: '{ref_text[:50]}...'")
        
        # Ajustar velocidad para mejor claridad (Spanish-F5 recomienda 0.8-1.2)
        adjusted_speed = max(0.8, min(1.2, speed))
        
        logger.info(f"🔧 Sintetizando con Spanish-F5 modelo oficial...")
        logger.info(f"🎭 Velocidad ajustada: {adjusted_speed}")
        
        # Usar la API correcta de Spanish-F5 según documentación oficial
        output_audio = f5_model.infer(
            ref_file=ref_audio,
            ref_text=ref_text,
            gen_text=text,
            model="F5-TTS",  # Especificar modelo
            remove_silence=False,  # Spanish-F5 maneja esto internamente
            speed=adjusted_speed
        )
        
        logger.info(f"🔍 Tipo de salida: {type(output_audio)}")
        
        # Manejar diferentes tipos de respuesta
        if isinstance(output_audio, tuple):
            # Si es tupla, extraer según longitud
            if len(output_audio) == 2:
                wav_data, sample_rate = output_audio
            elif len(output_audio) == 3:
                wav_data, sample_rate, _ = output_audio  # Ignorar tercer elemento
            else:
                logger.info(f"⚠️  Tupla con {len(output_audio)} elementos, usando primeros 2")
                wav_data = output_audio[0]
                sample_rate = output_audio[1] if len(output_audio) > 1 else 24000
        else:
            # Si no es tupla, es solo el audio
            wav_data = output_audio
            sample_rate = 24000
        
        logger.info(f"🎵 Audio extraído: tipo={type(wav_data)}, sample_rate={sample_rate}")
        
        # Convertir a numpy si es necesario
        if hasattr(wav_data, 'numpy'):
            wav_data = wav_data.numpy()
        elif hasattr(wav_data, 'cpu'):
            wav_data = wav_data.cpu().numpy()
        elif hasattr(wav_data, 'detach'):
            wav_data = wav_data.detach().cpu().numpy()
        
        # Asegurar que es un array 1D
        if hasattr(wav_data, 'ndim') and wav_data.ndim > 1:
            wav_data = wav_data.squeeze()
        
        # Post-procesar para mejorar claridad
        wav_data = improve_audio_clarity(wav_data, sample_rate)
        
        logger.info(f"✅ Audio procesado y mejorado: {len(wav_data)} samples, {sample_rate}Hz")
        return wav_data, sample_rate
        
    except Exception as e:
        logger.error(f"❌ Error en API: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        raise e

def synthesize_with_cli(text, ref_audio, speed=1.0):
    """Sintetizar usando CLI oficial de Spanish-F5"""
    try:
        import subprocess
        import tempfile
        
        # Obtener el texto exacto del archivo de referencia
        ref_text = get_reference_text(ref_audio)
        logger.info(f"📝 Texto de referencia CLI: '{ref_text[:50]}...'")
        
        # Crear archivo temporal para salida
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            output_file = tmp_file.name
        
        # Comando CLI forzando uso del modelo español específico
        output_dir = os.path.dirname(output_file)
        
        # Buscar el modelo español dinámicamente
        import glob
        spanish_models = glob.glob("/app/models/models--jpgallegoar--F5-Spanish/**/model_1200000.safetensors", recursive=True)
        
        cmd = [
            "f5-tts_infer-cli",
            "-m", "F5-TTS",
            "-r", ref_audio,
            "-s", ref_text,
            "-t", text,
            "-o", output_dir,
            "--speed", str(speed)
        ]
        
        # Si encontramos el modelo español, forzar su uso
        if spanish_models:
            spanish_model_path = spanish_models[0]
            cmd.extend(["-p", spanish_model_path])
            logger.info(f"🇪🇸 Forzando uso del modelo español: {os.path.basename(spanish_model_path)}")
        else:
            logger.warning("⚠️  No se encontró modelo español específico, usando modelo por defecto")
        
        logger.info(f"🔧 Ejecutando Spanish-F5 CLI oficial...")
        logger.info(f"📝 Comando: {' '.join(cmd[:4])}...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        logger.info(f"📋 CLI stdout: {result.stdout}")
        if result.stderr:
            logger.info(f"📋 CLI stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"CLI retornó código {result.returncode}: {result.stderr}")
        
        # Spanish-F5 CLI genera archivos en el directorio de salida
        # Buscar archivos generados en el directorio de salida
        import glob
        
        generated_files = glob.glob(os.path.join(output_dir, "*.wav"))
        
        if generated_files:
            # Usar el archivo más reciente
            latest_file = max(generated_files, key=os.path.getctime)
            wav_data, sample_rate = sf.read(latest_file)
            os.unlink(latest_file)  # Limpiar archivo
            
            logger.info(f"✅ Audio generado con Spanish-F5 CLI: {len(wav_data)} samples, {sample_rate}Hz")
            logger.info(f"📁 Archivo generado: {os.path.basename(latest_file)}")
            return wav_data, sample_rate
        else:
            # Buscar en directorio actual también
            current_dir_files = glob.glob("*.wav")
            if current_dir_files:
                latest_file = max(current_dir_files, key=os.path.getctime)
                wav_data, sample_rate = sf.read(latest_file)
                os.unlink(latest_file)  # Limpiar
                logger.info(f"✅ Audio encontrado en directorio actual: {latest_file}")
                return wav_data, sample_rate
            
            logger.error(f"📂 Archivos en {output_dir}: {os.listdir(output_dir)}")
            raise Exception("No se encontró archivo de salida generado por Spanish-F5 CLI")
            
    except Exception as e:
        logger.error(f"❌ Error en Spanish-F5 CLI: {e}")
        raise e

def save_debug_audio(wav_data, sample_rate, prefix="spanish_f5"):
    """Guardar audio de debug"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{prefix}_{timestamp}.wav"
        filepath = os.path.join(debug_dir, filename)
        
        # Guardar archivo
        sf.write(filepath, wav_data, sample_rate)
        
        logger.info(f"🐛 Debug guardado: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ Error guardando debug: {e}")
        return None

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({
        'status': 'ok',
        'model': 'spanish-f5',
        'device': device,
        'f5_available': f5_model is not None
    })

@app.route('/voices', methods=['GET'])
def get_voices():
    """Obtener voces disponibles"""
    language = request.args.get('language', 'es')
    
    if language == 'es':
        return jsonify(SPANISH_VOICES)
    else:
        return jsonify({
            'error': 'Only Spanish (es) is supported',
            'supported_languages': ['es']
        }), 400

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Endpoint principal de síntesis"""
    try:
        # Obtener parámetros
        text = request.form.get('text', '')
        language = request.form.get('language', 'es')
        voice = request.form.get('voice', 'es_female')
        speed = float(request.form.get('speed', 0.9))  # Velocidad óptima confirmada
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if language != 'es':
            return jsonify({'error': 'Only Spanish (es) is supported'}), 400
        
        logger.info(f"🎯 Síntesis solicitada: '{text[:30]}...' | Voz: {voice}")
        
        # Sintetizar
        wav_data, sample_rate = synthesize_spanish_f5(text, voice, speed)
        
        # Crear respuesta de audio
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, wav_data, sample_rate, format='WAV')
        audio_buffer.seek(0)
        
        # Guardar debug
        debug_file = save_debug_audio(wav_data, sample_rate)
        
        return send_file(
            audio_buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='spanish_synthesis.wav'
        )
        
    except Exception as e:
        logger.error(f"❌ Error en síntesis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/synthesize_json', methods=['POST'])
def synthesize_json():
    """Endpoint de síntesis con respuesta JSON"""
    try:
        # Obtener parámetros JSON
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        text = data.get('text', '')
        language = data.get('language', 'es')
        voice = data.get('voice', 'es_female')
        speed = float(data.get('speed', 0.9))  # Velocidad óptima confirmada
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        if language != 'es':
            return jsonify({'error': 'Only Spanish (es) is supported'}), 400
        
        logger.info(f"🎯 Síntesis JSON: '{text[:30]}...' | Voz: {voice}")
        
        # Sintetizar
        wav_data, sample_rate = synthesize_spanish_f5(text, voice, speed)
        
        # Guardar debug
        debug_file = save_debug_audio(wav_data, sample_rate)
        
        # Calcular duración
        duration = len(wav_data) / sample_rate
        
        return jsonify({
            'success': True,
            'text': text,
            'language': language,
            'voice': voice,
            'speed': speed,
            'model': 'spanish-f5',
            'sample_rate': sample_rate,
            'audio_duration': duration,
            'f5_available': True,
            'debug_audio_file': debug_file,
            'debug_audio_url': f'/debug/audio/{debug_file}' if debug_file else None
        })
        
    except Exception as e:
        logger.error(f"❌ Error en síntesis JSON: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'f5_available': f5_model is not None
        }), 500

@app.route('/debug/audio/<filename>')
def serve_debug_audio(filename):
    """Servir archivos de audio de debug"""
    try:
        filepath = os.path.join(debug_dir, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='audio/wav')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando servicio Spanish-F5...")
    
    # Inicializar modelo
    if initialize_spanish_f5():
        logger.info("✅ Servicio listo para usar")
    else:
        logger.error("❌ Error inicializando modelo")
        sys.exit(1)
    
    # Obtener configuración desde variables de entorno
    flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
    flask_port = int(os.getenv('FLASK_PORT', 5005))
    
    logger.info(f"🌐 Iniciando servidor en {flask_host}:{flask_port}")
    
    # Iniciar servidor
    app.run(host=flask_host, port=flask_port, debug=False) 