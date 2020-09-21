FROM python:3.8-alpine

ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

ADD config.json /config.json
ADD bot.py /bot.py

RUN ["bot.py"]