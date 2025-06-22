# 1. Imagen oficial de PyTorch con CUDA y cuDNN
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# 2. Evitar prompts interactivos de apt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Madrid

WORKDIR /app

# 3. Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      ffmpeg \
      espeak \
      espeak-data \
      libespeak1 \
      libespeak-dev \
      festival \
      tzdata \
      wget \
      curl \
      build-essential \
      libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# 4. Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Crear directorios necesarios para F5-TTS
RUN mkdir -p /app/debug_audio && \
    mkdir -p /app/models && \
    mkdir -p /app/references

# 6. Copia el código de la aplicación
COPY . .

# 7. Expone el puerto de Flask (puerto específico para F5-TTS)
EXPOSE 5005

# 8. Variables de entorno por defecto
ENV FLASK_PORT=5005
ENV FLASK_HOST=0.0.0.0
ENV DEFAULT_LANGUAGE=es
ENV DEFAULT_VOICE=es_female
ENV DEBUG_AUDIO=true
ENV F5_MODEL=jpgallegoar/F5-Spanish

# 9. Ejecuta la aplicación
CMD ["python", "app.py"] 