import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    's3_output_path',
    'source_glue_database',
    'source_glue_table'
])

s3_output_path = args['s3_output_path']
source_glue_database = args['source_glue_database']
source_glue_table = args['source_glue_table']

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource0 = glueContext. \
    create_dynamic_frame. \
    from_catalog(database=source_glue_database, 
        table_name=source_glue_table, 
        transformation_ctx="datasource0")

applymapping1 = ApplyMapping.apply(
    frame = datasource0, 
    mappings = [
        ("id", "string", "id", "string"), 
        ("title", "string", "title", "string"), 
        ("clickable_url", "string", "clickable_url", "string"), 
        ("feed_position", "int", "feed_position", "int"), 
        ("created_utc", "int", "created_utc", "int"), 
        ("author", "string", "author", "string"), 
        ("selftext", "string", "selftext", "string"), 
        ("num_comments", "int", "num_comments", "int"), 
        ("distinguished", "string", "distinguished", "string"), 
        ("link_flair_text", "string", "link_flair_text", "string"), 
        ("score", "int", "score", "int"), 
        ("upvote_ratio", "double", "upvote_ratio", "double"), 
        ("url", "string", "url", "string"), 
        ("name", "string", "name", "string"), 
        ("platform", "string", "platform", "string"), 
        ("subreddit_name", "string", "subreddit_name", "string"), 
        ("req_timestamp", "int", "req_timestamp", "int"), 
        ("req_uuid", "string", "req_uuid", "string"), 
        ("limit", "int", "limit", "int"), 
        ("useragent", "string", "useragent", "string"), 
        ("num_posts_collected", "int", "num_posts_collected", "int"), 
        ("req_duration", "double", "req_duration", "double"), 
        ("partition_0", "string", "partition_0", "string"), 
        ("partition_1", "string", "partition_1", "string"), 
        ("partition_2", "string", "partition_2", "string"), 
        ("partition_3", "string", "partition_3", "string")
        ], 
        transformation_ctx = "applymapping1")

resolvechoice2 = ResolveChoice.apply(
    frame=applymapping1, 
    choice="make_struct", 
    transformation_ctx="resolvechoice2")

dropnullfields3 = DropNullFields.apply(
    frame=resolvechoice2, 
    transformation_ctx="dropnullfields3")

# coalesce parquet into one
# https://github.com/aws-samples/aws-glue-samples/blob/master/FAQ_and_How_to.md
partitioned_dataframe = dropnullfields3.toDF().repartition(1)
partitioned_dynamicframe = DynamicFrame.fromDF(partitioned_dataframe, glueContext, "partitioned_df")

datasink4 = glueContext.write_dynamic_frame.from_options(
    frame = partitioned_dynamicframe, 
    connection_type = "s3", 
    connection_options = {
        "path": s3_output_path,
        "groupFiles": "inPartition",
        "groupSize": 1024 * 1024,
        "partitionKeys": ["partition_0", "partition_1", "partition_2", "partition_3"],
        }, 
        format = "parquet", 
        transformation_ctx = "datasink4")

job.commit()