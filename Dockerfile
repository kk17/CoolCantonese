# syntax=docker/dockerfile:1
FROM kk17/ekho:9.0_ubuntu_22.04
LABEL Author="Zhike Chan <zk.chan007@gmail.com>"
LABEL org.opencontainers.image.authors="Zhike Chan <zk.chan007@gmail.com>"
LABEL org.opencontainers.image.description="CoolCantonese web service with ekho speech synthesis"
LABEL org.opencontainers.image.source="https://github.com/kk17/CoolCantonese"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install Python 3.12 and dependencies
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        software-properties-common \
        gpg-agent \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        python3-pip \
        python3-lxml \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python3.12 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Create and activate virtual environment
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Set up application
COPY ./coolcantonese/ /workspace/coolcantonese/
WORKDIR /workspace

# Expose port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Run application
CMD ["gunicorn", "-b", "0.0.0.0:8888", "coolcantonese.wechat:ekho.wsgi"]
