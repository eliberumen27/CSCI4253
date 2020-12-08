##
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests

import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import mysql.connector

# Don't forget to set the env var GOOGLE_APPLICATION_CREDENTIALS with your own service account JSON
from google.cloud import storage

# We'll be using the python SpeeechRecognition module
# which acts as a wrapper for many well known
# speech recognition APIs(we're using google cloud speech-to-text)
# Note: SpeechRecognition ships out of the box with a google api key

# Second, we'll be using the Spotify API
# All necessary software was installed as a part of the image(Dockerfile)
# All necessary components are imported above

##
## Configure test vs. production
##
# This is assuming we set those environment variables for our containers to use
# SO DONT FORGET to set the Spotify API key stuff as env variables in our deployment .yaml
mySQLhost = os.getenv("MYSQL_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
# Setting env variable for API Keys by grabbing the env variable securely
clientKey = os.getenv("SPOTIFY_CLIENT_ID")
clientSecret = os.getenv("SPOTIFY_CLIENT_SECRET")

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

# This route does a voice search for songs and returns it to the user
# then adds the query data to our database and uploads any query related
# images and thumbnails to our bucket in GCP
@app.route('/spotifind/voice/<filename>', methods=['POST', 'GET'])
def voice_search(filename):
    print("We're using", filename)
    # Request should contain the voice data in a .wav or similar format
    r = request

    try:

        aud_f = r.files["file"]
        file_name = filename
        aud_f.save(file_name) # Save as that name

        # rec is our speech recognizer
        recog = sr.Recognizer()
        audio_file = sr.AudioFile(file_name)
        with audio_file as source:
            audio = recog.record(source)

        sentence = recog.recognize_google(audio)
        # response = {
        #     "Query" : sentence
        # }
        print("The user's query turned into text:", sentence)

        ### SPOTIFY API CALL TO MAKE A SEARCH FOR KEYWORDS IN THAT SENTENCE STRING ###
        response = {}
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=clientKey,
                                                           client_secret=clientSecret))

        results = sp.search(q=sentence, limit=10, type='track')
        for idx, track in enumerate(results['tracks']['items']):
            # print for server debugging
            print(idx, track['name'], track['artists'][0]['name'], track['album']['name'], track['external_urls']['spotify'])
            # send back top 10 results to client: NAME | ARTIST NAME | ALBUM NAME | SPOTIFY TRACK URL
            response[idx] = [track['name'], track['artists'][0]['name'], track['album']['name'], track['external_urls']['spotify']] # Returns the track object but we can access certain values from the dict

        ### SPOTIFY API CALL, INCLUDING LOADING THE QUERY RESPONSE DATA INTO OUR MYSQL DB TABLE(S)

        # Make connection
        mydb = mysql.connector.connect(
        host="mysql",
        user="root",
        password="123"
        )

        # Define Cursor to execute stuff and fetch results
        mycursor = mydb.cursor()
        # Until we implement a persistent volume, we are creating a new database everytime we run this function
        mycursor.execute("CREATE DATABASE IF NOT EXISTS spotifydb")
        mycursor.execute("USE spotifydb")
        mycursor.execute("CREATE TABLE IF NOT EXISTS tracks (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), artist VARCHAR(255), album_name VARCHAR(255), url VARCHAR(255))")

        # Insert the top result of this particular set of top 10 queries
        sql = "INSERT INTO tracks (name, artist, album_name, url) VALUES (%s, %s, %s, %s)" # preparing this to pass in the strings
        val = (response[0][0], response[0][1], response[0][2], response[0][3]) # access corresponding values in order from list(name, artist, album name, url)
        # print((response[0][0], response[0][1], response[0][2], response[0][3])) # testing the response lists
        mycursor.execute(sql, val)

        mydb.commit()
        # mycursor.fetchall() # don't do a fetchall here since there is nothing to get

        ### WE LOAD THE RESPONSE FIELDS INTO SEPARATE COLUMNS OF MY DB

        ### STORING ANY AND ALL IMAGES IN OUR STORAGE BUCKET IN GCP $$$
        # Storing the query audio file in the storage bucket "spotify-voice-search" of our GCP Project
        #
        storage_client = storage.Client()
        bucket = storage_client.get_bucket("spotify-voice-search")
        gcp_filename = "Query-{}".format(filename)
        blob = bucket.blob(gcp_filename)
        blob.upload_from_filename(filename)
        #
        ### MAKE SURE THAT IT PROPERLY STORES IMAGES IN BUCKET

    except:
        print("Speech was not recognized, or no valid input was provided")
        response = {}
        resp_pickled = jsonpickle.encode(response)
        return Response(response = resp_pickled, status = 404, mimetype = "application/json")


    # Encoding our response dict into json and returning it
    resp_pickled = jsonpickle.encode(response)
    return Response(response = resp_pickled, status = 200, mimetype = "application/json")

# Finds all tracks by artist that has been queried before and is stored in our DB
# and returns the result to the user if it exists, otherwise let's them know to do
# a brand new voice query
@app.route('/spotifind/artist/<name>', methods=['GET'])
def find_artist(name):

    try:

        print("Searching for a pre-existing query of ", name)
        ### SEARCH OUR DATABASE FOR ANY SONG ENTRIES THAT HAVE THAT ARTIST NAME???
        ## TODO:
        mydb = mysql.connector.connect(
        host="mysql",
        user="root",
        password="123"
        )

        mycursor = mydb.cursor()
        mycursor.execute("USE spotifydb")
        query = "SELECT * FROM tracks WHERE artist='{}'".format(name)
        mycursor.execute(query)
        # results is a list of the track info: ENTRY ID | NAME | ARTIST | ALBUM | URL
        results = mycursor.fetchall()
        # This can be improved by looping over all of the results and returning all of them instead of just the first by indexing the 0th element as follows
        info = "Songs found by " + name + ": Track Name: " + results[0][1] + ", Artist Name: " + results[0][2] + ", Album Name: " + results[0][3] + ", Spotify URL: " + results[0][4]
        print(info)
        # Later on this response could be improved if it were a list instead of a string so it can be worked with efficiently
        response = {
        "Matching Tracks": info
        }

    except:

        print("Nothing matching that query could be found...")
        response = {}
        resp_pickled = jsonpickle.encode(response)
        return Response(response = resp_pickled, status = 404, mimetype = "application/json")

    # Encoding our response dict into json and returning it
    resp_pickled = jsonpickle.encode(response)
    return Response(response = resp_pickled, status = 200, mimetype = "application/json")



app.run(host="0.0.0.0", port=5000, threaded=True)
