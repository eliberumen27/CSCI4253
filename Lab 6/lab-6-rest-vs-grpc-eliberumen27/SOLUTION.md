
|  Method 	| Local  	| Same-Zone  	|  SameReg/Diff Zone 	| Europe west1-b(Belgium) |
|---------- |---------- |-------------- |-----------------------|--------|
|   REST add	| 2.64  	| 2.4  	| 2.7 	| 290
|   gRPC add	| 0.53  	| 0.45  	| 0.55   	| 60
|   REST img	| 3.40  	| 6.8  	| 8.1  	| 1180.2
|   gRPC img	| 6.3      | 7.2  	| 7.15 	| 66
|   PING        | .045      | 0.22     | 0.3      | 50 

***Ping***

The biggest difference in latency comes from the difference regions(US to Europe)

***Local***

In the case where the server and client are on the same VM, the gRPC add service outperforms the REST counterpart by being over 4 times faster. However the opposite true for the image services and this may due to the fact that gRPC serializes the data despite being on the same subnet and machine, and REST doesn't have to serialize the data being transferred.

***Different Machines/Same Zone***

The same is true for different machines in the same Zone as the case where both the client and server were on the same host. Although in this case it should be noted that REST for the image service was signicantly slower this time and performance much closer to the gRPC image service. We can expect more latency here due to "physical" distance between the instances. 

***Different Zone/Same Region***

Here we now see a bit more of the benefits of gRPC and the use of a single TCP connection for all requests and protocol buffers for compact data transfer. REST starts to suffer more when there is more physical network latency between systems since it is creating a new TCP connection for every request. As for the image services, gRPC now outperforms REST and it becomes clear that it works best for building very low latency distributed systems.

***Different Region(Europe)***

In the end we are able to conclude that gRPC works best for light weight services such as our add method, although when it comes to high latency due to physical distance between systems it still outperforms REST for heavier services such as our image method.

Our overall results support the use of gRPC for faster performing web services.

