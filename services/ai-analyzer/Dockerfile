FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
COPY services/ai-analyzer/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY services/ai-analyzer/src /app/src
EXPOSE 8010
CMD ["uvicorn", "ai_analyzer.main:app", "--host", "0.0.0.0", "--port", "8010"]
