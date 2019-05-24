FROM python:3.7

RUN apt-get update

RUN apt-get install -y vim

COPY ./app /app
WORKDIR /app/

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

EXPOSE 80

CMD [ "python3", "./bikes_dash.py"]