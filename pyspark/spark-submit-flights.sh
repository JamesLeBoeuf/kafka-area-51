
# DONT FORGET TO CHANGE OUT ZOOKEEPER AND BOOTSTRAP SERVER MSK ENDPOINTS!
# AWS cli command to copy python file after changing new MSK endpoints
# aws s3 cp /Users/james/projects/data_engineering/wcd_de_bootcamp/wcd_de_final/pyspark_code/wcd_streaming_flights.py s3://wcd-de-final-streaming/wcd_streaming_flights.py

# Spark submission to be used inside of EMR.
spark-submit \
    --master yarn \
    --deploy-mode client \
    --name wcd_de_final_streaming \
    --jars /usr/lib/hudi/hudi-spark-bundle.jar,/usr/lib/spark/external/lib/spark-avro.jar \
    --conf "spark.serializer=org.apache.spark.serializer.KryoSerializer" \
    --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.hudi.catalog.HoodieCatalog" \
    --conf "spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension" \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
    s3://wcd-de-final-streaming/wcd_streaming_flights.py
