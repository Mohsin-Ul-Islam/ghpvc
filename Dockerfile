FROM python:3.10-alpine as production

WORKDIR /app

COPY ./main.py ./requirements.txt ./

RUN pip install -r requirements.txt

CMD [ "sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8080} --workers 2 --threads 2 main:app" ]
