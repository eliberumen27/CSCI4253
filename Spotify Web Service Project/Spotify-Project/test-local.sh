kubectl apply -f mysql/mysql-deployment.yaml
kubectl apply -f mysql/mysql-service.yaml
kubectl apply -f rabbitmq/rabbitmq-deployment.yaml
kubectl apply -f rabbitmq/rabbitmq-service.yaml

kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 &
kubectl port-forward --address 0.0.0.0 service/mysql 3306:3306 &

# To kill the port-forward processes us e.g. "ps augxww | grep port-forward"
# to identify the processes ids
#
# Dependencies: sudo pip3 install .......
