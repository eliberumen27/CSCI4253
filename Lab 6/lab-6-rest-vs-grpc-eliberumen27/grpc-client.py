import grpc

# import the generated classes
import sum_pb2
import sum_pb2_grpc
import struct
import sys
from time import perf_counter

# Via CLI we pass in the address to the gRPC server including the port(50051)
addr = sys.argv[1]
endpoint = sys.argv[2]
num_tests = int(sys.argv[3])
img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()

# open a gRPC channel
channel = grpc.insecure_channel(addr)

# add call
if endpoint == 'add':
    stub = sum_pb2_grpc.addStub(channel)

    timer1_start = perf_counter()
    for i in range(num_tests):
        number = sum_pb2.addMsg(a=5,b=4)
        resp = stub.add(number)
        print(resp.a)
    timer1_stop = perf_counter()

    total = timer1_stop - timer1_start
    avg = total/num_tests
    print(avg)

else:

    # image call
    stub = sum_pb2_grpc.imageStub(channel)
    timer1_start = perf_counter()
    for i in range(num_tests):
        number = sum_pb2.imageMsg(img=img)
        resp = stub.image(number)
        print(resp.a,resp.b)
    timer1_stop = perf_counter()

    total = timer1_stop - timer1_start
    avg = total/num_tests
    print(avg)
