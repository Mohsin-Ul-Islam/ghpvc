FROM python:3.10-alpine as production

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./main.py ./

CMD [ "sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8080} --workers 4 --threads 1 main:app" ]
