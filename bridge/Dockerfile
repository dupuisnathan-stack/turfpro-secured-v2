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

# Commande de démarrage avec Gunicorn - OPTIMISÉ pour Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 2 --timeout 30 --graceful-timeout 10 --worker-class gthread --access-logfile - --error-logfile - app:app
