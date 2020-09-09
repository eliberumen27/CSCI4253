### Commands in order to get running on Dataproc in GCP: 

**Necessary Software Installed:**

- Hadoop(Either 3.2.1 in coding.csel.io or 2.9.2 on GCP)
- Hadoop Streaming Jar
- Git
- Java
- Python

**Setting up on Dataproc Env before I run make stream

git clone https://github.com/cu-csci-4253-datacenter-fall-2020/lab-2-convert-wordcount-to-urlcount-eliberumen27.git

`vi MakeFile` - (to set the STREAM_JAR file correctly to /usr/lib/hadoop-mapreduce/hadoop-streaming.jar)
`vi Makefile` - add the following to make stream: `time hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar`
`hdfs dfs -mkdir hdfs:///user/(whoami)` - (OPTIONAL to create the user directory that doesn't already exist in Qwiklabs dataproc env)

`sudo apt-get install time` - linux command package necessary to run `time hadoop jar (STREAM_JAR)`
`make prepare` - Prepares our input in the HDFS(to be able to store the files across the cluster of machines)

**Now run our MapReduce with make stream:**

`make stream`

`hadoop fs -cat stream-output/* | hadoop fs -put - stream-output/total` - We concatenate our parts of output into one file
`hdfs dfs -copyToLocal stream-output/total total` - We bring our output file over to "local" from HDFS

`hdfs dfs -rm -r stream-output` - We remove the stream-ouput before running make stream each subsequent time to generate the new output

**Description of URLMapper/URLReducer Solution:**

The mapper parses out all of the URLs from each line it is reading from STDIN and gives them a trivial count of 1 and sends to STDOUT
The reducer takes the output from the mapper and starts to track occurrences and prints out urls that appear over 5 times.

The output goes to the stream-output directory in HDFS, those files might need to get concatenated, then we CopyToLocal

**Timing on 2 worker nodes**

20/09/09 00:21:16 INFO mapreduce.Job: Job job_1599606664747_0005 completed successfully
20/09/09 00:21:16 INFO mapreduce.Job: Counters: 50
        File System Counters
                FILE: Number of bytes read=61057
                FILE: Number of bytes written=6259842
                FILE: Number of read operations=0
                FILE: Number of large read operations=0
                FILE: Number of write operations=0
                HDFS: Number of bytes read=459201
                HDFS: Number of bytes written=109
                HDFS: Number of read operations=101
                HDFS: Number of large read operations=0
                HDFS: Number of write operations=21
        Job Counters 
                Killed map tasks=1
                Launched map tasks=22
                Launched reduce tasks=7
                Data-local map tasks=22
                Total time spent by all maps in occupied slots (ms)=426534
                Total time spent by all reduces in occupied slots (ms)=100500
                Total time spent by all map tasks (ms)=142178
                Total time spent by all reduce tasks (ms)=33500
                Total vcore-milliseconds taken by all map tasks=142178
                Total vcore-milliseconds taken by all reduce tasks=33500
                Total megabyte-milliseconds taken by all map tasks=436770816
                Total megabyte-milliseconds taken by all reduce tasks=102912000
        Map-Reduce Framework
                Map input records=1925
                Map output records=1730
                Map output bytes=57536
                Map output materialized bytes=61939
                Input split bytes=2288
                Combine input records=0
                Combine output records=0
                Reduce input groups=1374
                Reduce shuffle bytes=61939
                Reduce input records=1730
                Reduce output records=4
                Spilled Records=3460
                Shuffled Maps =154
                Failed Shuffles=0
                Merged Map outputs=154
                GC time elapsed (ms)=4106
                CPU time spent (ms)=26350
                Physical memory (bytes) snapshot=13646667776
                Virtual memory (bytes) snapshot=126455115776
                Total committed heap usage (bytes)=12143558656
        Shuffle Errors
                BAD_ID=0
                CONNECTION=0
                IO_ERROR=0
                WRONG_LENGTH=0
                WRONG_MAP=0
                WRONG_REDUCE=0
        File Input Format Counters 
                Bytes Read=456913
        File Output Format Counters 
                Bytes Written=109
20/09/09 00:21:16 INFO streaming.StreamJob: Output directory: stream-output
7.88user 0.33system 0:46.67elapsed 17%CPU (0avgtext+0avgdata 272960maxresident)k
0inputs+1312outputs (0major+33753minor)pagefaults 0swaps

**Timing on 4 worker nodes**

20/09/09 00:34:13 INFO mapreduce.Job: Job job_1599611417729_0001 completed successfully
20/09/09 00:34:13 INFO mapreduce.Job: Counters: 51
        File System Counters
                FILE: Number of bytes read=61105
                FILE: Number of bytes written=13047983
                FILE: Number of read operations=0
                FILE: Number of large read operations=0
                FILE: Number of write operations=0
                HDFS: Number of bytes read=559141
                HDFS: Number of bytes written=109
                HDFS: Number of read operations=213
                HDFS: Number of large read operations=0
                HDFS: Number of write operations=45
        Job Counters 
                Killed map tasks=1
                Launched map tasks=46
                Launched reduce tasks=15
                Data-local map tasks=31
                Rack-local map tasks=15
                Total time spent by all maps in occupied slots (ms)=951690
                Total time spent by all reduces in occupied slots (ms)=216531
                Total time spent by all map tasks (ms)=317230
                Total time spent by all reduce tasks (ms)=72177

When comparing the job running with 2 worker nodes and 4 worker nodes, it was surprising to see the total time spent by the 4 worker nodes to be larger.

**Combiner implementation in Java:**

Using a combiner could potentially cause issues when our reducer has certain constraints. For example if we have occurrences of "cat" that get combined to be 3 in one mapper and 4 in another mapper, then before they get to the reducer where the reducer has a constraint of processing (K, V) where V is greater than 6, then we have prevented "cat" from ever getting to the reducer althought "cat" totals to 7. Essentially we have to be smart about when to use combiners and it's generally when the order of prcoessing doesn't effect the result.

**Things to revert if trying to run "locally" (ie: coding.csel.io environment):**

Change the streaming .jar in MakeFile back to 3.2.1 found in /usr/local/...