# Docker image with luigi, boto3 and psycopg

FROM ubuntu:bionic

# Configura zona horaria
RUN apt-get update 
RUN echo "America/Mexico_City" > /etc/timezone 
RUN apt-get install -y tzdata
# Librerias para postgreSQL y psql
RUN apt-get install -y \
			make \
			git \
			gcc \
			jq \
			libpq-dev \
			postgresql \
			postgresql-contrib \
			postgresql-client 
			
RUN apt-get install -y libgdcm-tools

# Configura codificación
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Instala pyenv
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN apt-get install -y \
            sudo \
            nano \
            python3 \
			python3-dev \
			python3-venv \
			python3-virtualenv \
            python3-pip \
            python3-setuptools \
            libpq-dev 
            
RUN pip3 install --upgrade pip  && pip3 install awscli --upgrade


# Instalamos paquetes
COPY requirements.txt .
RUN pip3 install -r requirements.txt




