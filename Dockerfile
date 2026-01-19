FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
	gcc \
    build-essential \
    bash \
    procps \
    iputils-ping \
    curl \
    wget \
    nmap \
    htop \
    git \
    nano \
 && rm -rf /var/lib/apt/lists/*

COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python3", "run.py"]