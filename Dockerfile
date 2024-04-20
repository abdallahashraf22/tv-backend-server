FROM python3.11

#RUN apt-get update && \
#    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
#    build-essential \
#    && rm -rf /var/lib/apt/lists/* \
#    && apt-get clean

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install poetry

RUN poetry install --no-root --without dev

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "-c", "gunicorn_config.py", "main:app"]



