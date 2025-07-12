# Etapa builder (optimización)
FROM python:3.11-slim as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instala dependencias de compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Crear usuario en builder stage para consistencia
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias en directorio del usuario
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa final
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PORT=8888

# Instalar solo librerías runtime necesarias
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

WORKDIR /app

# Copiar dependencias instaladas al home del usuario
COPY --from=builder /root/.local /home/appuser/.local
RUN chown -R appuser:appuser /home/appuser/.local

# Copiar código y cambiar permisos
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# Healthcheck mejorado - verifica que la app responda
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Comando con puerto consistente
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1