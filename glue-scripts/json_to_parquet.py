import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
## @type: DataSource
## @args: [database = "dev-reddit-pipeline-1-database", table_name = "dev_ssrp_1_raw_reddit_posts_json", transformation_ctx = "datasource0"]
## @return: datasource0
## @inputs: []
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "dev-reddit-pipeline-1-database", table_name = "dev_ssrp_1_raw_reddit_posts_json", transformation_ctx = "datasource0")
## @type: ApplyMapping
## @args: [mapping = [("id", "string", "id", "string"), ("title", "string", "title", "string"), ("clickable_url", "string", "clickable_url", "string"), ("feed_position", "int", "feed_position", "int"), ("created_utc", "int", "created_utc", "int"), ("author", "string", "author", "string"), ("selftext", "string", "selftext", "string"), ("num_comments", "int", "num_comments", "int"), ("distinguished", "string", "distinguished", "string"), ("link_flair_text", "string", "link_flair_text", "string"), ("score", "int", "score", "int"), ("upvote_ratio", "double", "upvote_ratio", "double"), ("url", "string", "url", "string"), ("name", "string", "name", "string"), ("platform", "string", "platform", "string"), ("subreddit_name", "string", "subreddit_name", "string"), ("req_timestamp", "int", "req_timestamp", "int"), ("req_uuid", "string", "req_uuid", "string"), ("limit", "int", "limit", "int"), ("useragent", "string", "useragent", "string"), ("num_posts_collected", "int", "num_posts_collected", "int"), ("req_duration", "double", "req_duration", "double"), ("partition_0", "string", "partition_0", "string"), ("partition_1", "string", "partition_1", "string"), ("partition_2", "string", "partition_2", "string"), ("partition_3", "string", "partition_3", "string")], transformation_ctx = "applymapping1"]
## @return: applymapping1
## @inputs: [frame = datasource0]
applymapping1 = ApplyMapping.apply(frame = datasource0, mappings = [("id", "string", "id", "string"), ("title", "string", "title", "string"), ("clickable_url", "string", "clickable_url", "string"), ("feed_position", "int", "feed_position", "int"), ("created_utc", "int", "created_utc", "int"), ("author", "string", "author", "string"), ("selftext", "string", "selftext", "string"), ("num_comments", "int", "num_comments", "int"), ("distinguished", "string", "distinguished", "string"), ("link_flair_text", "string", "link_flair_text", "string"), ("score", "int", "score", "int"), ("upvote_ratio", "double", "upvote_ratio", "double"), ("url", "string", "url", "string"), ("name", "string", "name", "string"), ("platform", "string", "platform", "string"), ("subreddit_name", "string", "subreddit_name", "string"), ("req_timestamp", "int", "req_timestamp", "int"), ("req_uuid", "string", "req_uuid", "string"), ("limit", "int", "limit", "int"), ("useragent", "string", "useragent", "string"), ("num_posts_collected", "int", "num_posts_collected", "int"), ("req_duration", "double", "req_duration", "double"), ("partition_0", "string", "partition_0", "string"), ("partition_1", "string", "partition_1", "string"), ("partition_2", "string", "partition_2", "string"), ("partition_3", "string", "partition_3", "string")], transformation_ctx = "applymapping1")
## @type: ResolveChoice
## @args: [choice = "make_struct", transformation_ctx = "resolvechoice2"]
## @return: resolvechoice2
## @inputs: [frame = applymapping1]
resolvechoice2 = ResolveChoice.apply(frame = applymapping1, choice = "make_struct", transformation_ctx = "resolvechoice2")
## @type: DropNullFields
## @args: [transformation_ctx = "dropnullfields3"]
## @return: dropnullfields3
## @inputs: [frame = resolvechoice2]
dropnullfields3 = DropNullFields.apply(frame = resolvechoice2, transformation_ctx = "dropnullfields3")
## @type: DataSink
## @args: [connection_type = "s3", connection_options = {"path": "s3://dev-reddit-pipeline-1-us-east-1-reddit-data/data/raw_reddit_posts_parquet/"}, format = "parquet", transformation_ctx = "datasink4"]
## @return: datasink4
## @inputs: [frame = dropnullfields3]
datasink4 = glueContext.write_dynamic_frame.from_options(frame = dropnullfields3, connection_type = "s3", connection_options = {"path": "s3://dev-reddit-pipeline-1-us-east-1-reddit-data/data/raw_reddit_posts_parquet/", "partitionKeys": ["partition_0", "partition_1", "partition_2", "partition_3"]}, format = "parquet", transformation_ctx = "datasink4")
job.commit()