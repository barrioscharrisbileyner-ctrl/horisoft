FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system django && adduser --system --ingroup django django \
    && mkdir -p /app/private_media \
    && chown -R django:django /app/private_media

RUN DJANGO_ENV=build DJANGO_DEBUG=False python manage.py collectstatic --noinput

USER django

EXPOSE 8000

CMD ["gunicorn", "horisoft.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]
