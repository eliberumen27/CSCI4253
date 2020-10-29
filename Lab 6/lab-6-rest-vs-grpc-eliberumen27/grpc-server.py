import grpc
from concurrent import futures
import time
from PIL import Image
import io

# import the generated classes
import sum_pb2
import sum_pb2_grpc

# import the original add.py
#import add


class addServicer(sum_pb2_grpc.addServicer):
    def add(self, request, context):
        response = sum_pb2.addMsg()
        response.a = request.a  + request.b
        #response.a = add.add(request.a,request.b)
        return response

class imageServicer(sum_pb2_grpc.imageServicer):
    def image(self, request, context):
        response = sum_pb2.addMsg()
        ioBuffer = io.BytesIO(request.img)
        i = Image.open(ioBuffer)
        response.a = i.size[0]
        response.b = i.size[1] 
        return response
        
        
        
        #return sum_pb2.addMsg()
        #response.img = image.image(request.img)
        
# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

sum_pb2_grpc.add_addServicer_to_server(
        addServicer(), server)

sum_pb2_grpc.add_imageServicer_to_server(
        imageServicer(), server)

print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
