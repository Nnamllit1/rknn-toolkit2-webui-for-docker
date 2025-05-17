# Dockerfile für RKNN Toolkit2 Web-UI (Basis)
FROM python:3.9-slim

WORKDIR /app

# Systemabhängigkeiten für rknn-toolkit2
RUN apt-get update && apt-get install -y --no-install-recommends \
    git python3 python3-dev python3-pip \
    libxslt1-dev zlib1g zlib1g-dev \
    libglib2.0-0 libsm6 libgl1-mesa-glx \
    libprotobuf-dev gcc cmake make g++ && rm -rf /var/lib/apt/lists/*

# rknn-toolkit2 klonen
RUN git clone --depth 1 https://github.com/airockchip/rknn-toolkit2.git

# tf-estimator-nightly installieren
RUN pip install --no-cache-dir tf-estimator-nightly==2.8.0.dev2021122109

# rknn-toolkit2 Python-Abhängigkeiten und Toolkit installieren
RUN pip install --no-cache-dir -r rknn-toolkit2/rknn-toolkit2/packages/arm64/arm64_requirements_cp39.txt && \
    pip install --no-cache-dir rknn-toolkit2/rknn-toolkit2/packages/arm64/rknn_toolkit2-2.3.2-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 5000

CMD ["python", "app.py"]
