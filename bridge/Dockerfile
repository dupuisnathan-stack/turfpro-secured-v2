# Image Python ultra-légère
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Répertoire de travail
WORKDIR /app

# Copie des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY app.py .

# Utilisateur non-root
RUN useradd -m -u 1000 bridge && chown -R bridge:bridge /app
USER bridge

# Exposition du port
EXPOSE 8080

# Commande de démarrage avec Uvicorn (ASGI) - OPTIMISÉ pour Cloud Run
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1 --loop uvloop --http httptools --timeout-keep-alive 30 --no-access-log

# Force rebuild - FastAPI v2.0.1
