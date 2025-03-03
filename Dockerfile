FROM python:3.9.21-slim-bookworm
WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . .
CMD python bot.py
