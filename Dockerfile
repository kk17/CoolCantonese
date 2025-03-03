FROM kk17/ekho:9.0-ubuntu-22.04

LABEL org.opencontainers.image.authors="Zhike Chan <zk.chan007@gmail.com>"
LABEL org.opencontainers.image.description="CoolCantonese web service with ekho speech synthesis"
LABEL org.opencontainers.image.source="https://github.com/kk17/CoolCantonese"

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-pip \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
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

# Use exec form for ENTRYPOINT
ENTRYPOINT ["gunicorn"]
# Run application with logging enabled
CMD ["--bind", "0.0.0.0:8888", "--log-file=-", "--access-logfile=-", "--log-level=info", "coolcantonese.wechat:application"]
