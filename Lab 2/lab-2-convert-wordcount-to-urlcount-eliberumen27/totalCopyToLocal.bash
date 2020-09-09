# Combine output files and copy them to "local"

hadoop fs -cat stream-output/* | hadoop fs -put - stream-output/total # combine
hdfs dfs -copyToLocal stream-output/total total # copy to local
~ 
~ 
~ 
~ 
~ 
