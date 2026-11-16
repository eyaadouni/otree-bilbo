FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV OTREE_PRODUCTION=1 OTREE_AUTH_LEVEL=STUDY PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "otree prodserver 0.0.0.0:${PORT}"]
