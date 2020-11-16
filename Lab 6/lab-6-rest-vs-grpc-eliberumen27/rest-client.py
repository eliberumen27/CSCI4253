#!/usr/bin/env python3
from __future__ import print_function
import requests
import json
import sys
from time import perf_counter

# We parse command line arguments to indicate the endpoint and iterations to test as follows: machine, api route, number of runs
# python3 rest-client.py localhost add 1000

# The address the that of the server we are sending a request to
addr = sys.argv[1]
endpoint = sys.argv[2]
num_tests = int(sys.argv[3])
print(addr, endpoint, num_tests)

# Address of our server
# addr = 'http://localhost:5000'

# In the following, we are loading in our image and sending it to the /api/image endpoint via a request, and getting back the image size
# Next, we are making a request to the /api/add endpoint and getting back the sum in the response from the server

# prepare headers for different http requests
headers = {'content-type': 'image/png'}
headers_add = {'content-type': 'text/plain'}

img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
# send http request with image and receive response the appropriate amount of times specified
image_url = addr + '/api/image'
# url to send an http request to, in order to receive the sume of these hard-coded values
add_url = addr + '/api/add/5/2'

if endpoint == 'add':

    # Start timer before loop and stop after, then divide by the number of test requests
    start_t1 = perf_counter()
    for i in range(num_tests):
        resp = requests.get(add_url, headers=headers_add)
        # decode response
        print("Response is", resp.text)
        # print(json.loads(resp.text))
    stop_t1 = perf_counter()

    total = stop_t1 - start_t1
    avg = total / num_tests
    print("The average time taken for the /api/add endpoint was {}".format(avg))

else:

    # Start timer before loop and stop after, then divide by the number of tests for the image endpoint
    # Here we remember to include the image data in the POST request, along with the url and the headers
    start_t2 = perf_counter()
    for i in range(num_tests):
        resp = requests.post(image_url, data=img, headers=headers)
        # decode response
        print("Response is", resp)
        # commenting out the next line since for the image, the response is different
        # print(json.loads(resp.text))
    stop_t2 = perf_counter()

    total = stop_t2 - start_t2
    avg = total / num_tests
    print("The average time taken from the /api/image endpoint was {}".format(avg))



# response = requests.post(image_url, data=img, headers=headers)
# decode response
# print("Response is", response)
# print(json.loads(response.text))
