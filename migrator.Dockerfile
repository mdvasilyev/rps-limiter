FROM python:3.12-alpine3.22

WORKDIR /app

RUN adduser -D -u 1000 migrator

COPY --chown=migrator:migrator alembic.ini requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --root-user-action=ignore --no-cache-dir -r requirements.txt

COPY --chown=migrator:migrator migrations/ migrations/
COPY --chown=migrator:migrator src/ src/

USER migrator

CMD ["alembic", "upgrade", "head"]
