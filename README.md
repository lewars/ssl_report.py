# ssl_report.py

## Description
This is a simple python script that will take a list of hostnames and prints out SSL scan reports for each hostname.

## Quick Start
```bash
sudo dnf install go-task

go-task docker-build

docker run -it -e DEBUG=1 ssl_report.py:1.0.0 www.google.com www.yahoo.com
```
