USER=$(shell whoami)

##
## Configure the Hadoop classpath for the GCP dataproc enviornment
##

HADOOP_CLASSPATH=$(shell hadoop classpath)

WordCount1.jar: WordCount1.java
	javac -classpath $(HADOOP_CLASSPATH) -d ./ WordCount1.java
	jar cf WordCount1.jar WordCount1*.class	
	-rm -f WordCount1*.class

prepare:
	-hdfs dfs -mkdir input
	curl https://en.wikipedia.org/wiki/Apache_Hadoop > /tmp/input.txt
	hdfs dfs -put /tmp/input.txt input/file01
	curl https://en.wikipedia.org/wiki/MapReduce > /tmp/input.txt
	hdfs dfs -put /tmp/input.txt input/file02

filesystem:
	-hdfs dfs -mkdir /user
	-hdfs dfs -mkdir /user/$(USER)

run: WordCount1.jar
	-rm -rf output
	hadoop jar WordCount1.jar WordCount1 input output


##
## You may need to change the path for this depending
## on your Hadoop / java setup
##
#HADOOP_V=3.2.1
STREAM_JAR = /usr/lib/hadoop-mapreduce/hadoop-streaming.jar
# First things we do are remove the total local file from prev run, and remove stream-output dir from HDFS
stream:
	-rm total
	-hdfs dfs -f -R stream-output
	time hadoop jar $(STREAM_JAR) \
	-mapper URLMapper.py \
	-reducer URLReducer.py \
	-file URLMapper.py -file URLReducer.py \
	-input input -output stream-output
