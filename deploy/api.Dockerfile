FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY adapters adapters
COPY backend backend
COPY demo demo
COPY packages packages
COPY services services

ENV CLEARFRAME_AGENT_PROVIDER=local \
    CLEARFRAME_API_HOST=0.0.0.0 \
    CLEARFRAME_API_PORT=8000
EXPOSE 8000
CMD ["python", "-m", "services.api"]
