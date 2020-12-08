##
## You provide this
##
# Using Base Ubuntu image and installing python3 as well as our libraries
FROM ubuntu:20.04

RUN	DEBIAN_FRONTEND=noninteractive apt-get update -y && \
	apt-get install -yq --no-install-recommends \
	   git python3 python3-pip curl

RUN pip3 install pika redis jsonpickle requests flask spotipy SpeechRecognition mysql-connector-python
# DONT FORGET TO IONSTALL SPOTIFY API STUFF AFTER FLASK UP HERE ^^^^^^^^ AS WELL AS MYSQL CONNECTOR

WORKDIR /srv
COPY    . /srv
ENV     FLASK_APP=rest-server.py
CMD [ "python3", "rest-server.py"]
