# F5-TTS Español 🇪🇸

Servicio de síntesis de voz Text-to-Speech usando **[Spanish-F5](https://github.com/jpgallegoar/Spanish-F5)** oficial.

## ✨ Características

- **Acento español natural**: Resuelve el problema de acento inglés usando modelo español específico
- **Velocidad optimizada**: Configuración 0.9x por defecto (confirmada como óptima)
- **Modelo forzado**: Usa exclusivamente el modelo Spanish-F5 (no modelos base ingleses)
- **Archivos de referencia**: Usa grabaciones reales con textos específicos en español
- **API REST**: Endpoints `/synthesize` y `/synthesize_json`
- **Docker**: Servicio containerizado listo para usar
- **Debug**: Archivos de audio generados para pruebas

## 🚀 Inicio Rápido

### Usando Docker Compose

```bash
# 1. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env si necesitas cambiar puertos o configuración

# 2. Construir y ejecutar
docker compose up --build -d

# 3. Verificar estado
curl http://localhost:5005/health

# 4. Probar síntesis
curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, soy Spanish-F5 y hablo español natural","language":"es"}'
```

## 📊 Endpoints

### GET /health
Estado del servicio
```json
{
  "status": "ok",
  "model": "spanish-f5",
  "device": "cuda",
  "f5_available": true
}
```

### GET /voices?language=es
Voces disponibles
```json
{
  "default": "es_female",
  "language": "es",
  "model": "spanish-f5",
  "voices": {
    "female": ["es_female", "es_maria", "es_elena", "es_sofia"],
    "male": ["es_male", "es_carlos", "es_diego", "es_pablo"]
  }
}
```

### POST /synthesize
Síntesis que devuelve archivo WAV
```bash
curl -X POST http://localhost:5005/synthesize \
  -F "text=Tu texto aquí" \
  -F "language=es" \
  -F "voice=es_female" \
  -F "speed=0.9" \
  -o output.wav
```

### POST /synthesize_json
Síntesis que devuelve metadatos JSON
```json
{
  "text": "Tu texto aquí",
  "language": "es",
  "voice": "es_female",
  "speed": 0.9
}
```

Respuesta:
```json
{
  "success": true,
  "model": "spanish-f5",
  "speed": 0.9,
  "audio_duration": 3.5,
  "sample_rate": 24000,
  "f5_available": true,
  "debug_audio_file": "spanish_f5_20250620_145613_910.wav",
  "debug_audio_url": "/debug/audio/spanish_f5_20250620_145613_910.wav"
}
```

## 🎤 Voces Disponibles

- **Femeninas**: `es_female`, `es_maria`, `es_elena`, `es_sofia`
- **Masculinas**: `es_male`, `es_carlos`, `es_diego`, `es_pablo`

## 🔧 Configuración

### Variables de Entorno

El servicio usa un archivo `.env` para configurar todos los parámetros. Copia `.env.example` como `.env` y modifica según necesites:

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

#### Variables Disponibles

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `CONTAINER_NAME` | Nombre del contenedor Docker | `f5-tts-service` |
| `HOST_PORT` | Puerto en el host | `5005` |
| `CONTAINER_PORT` | Puerto dentro del contenedor | `5005` |
| `HOST_ADDRESS` | Dirección del host | `localhost` |
| `FLASK_HOST` | Host de Flask | `0.0.0.0` |
| `FLASK_PORT` | Puerto de Flask | `5005` |
| `DEFAULT_LANGUAGE` | Idioma por defecto | `es` |
| `DEFAULT_VOICE` | Voz por defecto | `es_female` |
| `DEBUG_AUDIO` | Habilitar debug de audio | `true` |
| `F5_MODEL` | Modelo F5 a usar | `jpgallegoar/F5-Spanish` |

#### Ejemplo de Configuración

```bash
# Configuración para desarrollo
CONTAINER_NAME=f5-tts-dev
HOST_PORT=5005
CONTAINER_PORT=5005
HOST_ADDRESS=localhost
FLASK_HOST=0.0.0.0
FLASK_PORT=5005
DEFAULT_LANGUAGE=es
DEFAULT_VOICE=es_female
DEBUG_AUDIO=true
F5_MODEL=jpgallegoar/F5-Spanish
```

### Variables de Entorno Adicionales
- `CUDA_VISIBLE_DEVICES`: GPU a usar (default: 0)
- `F5_MODEL`: Modelo a cargar (default: jpgallegoar/F5-Spanish)

### Archivos de Referencia
Los archivos de referencia WAV están en `/app/references/` con grabaciones reales y textos específicos:
- `es_masc_presentacion.wav`: "Hola, soy Carlos y esta es mi voz natural..."
- `es_masc_tecnico.wav`: "La síntesis de texto a voz permite convertir..."
- `es_masc_geografia.wav`: "España, México, Argentina, Colombia..."
- `es_masc_tiempo.wav`: "Hoy hace sol, ayer llovió..."
- `es_masc_despedida.wav`: "Gracias por escuchar esta grabación..."

## 🧪 Testing Completo

### Tests Automatizados

El proyecto incluye una suite completa de tests que cubre:

- **Tests Unitarios**: Funciones individuales y lógica de negocio
- **Tests de Integración**: Endpoints REST y comunicación entre componentes
- **Tests de Rendimiento**: Tiempos de respuesta y uso de recursos
- **Tests de Casos Límite**: Manejo de errores y situaciones extremas
- **Tests de Configuración**: Variables de entorno y configuración del sistema

#### Instalación de Dependencias de Testing

```bash
# Instalar dependencias específicas para testing
pip install -r requirements_test.txt

# O instalar manualmente las principales
pip install pytest pytest-html pytest-cov requests numpy soundfile
```

#### Ejecución de Tests

```bash
# 🔍 Tests completos con reporte detallado
python test_f5_tts_complete.py

# 🧪 Usando pytest (recomendado)
pytest test_f5_tts_complete.py -v

# 📊 Con reporte HTML
pytest test_f5_tts_complete.py -v --html=report.html --self-contained-html

# 📈 Con coverage
pytest test_f5_tts_complete.py --cov=app --cov-report=html

# ⚡ Tests en paralelo
pytest test_f5_tts_complete.py -n 4

# 🎯 Tests específicos por categoría
python test_f5_tts_complete.py --unit          # Solo tests unitarios
python test_f5_tts_complete.py --integration   # Solo tests de integración
python test_f5_tts_complete.py --performance   # Solo tests de rendimiento
python test_f5_tts_complete.py --edge-cases    # Solo casos límite

# 🌐 Tests con URL personalizada
python test_f5_tts_complete.py --url http://localhost:5005 --timeout 60
```

#### Estructura de Tests

```
f5-tts/
├── test_f5_tts_complete.py     # Suite completa de tests
├── requirements_test.txt       # Dependencias para testing
└── tests/
    ├── unit/                   # Tests unitarios
    ├── integration/            # Tests de integración
    ├── performance/            # Tests de rendimiento
    └── fixtures/               # Datos de prueba
```

### Tests Manuales y Validación

#### Prueba Rápida de Funcionamiento

```bash
# 1. Verificar que el servicio está corriendo
curl http://localhost:5005/health | jq

# 2. Listar voces disponibles
curl http://localhost:5005/voices?language=es | jq

# 3. Síntesis básica
curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola, soy Spanish-F5 y hablo español natural","language":"es","speed":0.9}' \
  | jq

# 4. Descargar archivo de audio
curl -X POST http://localhost:5005/synthesize \
  -F "text=Prueba de descarga de audio" \
  -F "language=es" \
  -F "voice=es_male" \
  -o test_audio.wav

# 5. Reproducir audio (requiere sox o similar)
play test_audio.wav
```

#### Tests de Diferentes Voces

```bash
# Probar todas las voces disponibles
for voice in es_female es_male es_maria es_carlos es_elena es_diego; do
  echo "🎤 Probando voz: $voice"
  curl -X POST http://localhost:5005/synthesize_json \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"Hola, soy $voice y esta es mi voz\",\"language\":\"es\",\"voice\":\"$voice\"}" \
    | jq '.success, .voice, .audio_duration'
  echo ""
done
```

#### Tests de Rendimiento Manual

```bash
# Test de velocidad de respuesta
time curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text":"Prueba de velocidad de respuesta","language":"es"}' \
  -o /dev/null -s

# Test con texto largo
long_text="La síntesis de texto a voz es una tecnología fascinante que permite convertir cualquier texto escrito en audio hablado con voz natural. Esta tecnología ha evolucionado considerablemente en los últimos años."

time curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$long_text\",\"language\":\"es\"}" \
  | jq '.audio_duration, .sample_rate'
```

### Métricas de Calidad

#### Benchmarks Esperados

| Métrica | Valor Esperado | Notas |
|---------|---------------|-------|
| **Tiempo de respuesta (texto corto)** | < 15 segundos | Texto de 1-20 palabras |
| **Tiempo de respuesta (texto largo)** | < 30 segundos | Texto de 100-300 palabras |
| **Sample Rate** | 24000 Hz | Calidad estándar |
| **Formato de salida** | WAV mono, 16-bit PCM | Compatible universalmente |
| **Velocidad óptima** | 0.9x | Máxima claridad confirmada |
| **Latencia inicial** | 2-5 segundos | Carga del modelo |

#### Monitoreo de Recursos

```bash
# Monitor de uso de GPU
nvidia-smi -l 1

# Monitor de memoria y CPU
docker stats f5-tts-service

# Logs en tiempo real
docker logs -f f5-tts-service

# Espacio en disco (archivos debug)
du -sh debug_audio/
ls -la debug_audio/ | tail -10
```

## 🐛 Debug

Los archivos de audio generados se guardan en `debug_audio/` para verificar la calidad:

```bash
# Listar archivos debug
ls -la debug_audio/

# Reproducir último archivo
play debug_audio/$(ls -t debug_audio/ | head -1)
```

## 📂 Estructura

```
f5-tts/
├── app/
│   ├── app.py              # Aplicación Flask principal (velocidad 0.9 optimizada)
│   ├── requirements.txt    # Dependencias Spanish-F5 oficial
│   └── Dockerfile         # Imagen Docker con CUDA
├── references/            # Archivos de referencia con textos específicos
│   ├── es_masc_presentacion.wav
│   ├── es_masc_tecnico.wav
│   ├── es_masc_geografia.wav
│   ├── es_masc_tiempo.wav
│   └── es_masc_despedida.wav
├── debug_audio/          # Archivos de debug generados
├── docker-compose.yml    # Configuración Docker Compose
├── test_clarity.py       # Test de velocidades múltiples
└── test_spanish_f5_official.py  # Test de verificación
```

## 🔗 Enlaces

- **Repositorio Spanish-F5**: https://github.com/jpgallegoar/Spanish-F5
- **Modelo HuggingFace**: https://huggingface.co/jpgallegoar/F5-Spanish
- **Documentación F5-TTS**: https://arxiv.org/abs/2410.06885

## 🔧 Resolución de Problemas

### ✅ Problema de Acento Inglés RESUELTO
- **Antes**: Usaba modelo base F5-TTS → acento inglés
- **Ahora**: Fuerza modelo Spanish-F5 específico → acento español natural
- **Configuración**: Velocidad 0.9 optimizada para máxima claridad

### 🎯 Configuración Optimizada
- **Velocidad por defecto**: 0.9 (confirmada como óptima)
- **Modelo**: Spanish-F5 exclusivamente (no modelos base)
- **Referencias**: Grabaciones reales con textos específicos

### 🐛 Problemas Comunes y Soluciones

#### Error: "Servicio no disponible"
```bash
# Verificar estado del contenedor
docker ps | grep f5-tts

# Si no está corriendo, iniciarlo
docker compose up -d

# Verificar logs
docker logs f5-tts-service

# Verificar puerto
netstat -tulpn | grep 5005
```

#### Error: "Modelo no se puede cargar"
```bash
# Verificar GPU disponible
nvidia-smi

# Verificar espacio en disco
df -h

# Limpiar cache de HuggingFace
rm -rf ~/.cache/huggingface/

# Reiniciar con reconstrucción
docker compose down
docker compose up --build -d
```

#### Error: "Audio distorsionado o con ruido"
```bash
# Verificar archivos de referencia
ls -la references/
file references/*.wav

# Regenerar archivos de referencia si están corruptos
# (Contactar al administrador del sistema)

# Ajustar velocidad para mejor claridad
curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text":"Prueba de claridad","language":"es","speed":0.8}'
```

#### Error: "Respuesta muy lenta"
```bash
# Verificar uso de GPU
nvidia-smi

# Verificar memoria disponible
free -h

# Verificar carga del sistema
htop

# Optimizar configuración Docker
# Aumentar memoria asignada en docker-compose.yml
```

#### Error: "Caracteres especiales no procesados"
```bash
# Verificar encoding del texto
echo "áéíóú ñ ¿¡" | file -

# Usar escapado correcto en JSON
curl -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"text":"Texto con acentos: áéíóú","language":"es"}'
```

### 📋 Checklist de Diagnóstico

Cuando tengas problemas, ejecuta este checklist:

```bash
#!/bin/bash
echo "🔍 DIAGNÓSTICO F5-TTS ESPAÑOL"
echo "================================"

echo "1. ✅ Verificando Docker..."
docker --version && echo "✅ Docker OK" || echo "❌ Docker no disponible"

echo "2. ✅ Verificando contenedor..."
docker ps | grep f5-tts && echo "✅ Contenedor corriendo" || echo "❌ Contenedor no está corriendo"

echo "3. ✅ Verificando puerto..."
curl -s http://localhost:5005/health >/dev/null && echo "✅ Puerto 5005 responde" || echo "❌ Puerto 5005 no responde"

echo "4. ✅ Verificando modelo..."
curl -s http://localhost:5005/health | jq -r '.f5_available' | grep -q true && echo "✅ Modelo F5 disponible" || echo "❌ Modelo F5 no disponible"

echo "5. ✅ Verificando GPU..."
nvidia-smi >/dev/null 2>&1 && echo "✅ GPU disponible" || echo "⚠️ GPU no disponible (usando CPU)"

echo "6. ✅ Verificando archivos de referencia..."
ls references/*.wav >/dev/null 2>&1 && echo "✅ Archivos de referencia OK" || echo "❌ Archivos de referencia faltantes"

echo "7. ✅ Test básico..."
response=$(curl -s -X POST http://localhost:5005/synthesize_json \
  -H "Content-Type: application/json" \
  -d '{"text":"Test","language":"es"}' | jq -r '.success')
[[ "$response" == "true" ]] && echo "✅ Test básico exitoso" || echo "❌ Test básico falló"

echo "================================"
echo "✅ Diagnóstico completado"
```

### 🚨 Logs de Debug

#### Activar Logging Detallado

```bash
# Variables de entorno para debug
export LOG_LEVEL=DEBUG
export DEBUG_AUDIO=true

# Reiniciar con logging debug
docker compose down
docker compose up -d

# Ver logs en tiempo real
docker logs -f f5-tts-service | grep -E "(ERROR|WARNING|INFO)"
```

#### Interpretar Logs Comunes

```bash
# ✅ Logs normales (OK)
"✅ Spanish-F5 inicializado con modelo HuggingFace"
"✅ Audio procesado y mejorado: X samples, 24000Hz"
"🎯 Síntesis solicitada: 'texto...'"

# ⚠️ Logs de advertencia (atención)
"⚠️ Método HuggingFace falló: timeout"
"⚠️ Error mejorando claridad: usando audio original"
"⚠️ No se encontró modelo español específico"

# ❌ Logs de error (problema)
"❌ Error inicializando Spanish-F5"
"❌ Error en síntesis Spanish-F5"
"❌ CLI no disponible"
```

## 🚀 Ejemplos Avanzados

### Integración con Python

```python
#!/usr/bin/env python3
"""
Ejemplo de integración con el servicio F5-TTS Español
"""

import requests
import json
import base64
import io
import soundfile as sf
from datetime import datetime

class F5TTSClient:
    def __init__(self, base_url="http://localhost:5005"):
        self.base_url = base_url
    
    def synthesize_text(self, text, voice="es_female", speed=0.9):
        """Sintetizar texto y retornar metadatos"""
        payload = {
            "text": text,
            "language": "es",
            "voice": voice,
            "speed": speed
        }
        
        response = requests.post(
            f"{self.base_url}/synthesize_json",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}")
    
    def download_audio(self, text, voice="es_female", speed=0.9, filename=None):
        """Descargar archivo de audio directamente"""
        payload = {
            "text": text,
            "language": "es",
            "voice": voice,
            "speed": str(speed)
        }
        
        response = requests.post(
            f"{self.base_url}/synthesize",
            data=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"f5_tts_{timestamp}.wav"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return filename
        else:
            raise Exception(f"Error: {response.status_code}")
    
    def get_available_voices(self):
        """Obtener lista de voces disponibles"""
        response = requests.get(f"{self.base_url}/voices?language=es")
        return response.json()
    
    def health_check(self):
        """Verificar estado del servicio"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Ejemplo de uso
if __name__ == "__main__":
    client = F5TTSClient()
    
    # Verificar estado
    health = client.health_check()
    print(f"Estado del servicio: {health}")
    
    # Obtener voces
    voices = client.get_available_voices()
    print(f"Voces disponibles: {voices['voices']}")
    
    # Sintetizar texto
    result = client.synthesize_text(
        "Hola, este es un ejemplo de síntesis de voz con Python",
        voice="es_male",
        speed=0.9
    )
    print(f"Síntesis exitosa: {result['success']}")
    print(f"Duración: {result['audio_duration']:.2f} segundos")
    
    # Descargar audio
    filename = client.download_audio(
        "Este audio se descarga directamente a archivo",
        voice="es_female"
    )
    print(f"Audio guardado en: {filename}")
```

### Integración con Node.js/JavaScript

```javascript
// f5-tts-client.js
const axios = require('axios');
const fs = require('fs');

class F5TTSClient {
    constructor(baseUrl = 'http://localhost:5005') {
        this.baseUrl = baseUrl;
    }
    
    async synthesizeText(text, voice = 'es_female', speed = 0.9) {
        try {
            const response = await axios.post(`${this.baseUrl}/synthesize_json`, {
                text: text,
                language: 'es',
                voice: voice,
                speed: speed
            }, {
                timeout: 30000
            });
            
            return response.data;
        } catch (error) {
            throw new Error(`Síntesis falló: ${error.message}`);
        }
    }
    
    async downloadAudio(text, voice = 'es_female', speed = 0.9, filename = null) {
        try {
            const response = await axios.post(`${this.baseUrl}/synthesize`, 
                new URLSearchParams({
                    text: text,
                    language: 'es',
                    voice: voice,
                    speed: speed.toString()
                }),
                {
                    responseType: 'arraybuffer',
                    timeout: 30000,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            );
            
            if (!filename) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                filename = `f5_tts_${timestamp}.wav`;
            }
            
            fs.writeFileSync(filename, response.data);
            return filename;
        } catch (error) {
            throw new Error(`Descarga falló: ${error.message}`);
        }
    }
    
    async getVoices() {
        const response = await axios.get(`${this.baseUrl}/voices?language=es`);
        return response.data;
    }
    
    async healthCheck() {
        const response = await axios.get(`${this.baseUrl}/health`);
        return response.data;
    }
}

// Ejemplo de uso
async function example() {
    const client = new F5TTSClient();
    
    try {
        // Verificar estado
        const health = await client.healthCheck();
        console.log('Estado del servicio:', health);
        
        // Sintetizar texto
        const result = await client.synthesizeText(
            '¡Hola! Este es un ejemplo desde Node.js',
            'es_female',
            0.9
        );
        console.log(`Síntesis exitosa: ${result.success}`);
        
        // Descargar archivo
        const filename = await client.downloadAudio(
            'Este archivo se descarga desde JavaScript'
        );
        console.log(`Audio guardado: ${filename}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

example();
```

### Uso con cURL Avanzado

```bash
#!/bin/bash
# script_f5_tts_advanced.sh - Ejemplos avanzados con cURL

BASE_URL="http://localhost:5005"

# Función para síntesis con validación
synthesize_with_validation() {
    local text="$1"
    local voice="${2:-es_female}"
    local speed="${3:-0.9}"
    
    echo "🎤 Sintetizando: '$text'"
    echo "🎭 Voz: $voice | Velocidad: $speed"
    
    response=$(curl -s -X POST "$BASE_URL/synthesize_json" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"$text\",\"language\":\"es\",\"voice\":\"$voice\",\"speed\":$speed}")
    
    success=$(echo "$response" | jq -r '.success')
    if [[ "$success" == "true" ]]; then
        duration=$(echo "$response" | jq -r '.audio_duration')
        debug_file=$(echo "$response" | jq -r '.debug_audio_file')
        echo "✅ Éxito - Duración: ${duration}s - Debug: $debug_file"
    else
        error=$(echo "$response" | jq -r '.error')
        echo "❌ Error: $error"
    fi
}

# Función para descargar múltiples archivos
batch_download() {
    local texts=("$@")
    local counter=1
    
    for text in "${texts[@]}"; do
        echo "📥 Descargando archivo $counter..."
        curl -X POST "$BASE_URL/synthesize" \
            -F "text=$text" \
            -F "language=es" \
            -F "voice=es_female" \
            -o "batch_audio_$counter.wav"
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Descargado: batch_audio_$counter.wav"
        else
            echo "❌ Error descargando archivo $counter"
        fi
        
        ((counter++))
        sleep 1  # Pausa entre descargas
    done
}

# Función de benchmark
benchmark_voices() {
    local test_text="Esta es una prueba de rendimiento de voces"
    local voices=("es_female" "es_male" "es_maria" "es_carlos")
    
    echo "🏁 BENCHMARK DE VOCES"
    echo "===================="
    
    for voice in "${voices[@]}"; do
        echo "Probando voz: $voice"
        start_time=$(date +%s.%N)
        
        response=$(curl -s -X POST "$BASE_URL/synthesize_json" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$test_text\",\"language\":\"es\",\"voice\":\"$voice\"}")
        
        end_time=$(date +%s.%N)
        elapsed=$(echo "$end_time - $start_time" | bc)
        
        success=$(echo "$response" | jq -r '.success')
        if [[ "$success" == "true" ]]; then
            duration=$(echo "$response" | jq -r '.audio_duration')
            echo "  ✅ Tiempo: ${elapsed}s - Audio: ${duration}s"
        else
            echo "  ❌ Error con voz $voice"
        fi
    done
}

# Ejecutar ejemplos
echo "🚀 EJEMPLOS AVANZADOS F5-TTS"
echo "============================="

# Test básico
synthesize_with_validation "Hola, esta es una prueba básica"

# Test con diferentes voces
synthesize_with_validation "Soy una voz femenina" "es_female"
synthesize_with_validation "Soy una voz masculina" "es_male"

# Test con velocidades diferentes
synthesize_with_validation "Velocidad lenta" "es_female" "0.8"
synthesize_with_validation "Velocidad rápida" "es_female" "1.1"

# Descarga en lote
batch_texts=(
    "Primer archivo de lote"
    "Segundo archivo de lote"
    "Tercer archivo de lote"
)
batch_download "${batch_texts[@]}"

# Benchmark
benchmark_voices

echo "✅ Ejemplos completados"
```

## 📝 Notas Técnicas

### Especificaciones del Sistema

- **GPU Requerida**: CUDA-compatible para mejor rendimiento
- **RAM Mínima**: 8GB (16GB recomendado)
- **Espacio en Disco**: 5GB mínimo para modelos y cache
- **Sample Rate**: 24kHz (estándar para alta calidad)
- **Formato de Salida**: WAV mono, 16-bit PCM
- **Latencia Típica**: 2-5 segundos para textos cortos
- **Throughput**: ~100-200 palabras por minuto

### Limitaciones Conocidas

- **Solo idioma español**: No soporta otros idiomas
- **Longitud máxima**: Textos muy largos (>2000 caracteres) pueden causar timeouts
- **Concurrencia**: Un solo modelo por contenedor (no multi-threading)
- **Memoria**: Modelo requiere ~4GB VRAM en GPU

### Optimizaciones Recomendadas

```yaml
# docker-compose.yml optimizado para producción
services:
  f5-tts:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - OMP_NUM_THREADS=4
      - TORCH_NUM_THREADS=4
    volumes:
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 2G
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles. 