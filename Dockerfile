FROM python:3.10-slim-bullseye

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /app/src
COPY models/ /app/models
COPY data/ /app/data

WORKDIR /app/src/

ENTRYPOINT python main.py

