FROM python:3.12-alpine3.22

WORKDIR /app

RUN adduser -D -u 1000 appuser

COPY --chown=appuser:appuser requirements.txt .

RUN pip install --upgrade pip \
    && pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser src/ src/

USER appuser

CMD ["python", "-m", "src.main"]
