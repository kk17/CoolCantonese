FROM kk17/ekho
MAINTAINER Zhike Chan "zk.chan007@gmail.com"
ENV REFRESHED_AT 2015-12-20

ENV PYTHONUNBUFFERED 1

RUN sed 's/http:\/\/archive\.ubuntu\.com\/ubuntu\//mirror:\/\/mirrors\.ubuntu\.com\/mirrors.txt/' -i /etc/apt/sources.list

## python3-pip and python3-lxml
RUN \
  set -x && \
  apt-get update && \
  apt-get install -y python3-pip python3-lxml && \
  rm -rf /var/lib/apt/lists/*

## Install Python packages.
ADD requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && rm /tmp/requirements.txt


ENTRYPOINT []
CMD []