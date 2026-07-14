ARG PYTHON_VERSION=3.13.14
ARG TORCH_VERSION=2.7.0
FROM python:${PYTHON_VERSION}-slim

ARG TORCH_VERSION

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

COPY app/backend/requirements.txt ./requirements.txt

# Install CPU-only PyTorch first so downstream NLP packages do not pull CUDA wheels.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==${TORCH_VERSION}

RUN pip install --no-cache-dir -r requirements.txt

COPY app/backend/ ./
COPY docker/credentials /opt/credentials

RUN mkdir -p uploads logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
