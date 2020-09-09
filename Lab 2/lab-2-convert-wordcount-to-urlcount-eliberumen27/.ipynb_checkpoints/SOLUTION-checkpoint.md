**Commands in order to get running on Dataproc in GCP:**

git clone https://github.com/cu-csci-4253-datacenter-fall-2020/lab-2-convert-wordcount-to-urlcount-eliberumen27.git
`vi MakeFile` (to set the STREAM_JAR file correctly)
`hdfs dfs -mkdir hdfs:///user/(whoami)` (to create the user directory that doesn't already exist in dataproc env)

Before I run make stream:

`hdfs dfs -rm -r stream-output` - We move the stream-ouput before running it again to generate the new output
`make prepare` - Prepares out input
`sudo apt-get install time` - package necessary to run `time hadoop jar (STREAM_JAR)`

Now run make stream:
`make stream`

Timing on 2 worker nodes

Timing on 4 worker nodes