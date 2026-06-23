FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts/
COPY assets/ ./assets/
COPY references/ ./references/

ENTRYPOINT ["python"]
CMD ["--help"]
