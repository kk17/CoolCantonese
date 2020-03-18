# Ubuntu 14.04.3 LTS 
FROM kk17/ekho 
LABEL Author Zhike Chan "zk.chan007@gmail.com"

ENV PYTHONUNBUFFERED 1

# python 3.4
RUN \
  set -x && \
  apt-get update && \
  apt-get install -y python3-pip python3-lxml && \
  rm -rf /var/lib/apt/lists/*

## Install Python packages.
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY ./coolcantonese/ /workspace/coolcantonese/
WORKDIR /workspace

EXPOSE 8888

ENTRYPOINT [ ]
CMD gunicorn -b 0.0.0.0:8888 coolcantonese.wechat:ekho.wsgi
