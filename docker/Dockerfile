FROM debian

COPY entrypoint.sh /entrypoint.sh

## Instalación de paquetes y dependencias
RUN apt-get update && \
    apt-get install -y \
    python3 \
    pip \
    iptables \
    net-tools \
    nano \
    openssh-server \
    sudo && \
    apt-get clean

RUN mkdir -p /docker
COPY requirements.txt /docker/requirements.txt
RUN pip install -r /docker/requirements.txt

## Copiar Implementación de la API
RUN mkdir -p /docker/restfs_dirs && \
    mkdir -p /docker/restfs_auth && \
    mkdir -p /docker/restfs_blob && \
    mkdir -p /docker/restfs_client && \
    mkdir -p /docker/restfs_common

ADD restfs_dirs /docker/restfs_dirs
ADD restfs_auth /docker/restfs_auth
ADD restfs_blob /docker/restfs_blob
ADD restfs_common /docker/restfs_common
ADD restfs_client /docker/restfs_client

# Copia del setup de los paquetes
COPY setup.py /docker/setup.py

## Lanzamiento entrypoint del docker

ENTRYPOINT [ "/bin/bash","entrypoint.sh" ]




