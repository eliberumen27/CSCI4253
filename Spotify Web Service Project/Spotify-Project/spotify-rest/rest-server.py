##
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import speech_recognition as sr

# We'll be using the python SpeeechRecognition module
# which acts as a wrapper for many well known
# speech recognition APIs(we're using google cloud speech-to-text)
# Note: SpeechRecognition ships out of the box with a google api key

##
## Configure test vs. production
##
# This is assuming we set those environment variables for our containers to use
mySQLhost = os.getenv("MYSQL_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and mysql({})".format(rabbitMQHost,mySQLhost))

##
## You provide this
##

# flask app
app = Flask(__name__)

# We need this default route since Google Kubernetes Engine checks for the health of our services(if we deploy to the cloud)
@app.route('/', methods=['GET'])
def hello():
    return '<h1> Welcome to Voice-based music search service</h1><p> Use a valid endpoint </p>'

@app.route('/spotifind/voice/<filename>', method=['POST'])
def voice_search(filename):
    print("We're using ", filename)
    # Request shoud contain the voice data in a .wav or similar
    r = request

    try:

        # rec is our speech recognizer
        recog = sr.Recognizer()
        audio_file = sr.AudioFile(filename)
        with audio_file as source:
            audio = recog.record(source)

        sentence = recog.recognize_google(audio)

    except:

        print("Speech was not recognized, or no valid input was provided")


app.run(host="0.0.0.0", port=5000)
