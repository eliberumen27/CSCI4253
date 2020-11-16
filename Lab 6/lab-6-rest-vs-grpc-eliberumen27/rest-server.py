#!/usr/bin/env python3
##
## Sample Flask REST server implementing two methods
##
## Endpoint /api/image is a POST method taking a body containing an image
## It returns a JSON document providing the 'width' and 'height' of the
## image that was provided. The Python Image Library (pillow) is used to
## proce#ss the image
##
## Endpoint /api/add/X/Y is a post or get method returns a JSON body
## containing the sum of 'X' and 'Y'. The body of the request is ignored
##
##
from flask import Flask, request, Response
import jsonpickle
import numpy as np
from PIL import Image
import io

# Initialize the Flask application
app = Flask(__name__)


# route http posts to this method(ie: client sends us a picture) AKA: we're getting the image data but then still returning something(the dimensions of the image)
@app.route('/api/image', methods=['POST'])
def test():
    r = request
    # convert the data to a PIL image type so we can extract dimensions
    try:
        ioBuffer = io.BytesIO(r.data)
        img = Image.open(ioBuffer)
    # build a response dict to send back to client
        response = {
            'width' : img.size[0],
            'height' : img.size[1]
            }
    except:
        response = { 'width' : 0, 'height' : 0}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")


# route http gets to this method(ie: client wants the sum of the two numbers
@app.route('/api/add/<int:x>/<int:y>', methods=['GET'])
def test_add(x,y):
    # Alternatively we could have done a POST method where the client(user) sends us numbers, not just hitting a hardcoded route
    # req = request
    # Try to add the numbers and return the sum or else return 0, note that the endpoint gets us the values as ints so no need to convert
    # Also for this method, the body of the request is ignored since we're getting the numbers from the endpoint
    try:
        total = x + y
        # We put our response in a dictionary as key value pairs after doing the processing above. with jsonpickle.encode(response) the respons and return Response(response, status, mimetype)
        resp = {
            'sum': total
        }

    except:
        resp = {
            'sum': 0
        }

    # Now we pickle the response and return it to the client as true json
    pickled = jsonpickle.encode(resp)

    return Response(response=pickled, status=200, mimetype="application/json")


# start flask app, using 0.0.0.0 allows us to hit the flask app via the ip address of the machine is on rather than just localhost
app.run(host="0.0.0.0", port=5000)
