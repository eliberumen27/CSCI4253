#!/usr/bin/env python3
#
#
# A sample REST client for the Spotifind application
#
import requests
import json
import time
import sys, os
import jsonpickle

# def doImage(addr, filename, debug=False):
#     # prepare headers for http request
#     headers = {'content-type': 'image/jpg'}
#     img = open(filename, 'rb').read()
#     # send http request with image and receive response
#     image_url = addr + '/scan/image' + "/" + os.path.basename(filename)
#     response = requests.post(image_url, data=img, headers=headers)
#     if debug:
#         # decode response
#         print("Response is", response)
#         print(json.loads(response.text))
#
# def doUrl(addr, filename, debug=False):
#     # prepare headers for http request
#     headers = {'content-type': 'application/json'}
#     # send http request with image and receive response
#     image_url = addr + '/scan/url'
#     data = jsonpickle.encode({ "url" : filename})
#     response = requests.post(image_url, data=data, headers=headers)
#     if debug:
#         # decode response
#         print("Response is", response)
#         print(json.loads(response.text))



### START OF SPOTIFIND ROUTE TESTING ###

host = sys.argv[1]
cmd = sys.argv[2]

addr = 'http://{}'.format(host)

# Sample request to the voice search web service
def doVoice(addr, filename, debug=False):
    # Preparing the http request headers
    headers = {'content-type': 'audio/wav'}

    voice = open(filename, 'rb')
    values = {"file": ("test.wav", voice, "audio/wav") }
    # send http request with voice data and receive response
    voice_url = addr + '/spotifind/voice' + "/" + os.path.basename(filename)
    response = requests.post(voice_url, files=values) # trying files instead of data stream(data=voice, headers=headers) 

    # grab data from the response(which should be a dict here)

    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def doFind(addr, query_word, debug=False):
    url = addr + "/spotifind/artist/" + query_word
    response = requests.get(url)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

# Testing: python3 rest-client.py localhost voice test.wav 3
if cmd == 'voice':
    filename = sys.argv[3]
    reps = int(sys.argv[4])
    #start = time.perf_counter()
    for x in range(reps):
        doVoice(addr, filename, True)
    #delta = ((time.perf_counter() - start)/reps)*1000
    #print("Took", delta, "ms per operation")

# Testing: python3 rest-client.py localhost find Eagles 3
elif cmd == 'find':
    query_word = sys.argv[3]
    reps = int(sys.argv[4])
    start = time.perf_counter()
    for x in range(reps):
        doFind(addr, query_word, True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")

# Unknown option
else:
    print("Unknown option", cmd)
