FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
COPY services/ingestor-fleet/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && python -m playwright install chromium
COPY services/ingestor-fleet/src /app/src
CMD ["python", "-m", "ingestor_fleet.worker"]
