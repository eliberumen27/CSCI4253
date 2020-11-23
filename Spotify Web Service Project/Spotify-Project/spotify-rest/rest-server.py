##
from flask import Flask, request, Response
import jsonpickle, pickle
import platform
import io, os, sys
import pika, redis
import hashlib, requests

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

##
## You provide this
##

# flask app
app = Flask(__name__)

# We need this default route since Google Kubernetes Engine checks for the health of our services(if we deploy to the cloud)
@app.route('/', methods=['GET'])
def hello():
    return '<h1> Face Rec Server</h1><p> Use a valid endpoint </p>'

# Server receives an image along with the filename that we're going to compute the hash of its contents, then send hash and the image to a toWorker
# Also adding the filename to the Redis database(more info in the worker documentation)
# response will be a json with a single field containing the hash used to identify that particular image later on
@app.route('/scan/image/<filename>', methods = ['POST'])
def scan_image(filename):
    print(filename)
    r = request # The data of the request should contain the image data

    # Computing the hash of the image and sending the image and its hash to the toWorker
    # update(data) let's us provide the data to the hash
    try:
        hash = hashlib.sha256()
        hash.update(r.data)
        print("hash before is this ", hash)
        final_hash = hash.hexdigest()
        print("hash after is this ", final_hash)
        # Dict we'll convert into json and send back to client
        response = {
            "hash" : final_hash
        }

        # pika to use rabbitmq communication and send the photo database
        # Important note, our msg is a list that gets pickled
        rmq_msg = pickle.dumps([filename, final_hash, r.data])
        # Generic rabbitmq credentials and connection to queue(exchange), sends message
        params = pika.ConnectionParameters(rabbitMQHost, 5672)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue = "toWorker")
        # this is where we send the actual message
        channel.basic_publish(exchange = "", routing_key = "toWorker", body = rmq_msg)

        # confirmation message and close out channel
        print("We have sent the image data to the worker")
        connection.close()
    except:
        # Otherwise respond with an empty hash(value is just 0)
        response = {
            "hash" : 0
        }

    # Encoding our response dict into json and returning it
    resp_pickled = jsonpickle.encode(response)
    return Response(response = resp_pickled, status = 200, mimetype = "application/json")








# Same thing as the image data route but now handling urls
# Treating the url as a filename after we retrieve it
@app.route('/scan/url', methods = ['POST'])
def scan_image_url():
    r = request # The json data of the request contains the single url entry
    url = r.json["url"]
    print("The url is ", url)

    # Get image data from the url provided to us by the client
    img = requests.get(url, allow_redirects=True)
    img_data = img.content # this is equivalent to what r.data had in the prev route

    # Computing the hash of the image and sending the image and its hash to the toWorker
    # update(data) let's us provide the data to the hash
    try:
        hash = hashlib.sha256()
        hash.update(img_data) # Feeds data to the has function
        final_hash = hash.hexdigest()
        # Dict we'll convert into json and send back to client
        response = {
            "hash" : final_hash
        }

        # pika to use rabbitmq communication and send the photo database
        rmq_msg = pickle.dumps([url, final_hash, img_data])
        # Generic rabbitmq credentials and connection to queue(exchange), sends message
        #creds = pika.PlainCredentials('guest', 'guest')
        params = pika.ConnectionParameters(rabbitMQHost, 5672)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue = "toWorker")
        # Publishes on dfault exchange to the toWorker
        channel.basic_publish(exchange = "", routing_key = "toWorker", body = rmq_msg)

        # confirmation message and close out channel
        print("We have sent the image data to the worker")
        connection.close()
    except:
        # Otherwise respond with an empty hash(value is just 0)
        response = {
            "hash" : 0
        }

    # Encoding our response dict into json and returning it
    resp_pickled = jsonpickle.encode(response)
    return Response(response = resp_pickled, status = 200, mimetype = "application/json")




# Takes a hash argument that we will use as our parameter
# We will find the photo that matches that hash
@app.route('/match/<hash>', methods = ['GET'])
def match_hash(hash):
    img_hash = hash
    # The worker makes the Redis DB so we can get image name/url from the hash as the key
    # We are just querying the DB here
    try:
        r = redis.Redis(host=redisHost, db=2)
        #v = pickle.loads(r.get(img_hash))
        v = r.get(img_hash).decode() # decode() should be necessary so we have a proper string not that 'b' in front
        response = {
            "list": v
        }
    except:

        response = {
            "list" : 0
        }

    resp_pickled = jsonpickle.encode(response)
    return Response(response = resp_pickled, status = 200, mimetype = "application/json")




app.run(host="0.0.0.0", port=5000)
