from pyspark.sql.session import SparkSession
from pyspark.sql.functions import col, from_json

application_name = 'wcd_streaming_application'
schema_file = 's3://wcd-de-final-streaming/schema/flight_status.json'
# Amazon MSK
msk_bootstrap_server_endpoint = 'b-3.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:9092,b-2.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:9092,b-1.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:9092'
msk_zookeeper_endpoint = 'z-1.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:2181,z-2.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:2181,z-3.wcddefinal262.2d3qne.c13.kafka.us-east-1.amazonaws.com:2181'

kafka_topic_name = 'dbserver1.flights.flight_status'
starting_offset = 'latest'
checkpoint_location = 's3://wcd-de-final-streaming/checkpoint/checkpoint_after_payload'
query_name = 'wcd_streaming_flight_status_app'
glue_database_name = 'wcd_de_final_flights'
record_key_field = 'record_id'
partition_field = 'origin_country'
table_name = 'flight_status'
# Hoodie has...
# COPY_ON_WRITE : read optimized. Light on read. Heavy on write.
## Data in parquet format.
## When there is an upsert/insert request, data will be on the fly merged and write to disk in parquet.
## Prefered way

# MERGE_ON_READ : read heavy. Heavy on read. Light on write.
## Not going to validate the duplicate of the records on the fly, but only to compact the data (de-duplicate the records).
## Data in parquet + avro.
## Quickly write to data into disk (append only).
## Only taking care of deduplication (data shuffle, data rewrite) scheduled compactions or read + force data compaction

# .option('hoodie.insert.shuffle.parallelism', '100') \
# Increase size if data is bigger
# 100 means how many partitions we are going to use when we do a shuffle
def bus_batch_function(batchDF, batchID):
    batchDF.write.format('org.apache.hudi') \
        .option('hoodie.datasource.write.table.type', 'COPY_ON_WRITE') \
        .option('hoodie.datasource.write.precombine.field', 'event_time') \
        .option('hoodie.datasource.write.recordkey.field', record_key_field) \
        .option('hoodie.datasource.write.partitionpath.field', partition_field) \
        .option('hoodie.datasource.write.hive_style_partitioning', 'true') \
        .option('hoodie.database.hive_sync.database', glue_database_name) \
        .option('hoodie.database.hive_sync.enable', 'true') \
        .option('hoodie.datasource.hive_sync.table', table_name) \
        .option('hoodie.datasource.hive_sync.partition_fields', partition_field) \
        .option('hoodie.datasource.hive_sync.partition_extractor_class', 'org.apache.hudi.hive.MultiPartKeysValueExtractor') \
        .option('hoodie.table.name', table_name) \
        .option('hoodie.insert.shuffle.parallelism', '100') \
        .option('hoodie.upsert.shuffle.parallelism', '100') \
        .mode('append') \
        .save('s3://wcd-de-final-streaming/hudi/flight_routes')


def spark_init(parser_name):
    ss = SparkSession \
        .builder \
        .appName(parser_name) \
        .getOrCreate()
    return ss

if __name__ == "__main__":
    spark = spark_init(application_name)
    schema = spark.read.json(schema_file).schema

    df = spark.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers', msk_bootstrap_server_endpoint) \
        .option('subscribe', kafka_topic_name) \
        .option('startingOffsets', starting_offset) \
        .load()

    df.printSchema()

    transformDF = df.select(from_json(col("value").cast("string"), schema).alias("value"))

    transformDF.select("value.payload.after.*") \
        .writeStream \
        .option("checkpointLocation", checkpoint_location) \
        .queryName(query_name) \
        .foreachBatch(bus_batch_function) \
        .start() \
        .awaitTermination()
