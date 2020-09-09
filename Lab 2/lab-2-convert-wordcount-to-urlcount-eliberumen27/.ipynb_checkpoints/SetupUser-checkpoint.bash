#1/bin/bash

# The following is needed to set up user in dataproc environment on master node
user=$1
cluster='cluster-lab2'
echo "making dir in hdfs path for my user"
hdfs dfs -mkdir hdfs://$cluster-m/user/$user
echo "run make prepare"
make run
make prepare
echo "run make stream"
make stream 