FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home appuser \
    && mkdir /app/data \
    && chown appuser:appuser /app/data

COPY src/ ./src/
USER appuser

CMD ["python", "src/scraper.py"]