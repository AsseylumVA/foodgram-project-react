FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt --no-cache-dir

COPY . .
RUN python manage.py collectstatic
CMD ["gunicorn", "--access-logfile", "-", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]
