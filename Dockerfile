FROM python:3.8-alpine as base
WORKDIR /code

ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV ELASTICSEARCH_URI http://elasticsearch:9200/

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
########## NEW IMAGE: DEBUG ##########
FROM base as debug

RUN pip install debugpy

CMD python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m flask run -h 0.0.0.0 -p 5000

########## NEW IMAGE: DEBUG ##########
FROM base as prod

CMD flask run -h 0.0.0.0 -p 5000

# docker build --target debug -t flask-run-debug:debug .
# docker run -p 5000:5000 -p 5678:5678 flask-run-debug:debug   