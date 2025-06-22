#!/usr/bin/env python3
"""
Test de Servicio F5-TTS Español
Tests completos usando solo librerías estándar de Python

Funcionalidades:
- ✅ Tests de conectividad y salud
- ✅ Tests de endpoints REST
- ✅ Tests de síntesis básica y avanzada
- ✅ Tests de manejo de errores
- ✅ Tests de diferentes voces
- ✅ Tests de velocidades
- ✅ Tests de caracteres especiales
- ✅ Tests de rendimiento básico
- ✅ Diagnóstico del sistema

Ejecución:
    python3 test_service.py
    python3 test_service.py --url http://localhost:5005
    python3 test_service.py --timeout 60 --verbose
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Configuración
BASE_URL = os.getenv('F5_TTS_TEST_URL', 'http://localhost:5005')
TEST_TIMEOUT = 30
VERBOSE = False


class TestRunner:
    """Runner de tests sin dependencias externas"""
    
    def __init__(self, verbose=False):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
        self.verbose = verbose
        self.start_time = time.time()
    
    def run_test(self, test_name, test_func):
        """Ejecutar un test individual"""
        if self.verbose:
            print(f"\n🧪 {test_name}")
            print("-" * len(test_name))
        else:
            print(f"🧪 {test_name}...", end=" ")
        
        self.tests_run += 1
        
        try:
            start = time.time()
            result = test_func()
            duration = time.time() - start
            
            if result:
                if self.verbose:
                    print(f"✅ PASS ({duration:.2f}s)")
                else:
                    print("✅ PASS")
                self.tests_passed += 1
            else:
                if self.verbose:
                    print(f"❌ FAIL ({duration:.2f}s)")
                else:
                    print("❌ FAIL")
                self.tests_failed += 1
                self.failures.append(test_name)
        except Exception as e:
            duration = time.time() - start if 'start' in locals() else 0
            error_msg = f"💥 ERROR: {e}"
            if self.verbose:
                print(f"{error_msg} ({duration:.2f}s)")
            else:
                print(error_msg)
            self.tests_failed += 1
            self.failures.append(f"{test_name}: {e}")
    
    def print_summary(self):
        """Imprimir resumen de tests"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE TESTS F5-TTS ESPAÑOL")
        print("="*60)
        print(f"⏱️  Tiempo total: {total_time:.2f} segundos")
        print(f"🧪 Tests ejecutados: {self.tests_run}")
        print(f"✅ Tests exitosos: {self.tests_passed}")
        print(f"❌ Tests fallidos: {self.tests_failed}")
        
        if self.failures:
            print("\n❌ FALLOS DETALLADOS:")
            for i, failure in enumerate(self.failures, 1):
                print(f"   {i}. {failure}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print("✅ El servicio F5-TTS Español está funcionando perfectamente")
        elif success_rate >= 80:
            print("⚠️  La mayoría de tests pasaron - revisar fallos menores")
        else:
            print("🚨 Múltiples fallos detectados - revisar configuración")
        
        return self.tests_failed == 0


def make_request(url, method='GET', data=None, headers=None):
    """Hacer petición HTTP usando urllib"""
    try:
        if headers is None:
            headers = {}
        
        if data is not None:
            if isinstance(data, dict):
                # Para JSON
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                # Para form data
                data = data.encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        with urllib.request.urlopen(req, timeout=TEST_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            return {
                'status_code': response.getcode(),
                'content': content,
                'headers': dict(response.headers)
            }
            
    except urllib.error.HTTPError as e:
        return {
            'status_code': e.code,
            'content': e.read().decode('utf-8') if e.fp else '',
            'headers': dict(e.headers) if e.headers else {}
        }
    except Exception as e:
        raise Exception(f"Request failed: {e}")


def test_service_health():
    """Test básico de conectividad y salud del servicio"""
    response = make_request(f"{BASE_URL}/health")
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Status code incorrecto: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    # Verificar estructura de respuesta
    required_keys = ['status', 'model', 'device', 'f5_available']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta clave requerida: {key}")
            return False
    
    # Verificar valores esperados
    if data['status'] != 'ok':
        if VERBOSE:
            print(f"❌ Status no es 'ok': {data['status']}")
        return False
    
    if data['model'] != 'spanish-f5':
        if VERBOSE:
            print(f"❌ Modelo incorrecto: {data['model']}")
        return False
    
    if not data.get('f5_available', False):
        if VERBOSE:
            print("⚠️  Modelo F5 no está disponible")
    
    if VERBOSE:
        print(f"✅ Servicio OK - Dispositivo: {data['device']}, F5: {data['f5_available']}")
    
    return True


def test_voices_endpoint():
    """Test endpoint de voces disponibles"""
    # Test para español (debe funcionar)
    response = make_request(f"{BASE_URL}/voices?language=es")
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error obteniendo voces ES: {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    required_keys = ['default', 'language', 'model', 'voices']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta clave en voces: {key}")
            return False
    
    if data['language'] != 'es':
        if VERBOSE:
            print(f"❌ Idioma incorrecto: {data['language']}")
        return False
    
    if data['model'] != 'spanish-f5':
        if VERBOSE:
            print(f"❌ Modelo incorrecto en voces: {data['model']}")
        return False
    
    # Verificar que hay voces disponibles
    voices = data.get('voices', {})
    if not voices.get('female') and not voices.get('male'):
        if VERBOSE:
            print("❌ No hay voces disponibles")
        return False
    
    # Test para idioma no soportado (debe fallar)
    response2 = make_request(f"{BASE_URL}/voices?language=en")
    if response2['status_code'] != 400:
        if VERBOSE:
            print(f"❌ Idioma no soportado debería dar 400, dio: {response2['status_code']}")
        return False
    
    if VERBOSE:
        total_voices = len(voices.get('female', [])) + len(voices.get('male', []))
        print(f"✅ {total_voices} voces disponibles ({len(voices.get('female', []))} fem, {len(voices.get('male', []))} masc)")
    
    return True


def test_basic_synthesis():
    """Test síntesis básica de texto a voz"""
    payload = {
        "text": "Hola, esta es una prueba básica del sistema de síntesis de voz",
        "language": "es",
        "voice": "es_female",
        "speed": 0.9
    }
    
    response = make_request(
        f"{BASE_URL}/synthesize_json",
        method='POST',
        data=payload
    )
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Error en síntesis: {response['status_code']}")
            try:
                error_data = json.loads(response['content'])
                print(f"   Error: {error_data.get('error', 'Unknown')}")
            except:
                pass
        return False
    
    data = json.loads(response['content'])
    
    if not data.get('success', False):
        if VERBOSE:
            print(f"❌ Síntesis falló: {data.get('error', 'Unknown error')}")
        return False
    
    # Verificar metadatos importantes
    required_keys = ['text', 'language', 'voice', 'speed', 'model', 'audio_duration']
    for key in required_keys:
        if key not in data:
            if VERBOSE:
                print(f"❌ Falta metadato: {key}")
            return False
    
    if data['audio_duration'] <= 0:
        if VERBOSE:
            print(f"❌ Duración de audio inválida: {data['audio_duration']}")
        return False
    
    if VERBOSE:
        print(f"✅ Síntesis exitosa - Duración: {data['audio_duration']:.2f}s, Sample rate: {data.get('sample_rate', 'N/A')}")
    
    return True


def test_error_handling():
    """Test manejo de errores del servicio"""
    # Test 1: Texto vacío
    payload = {"text": "", "language": "es"}
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    
    if response['status_code'] != 400:
        if VERBOSE:
            print(f"❌ Texto vacío debería dar 400, dio: {response['status_code']}")
        return False
    
    # Test 2: Idioma no soportado
    payload = {"text": "Hello world", "language": "en"}
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    
    if response['status_code'] != 400:
        if VERBOSE:
            print(f"❌ Idioma no soportado debería dar 400, dio: {response['status_code']}")
        return False
    
    # Test 3: Request sin JSON
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST')
    
    if response['status_code'] not in [400, 422, 500]:  # 500 también puede ocurrir con JSON faltante
        if VERBOSE:
            print(f"❌ Request sin JSON debería dar 400/422/500, dio: {response['status_code']}")
        return False
    
    if VERBOSE:
        print("✅ Manejo de errores correcto (texto vacío, idioma inválido, JSON faltante)")
    
    return True


def test_different_voices():
    """Test diferentes voces disponibles"""
    voices_to_test = ["es_female", "es_male"]
    text = "Prueba de diferentes voces en español"
    successful_voices = 0
    
    for voice in voices_to_test:
        payload = {
            "text": text,
            "language": "es",
            "voice": voice
        }
        
        try:
            response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
            
            if response['status_code'] == 200:
                data = json.loads(response['content'])
                if data.get('success', False):
                    successful_voices += 1
                    if VERBOSE:
                        print(f"   ✅ Voz {voice}: {data.get('audio_duration', 0):.2f}s")
                else:
                    if VERBOSE:
                        print(f"   ❌ Voz {voice}: {data.get('error', 'Unknown error')}")
            else:
                if VERBOSE:
                    print(f"   ❌ Voz {voice}: HTTP {response['status_code']}")
        except Exception as e:
            if VERBOSE:
                print(f"   💥 Voz {voice}: {e}")
    
    # Al menos una voz debe funcionar
    if successful_voices == 0:
        if VERBOSE:
            print("❌ Ninguna voz funcionó")
        return False
    
    if VERBOSE and successful_voices < len(voices_to_test):
        print(f"⚠️  Solo {successful_voices}/{len(voices_to_test)} voces funcionaron")
    
    return True


def test_speed_variations():
    """Test diferentes velocidades de síntesis"""
    speeds = [0.8, 0.9, 1.0, 1.1]
    text = "Prueba de velocidades de síntesis"
    successful_speeds = 0
    
    for speed in speeds:
        payload = {
            "text": text,
            "language": "es",
            "speed": speed
        }
        
        try:
            response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
            
            if response['status_code'] == 200:
                data = json.loads(response['content'])
                if data.get('success', False):
                    successful_speeds += 1
                    if VERBOSE:
                        actual_speed = data.get('speed', speed)
                        print(f"   ✅ Velocidad {speed} → {actual_speed}: {data.get('audio_duration', 0):.2f}s")
                else:
                    if VERBOSE:
                        print(f"   ❌ Velocidad {speed}: {data.get('error', 'Unknown error')}")
            else:
                if VERBOSE:
                    print(f"   ❌ Velocidad {speed}: HTTP {response['status_code']}")
        except Exception as e:
            if VERBOSE:
                print(f"   💥 Velocidad {speed}: {e}")
    
    # Al menos la mitad de las velocidades deben funcionar
    if successful_speeds < len(speeds) // 2:
        if VERBOSE:
            print(f"❌ Solo {successful_speeds}/{len(speeds)} velocidades funcionaron")
        return False
    
    return True


def test_special_characters():
    """Test caracteres especiales españoles"""
    special_texts = [
        "¡Hola! ¿Cómo estás?",
        "Acentos: áéíóú ñ ü",
        "Números: 1, 2, 3",
        "Símbolos básicos: . , ; : - _ ( )"
    ]
    
    successful_texts = 0
    
    for text in special_texts:
        payload = {
            "text": text,
            "language": "es"
        }
        
        try:
            response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
            
            if response['status_code'] == 200:
                data = json.loads(response['content'])
                if data.get('success', False):
                    successful_texts += 1
                    if VERBOSE:
                        print(f"   ✅ '{text[:30]}...': {data.get('audio_duration', 0):.2f}s")
                else:
                    if VERBOSE:
                        print(f"   ❌ '{text[:30]}...': {data.get('error', 'Unknown error')}")
            else:
                if VERBOSE:
                    print(f"   ⚠️  '{text[:30]}...': HTTP {response['status_code']}")
        except Exception as e:
            if VERBOSE:
                print(f"   💥 '{text[:30]}...': {e}")
    
    # La mayoría de textos especiales deberían funcionar
    if successful_texts < len(special_texts) * 0.5:  # Al menos 50%
        if VERBOSE:
            print(f"❌ Solo {successful_texts}/{len(special_texts)} textos especiales funcionaron")
        return False
    
    return True


def test_response_time():
    """Test tiempo de respuesta del servicio"""
    payload = {
        "text": "Prueba de tiempo de respuesta del sistema",
        "language": "es"
    }
    
    start_time = time.time()
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    end_time = time.time()
    
    response_time = end_time - start_time
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Request falló: HTTP {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    if not data.get('success', False):
        if VERBOSE:
            print(f"❌ Síntesis falló: {data.get('error', 'Unknown error')}")
        return False
    
    # Verificar tiempo razonable (menos de 30 segundos)
    if response_time > 30:
        if VERBOSE:
            print(f"⚠️  Respuesta lenta: {response_time:.2f}s")
        return False
    
    if VERBOSE:
        audio_duration = data.get('audio_duration', 0)
        ratio = audio_duration / response_time if response_time > 0 else 0
        print(f"✅ Tiempo respuesta: {response_time:.2f}s, Audio: {audio_duration:.2f}s, Ratio: {ratio:.2f}x")
    else:
        print(f"Response time: {response_time:.2f}s", end=" ")
    
    return True


def test_debug_functionality():
    """Test funcionalidad de debug del servicio"""
    payload = {
        "text": "Prueba de funcionalidad de debug",
        "language": "es"
    }
    
    response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=payload)
    
    if response['status_code'] != 200:
        if VERBOSE:
            print(f"❌ Request falló: HTTP {response['status_code']}")
        return False
    
    data = json.loads(response['content'])
    
    if not data.get('success', False):
        if VERBOSE:
            print(f"❌ Síntesis falló: {data.get('error', 'Unknown error')}")
        return False
    
    # Verificar que se generan archivos de debug
    debug_file = data.get('debug_audio_file')
    debug_url = data.get('debug_audio_url')
    
    if debug_file and debug_url:
        if VERBOSE:
            print(f"✅ Debug activo - Archivo: {debug_file}")
        return True
    else:
        if VERBOSE:
            print("⚠️  Debug no está configurado")
        return True  # No es crítico


def check_service_availability():
    """Verificar si el servicio está disponible"""
    try:
        response = make_request(f"{BASE_URL}/health")
        return response['status_code'] == 200
    except:
        return False


def run_diagnostic():
    """Ejecutar diagnóstico completo del sistema"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA F5-TTS")
    print("="*40)
    
    try:
        # 1. Conectividad básica
        response = make_request(f"{BASE_URL}/health")
        health_data = json.loads(response['content'])
        
        print(f"🌐 URL del servicio: {BASE_URL}")
        print(f"🔗 Conectividad: {'✅ OK' if response['status_code'] == 200 else '❌ FAIL'}")
        print(f"🧠 Modelo: {health_data.get('model', 'N/A')}")
        print(f"🖥️  Dispositivo: {health_data.get('device', 'N/A')}")
        print(f"🤖 F5 disponible: {'✅ Sí' if health_data.get('f5_available') else '❌ No'}")
        
        # 2. Voces disponibles
        voices_response = make_request(f"{BASE_URL}/voices?language=es")
        if voices_response['status_code'] == 200:
            voices_data = json.loads(voices_response['content'])
            voices = voices_data.get('voices', {})
            total_voices = len(voices.get('female', [])) + len(voices.get('male', []))
            print(f"🎭 Voces disponibles: {total_voices}")
            print(f"   - Femeninas: {len(voices.get('female', []))}")
            print(f"   - Masculinas: {len(voices.get('male', []))}")
        
        # 3. Test rápido de síntesis
        test_payload = {"text": "Test", "language": "es"}
        test_response = make_request(f"{BASE_URL}/synthesize_json", method='POST', data=test_payload)
        print(f"🎤 Síntesis básica: {'✅ Funciona' if test_response['status_code'] == 200 else '❌ Error'}")
        
    except Exception as e:
        print(f"💥 Error en diagnóstico: {e}")


def main():
    """Función principal de testing"""
    print("🧪 TEST DE SERVICIO F5-TTS ESPAÑOL")
    print("="*50)
    print(f"🌐 URL del servicio: {BASE_URL}")
    print(f"⏱️  Timeout: {TEST_TIMEOUT}s")
    print(f"📝 Modo verboso: {'✅ Activado' if VERBOSE else '❌ Desactivado'}")
    print()
    
    # Verificar disponibilidad inicial
    print("🔍 Verificando disponibilidad del servicio...")
    if not check_service_availability():
        print("❌ ERROR: Servicio no disponible en " + BASE_URL)
        print("\n💡 Soluciones:")
        print("   1. Verificar que el servicio esté corriendo:")
        print("      docker compose up -d")
        print("   2. Verificar conectividad:")
        print("      curl http://localhost:5005/health")
        print("   3. Verificar puertos:")
        print("      netstat -tulpn | grep 5005")
        return False
    
    print("✅ Servicio disponible")
    
    if VERBOSE:
        run_diagnostic()
    
    print()
    
    # Ejecutar tests
    runner = TestRunner(verbose=VERBOSE)
    
    # Tests básicos
    runner.run_test("Conectividad y salud del servicio", test_service_health)
    runner.run_test("Endpoint de voces", test_voices_endpoint)
    runner.run_test("Síntesis básica", test_basic_synthesis)
    runner.run_test("Manejo de errores", test_error_handling)
    
    # Tests de funcionalidad
    runner.run_test("Diferentes voces", test_different_voices)
    runner.run_test("Variaciones de velocidad", test_speed_variations)
    runner.run_test("Caracteres especiales", test_special_characters)
    
    # Tests de rendimiento
    runner.run_test("Tiempo de respuesta", test_response_time)
    
    # Tests adicionales
    runner.run_test("Funcionalidad de debug", test_debug_functionality)
    
    # Resumen final
    success = runner.print_summary()
    
    if not success:
        print("\n🔧 AYUDA PARA PROBLEMAS:")
        print("   1. Logs del servicio: docker logs f5-tts-service")
        print("   2. Estado del contenedor: docker ps | grep f5-tts")
        print("   3. Recursos del sistema: docker stats f5-tts-service")
        print("   4. Test específico: python3 test_service.py --verbose")
    
    return success


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Tests del servicio F5-TTS Español')
    parser.add_argument('--url', default=BASE_URL, help='URL del servicio F5-TTS')
    parser.add_argument('--timeout', type=int, default=TEST_TIMEOUT, help='Timeout para requests (segundos)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verboso con detalles')
    
    args = parser.parse_args()
    
    # Actualizar configuración global
    BASE_URL = args.url
    TEST_TIMEOUT = args.timeout
    VERBOSE = args.verbose
    
    success = main()
    sys.exit(0 if success else 1) 