FROM harbor.prd.afip.gob.ar/dockerhub/library/python:3.12-slim-bullseye

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./docker/app/conf/certs/cert.crt /etc/ssl/certs/ca-certificates.crt
COPY ./docker/app/conf/etc/pip.conf /etc/
WORKDIR /app

COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.txt

COPY app .
CMD ["tail", "-f", "/dev/null"]
