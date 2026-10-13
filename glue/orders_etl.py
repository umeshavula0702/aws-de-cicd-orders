import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, count, sum as spark_sum, to_date, trim, upper


args = getResolvedOptions(sys.argv, ["JOB_NAME", "DATA_BUCKET", "ENV"])
DATA_BUCKET = args["DATA_BUCKET"]
ENV = args["ENV"]

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args["JOB_NAME"], args)

input_path = f"s3://{DATA_BUCKET}/{ENV}/input/orders/"
curated_path = f"s3://{DATA_BUCKET}/{ENV}/curated/orders/"
gold_path = f"s3://{DATA_BUCKET}/{ENV}/gold/order_summary/"

print(f"Reading source data from: {input_path}")
orders_df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(input_path)
)

print(f"Source record count: {orders_df.count()}")

clean_df = (
    orders_df
    .withColumn("status", upper(trim(col("status"))))
    .withColumn("amount", col("amount").cast("double"))
    .withColumn("order_date", to_date(col("order_date"), "yyyy-MM-dd"))
    .filter(col("order_id").isNotNull())
    .filter(col("customer_id").isNotNull())
    .filter(col("amount").isNotNull())
    .filter(col("amount") > 0)
)

print(f"Clean record count: {clean_df.count()}")

(
    clean_df
    .write
    .mode("overwrite")
    .parquet(curated_path)
)

summary_df = (
    clean_df
    .groupBy("country", "status")
    .agg(
        count("*").alias("order_count"),
        spark_sum("amount").alias("total_amount"),
    )
)

(
    summary_df
    .write
    .mode("overwrite")
    .parquet(gold_path)
)

print(f"Curated output: {curated_path}")
print(f"Gold output: {gold_path}")
print("Glue ETL completed successfully")

job.commit()
