##
## You provide this FOR THE WORKER
##
# Uses the FROM Dirks image as the base but in the Deployment I have
# specified that I'm using my image
# This should have face_recognition installed on it already so test it by running
# its container with docker run image
FROM dirkcgrunwald/facerec:latest
LABEL MAINTAINER="dirk grunwald <grunwald@colorado.edu>"

RUN pip3 install pika redis jsonpickle requests

WORKDIR /srv
COPY    worker-server.py /srv
ENV     FLASK_APP=worker-server.py
CMD [ "python3", "worker-server.py"]
