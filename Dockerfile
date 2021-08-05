FROM debian:buster
LABEL maintainer="ethan@ethandjeric.com"

RUN apt-get update && \ 
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3 \
        python3-wheel \
        python3-dev \
        python3-pip \
        python3-setuptools && \
    pip3 install \
        watchdog && \
    # clean up
    apt-get clean && \
    rm -rf \
    /tmp/* \
    /var/lib/apt/lists/* \
    /var/cache/apt/* \
    /var/tmp/*

COPY root/ /

USER root

ENTRYPOINT ["python3", "/app/main.py"]
