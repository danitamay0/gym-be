# Imagen base ligera
FROM python:3.12-slim

# Evita bytecode y buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema que suelen requerir libs (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio app
WORKDIR /app

# Copiar requirements primero para cache de capas
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . /app

# (Opcional) variable para usar en tu app si quieres
#ENV FLASK_ENV=production \
#    PYTHONPATH=/app

# Puerto
EXPOSE 8000

# Comando: Gunicorn con 3 workers
# Nota: el módulo wsgi es app:create_app y el código vive en /app/app
#       --chdir asegura que 'app' se resuelva igual que en tu local
CMD ["python","-m","gunicorn","--chdir","/app/app","--workers","3","--bind","0.0.0.0:8000","app:app"]

