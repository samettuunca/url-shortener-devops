# ---------- Stage 1: Builder ----------
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- Stage 2: Final ----------
FROM python:3.13-slim

RUN useradd -m appuser

WORKDIR /app

RUN mkdir -p /app/data && chown appuser:appuser /app/data

COPY --from=builder /root/.local /home/appuser/.local
COPY app.py .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]