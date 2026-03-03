FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
COPY services/workflow-engine/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/workflow-engine/src /app/src
CMD ["python", "-m", "workflow_engine.worker"]
