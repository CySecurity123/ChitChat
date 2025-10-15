# Dockerfile (dev)
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala deps primeiro p/ cache mais eficiente
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir streamlit watchdog

# Copia o resto (em dev, vamos sobrepor com volume)
COPY . .

EXPOSE 8501

# --server.runOnSave ativa reload imediato ao salvar
# watchdog dá um file-watcher mais rápido e confiável
CMD ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.runOnSave=true","--server.fileWatcherType=watchdog"]
