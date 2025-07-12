# Multi-stage build para optimizar tamaño
FROM python:3.11-slim as builder

# Variables de entorno para optimización
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa final - imagen más ligera
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Instalar solo las dependencias runtime necesarias
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Crear directorio de aplicación
WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de aplicación
COPY . .

# Cambiar permisos y usuario
RUN chown -R appuser:appuser /app
USER appuser

# Healthcheck mejorado
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; import asyncpg; asyncio.run(asyncpg.connect('$DATABASE_URL').close())" || exit 1

# Exponer puerto
EXPOSE 8000

# Comando para producción (sin --reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8888", "--workers", "1"]