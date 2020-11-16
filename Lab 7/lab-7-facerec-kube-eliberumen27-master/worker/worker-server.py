#
# Worker server
#
import pickle
import platform
from PIL import Image
import io
import os
import sys
import pika
import redis
import hashlib


hostname = platform.node()

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

##
## You provide this
##

# FACE REC STUFF OBAMA SAMPLE
import face_recognition

# obama_image = face_recognition.load_image_file("obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
#
# print("obama face encoding is", obama_face_encoding)


# TO DO

# RMQ Connection( after exporting the environment variables with my IP)
# params = pika.ConnectionParameters('rabbitmq')
# connection = pika.BlockingConnection(params)
# channel = connection.channel()
# channel.queue_declare(queue='toWorker')
params = pika.ConnectionParameters(host=rabbitMQHost)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue = "toWorker")

# CALLBACK where we process the image data that came in from the rest server
# Image data will be found in the body paramater
# Note: The callback runs everytime the worker reads a message from our Q
def callback(ch, method, properties, body):
    # commenting the following out to hide the spam and just getting what we want in pieces
    # print(" [x] %r:%r" % (method.routing_key, body), file = sys.stderr)

    # data1 = URL where image is from or filename, data2 = hash of the image, data3 = actual image data
    data1, data2, data3 = pickle.loads(body)
    print("Image URL or Filename = ", data1, "\nImage Hash", data2)

    # data3 contains our image data
    imgBytes = io.BytesIO(data3)


    # Set up redis DBs, one by one based on their purpose
    # NAME TO HASH DB (db=1)
    redisNameToHash = redis.Redis(host=redisHost, db=1)    # Key -> Value
    redisNameToHash.set(data1, data2)
    print("Getting Image Hash based on the URL or filename")
    print("filename or URL = ", data1)
    hash_val = redisNameToHash.get(data1) # No need to do a pickle loads again since we already unpacked object
    print("Hash value for that filename/URL: ", hash_val.decode()) # decode() to remove the 'b'

    # HASH TO NAME (db=2), for every hash, we gotta have a value that is a redis set or list holding names/urls
    redisHashToName = redis.Redis(host=redisHost, db=2)    # Key -> Set
    redisHashToName.set(data2, data1) # putting hash in as the key
    print("Getting URL or Filename based on the hash")
    name = redisHashToName.get(data2).decode() # Ususlly have to decode when getting from Redis DB
    print("Filename or URL = ", name)



    # HASH TO SET OF FACES RECOGNIZED FROM IMAGE (db=3)
    redisHashToFaceRec = redis.Redis(host=redisHost, db=3) # Key -> Set
    # Was going to use Redis set but breaking down python list was easier
    # Load the uploaded image file as a bytestream with we got already
    img = face_recognition.load_image_file(imgBytes)
    # Get face encodings for any faces in the uploaded image and put in a list
    unknown_face_encodings = face_recognition.face_encodings(img)
    faces_list = [face for face in unknown_face_encodings] # one liner to give list of found faces to DB 3
    num_faces = len(faces_list)
    redisHashToFaceRec.set(data2, pickle.dumps(faces_list)) # On the other end can do pickle.loads(faces_list) to reconstruct
    print("There are {} faces in that image as follows: ".format(num_faces), redisHashToFaceRec.get(data2))



    # HASH TO SET OF HASHES OF MATCHING IMAGES
    # The worker should extract the list of faces in the image using face_recognition.face_encodings (see below). Then, for each face in that list, you should add the face and corresponding image to the Redis database and then compare those faces to all other faces in each image the database. For each image containing any matching face, you would add the images (hashes) of each image to the other such that eventually we can determine the set of images that contain matching faces. Once this
    redisHashToHashSet = redis.Redis(host=redisHost, db=4) # Key -> Set
    

# Worker pod consuming on queue, using our processsImage callback function
channel.basic_consume(queue='toWorker', on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
