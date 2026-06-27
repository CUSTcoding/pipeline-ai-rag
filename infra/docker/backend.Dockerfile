FROM python:3.12-slim

# Evita criação de arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Logs em tempo real
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia todo o projeto do backend (incluindo .venv se existir)
COPY apps/backend .

# Se a pasta .venv já existir, adiciona-a ao PATH.
# Caso contrário, instala as dependências via pip.
ENV PATH="/app/.venv/bin:$PATH"

RUN if [ ! -f ".venv/bin/uvicorn" ]; then \
      echo "uvicorn não encontrado em .venv/bin. Instalando dependências via pip..." && \
      pip install --default-timeout=1000 --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir -r requirements.txt; \
    else \
      echo "Usando .venv local existente (modo offline)."; \
    fi

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]