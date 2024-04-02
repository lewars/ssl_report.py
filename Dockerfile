# Dockerfile to build a container image for ssl_report.py
FROM fedora:latest
LABEL maintainer="Alistair Y. Lewars <alistiar.lewars@gmail.com>"

RUN dnf install -y go-task \
    python3 \
    python3-pip
WORKDIR /app
COPY . .
RUN go-task clean install-global

ENTRYPOINT ["python3", "ssl_report.py"]
