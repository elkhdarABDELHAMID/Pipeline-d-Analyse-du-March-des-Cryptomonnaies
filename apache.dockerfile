FROM apache/airflow:2.7.0

USER root

RUN apt-get update && apt-get install -y \
    docker.io \
    gcc \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir --user happybase