**Dependencies:**

- Run the setup.sh script on both the server and client machine

Notes: 
- Might also need to install both flask, git and time on the host you're running this on if it doesn't already have it
- Might need to run(if grpcio not working):
  $ sudo python3 -m pip install grpcio
  $ python3 -m grpc_tools.protoc -I/home/<user>/<project_dir> --python_out=. --grpc_python_out=. <file>.proto


**Instructions**

Get the code on your local machine or on the networked VMs you are using

$ git clone <REPO URL>

Running REST Tests:

Get the server running

$ python3 rest-server.py

If it says that address is being used, you have to kill the previous server first with the following:

$ ps -Af | grep python

$ sudo kill -9 <PID> 

Run the client to make requests to the server for either the add or image service

$ python3 rest-client.py <GCP instance internal ip>:5000 image 1000
  
$ python3 rest-client.py <GCP instance internal ip>:5000 add 1000


Running gRPC Tests:

Get the server running

$ python3 grpc-server.py

If it says that address is being used, you have to kill the previous server first with the following:

$ ps -Af | grep python

$ sudo kill -9 <PID> 

Run the client to make requests to the server for either the add or image service

$ python3 grpc-client.py <GCP instance internal ip>:50051 image 1000
  
$ python3 grpc-client.py <GCP instance internal ip>:50051 add 1000






**Important "gotcha"**: Flask might already be using 0.0.0.0:5000 so check with ps -fA | grep python, then $ kill -9 <PID>
