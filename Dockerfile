FROM godatadriven/pyspark:2.4.2
MAINTAINER "Paola" pmejiado@gmail.com

# Configura zona horaria
RUN apt-get update
RUN echo "America/Mexico_City" > /etc/timezone
RUN apt-get install -y tzdata

# Configura codificación
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

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

RUN apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev

RUN apt-get install -y \
            sudo \
            nano

RUN pip install --upgrade pip
RUN pip install awscli  --upgrade

# Instalamos paquetes
COPY requirements.txt .
COPY setup.py .
RUN pip install -r requirements.txt
