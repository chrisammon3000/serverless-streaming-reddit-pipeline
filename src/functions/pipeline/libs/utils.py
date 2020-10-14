import os
import sys
import json
import copy
import logging
import uuid
from datetime import datetime
import time
from timeit import default_timer as timer
import boto3
import praw
from libs.dict_smasher import remove_listed_dict_keys
#from src.functions.pipeline.libs.dict_smasher import remove_listed_dict_keys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Reddit login credentials
PRAW_CID = os.environ["PRAW_CID"]
PRAW_SECRET = os.environ["PRAW_SECRET"]
PRAW_PASSWORD = os.environ["PRAW_PASSWORD"]
PRAW_USERAGENT = "ssrp" #os.environ["PRAW_USERAGENT"] "serverless-streaming-reddit-pipeline"
PRAW_USERNAME = os.environ["PRAW_USERNAME"]

# PRAW API params
PRAW_LIMIT = int(os.environ["PRAW_LIMIT"])

# AWS SDK utils
def s3_get_json(bucket, s3_object):

    s3 = boto3.resource('s3')

    logger.info(f'Retrieving "{s3_object}" from "{bucket}"...')
    try: 
        content_object = s3.Object(bucket, s3_object)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        logger.info(f'"{s3_object}" retrieved from "{bucket}"')
        return json.loads(file_content)

    except Exception as error:
        logger.exception(f'Could not retrieve "{s3_object}" from "{bucket}"')
        raise error


def process_or_store_batch(data_chunks, delivery_stream):
    
    firehose_client = boto3.client('firehose', region_name="us-east-1")

    # Format for batch streaming must be a list of dictionaries
    batch = []
    for chunk in data_chunks:
        chunk_records = []
        for post in chunk:
            chunk_records.append(
                {
                    'Data': (json.dumps(post, ensure_ascii=False)).encode('utf8')
                }
            )
            
        batch.append(chunk_records)
            
    for idx0, batch_chunk in enumerate(batch):
        
        logger.info(f'--------STREAMING BATCH {idx0+1}/{len(batch)}--------')
        logger.info(f'Records: {len(batch_chunk)}')
        
        try:
            response = firehose_client.put_record_batch(
                DeliveryStreamName=delivery_stream,
                Records = batch_chunk
            )
            
            logging.debug(response)
            logger.info(f'Content length: {response["ResponseMetadata"]["HTTPHeaders"]["content-length"]}')
            logger.info(f'Response Status Code: {response["ResponseMetadata"]["HTTPStatusCode"]}')
            logger.info(f'FailedPutCount: {response["FailedPutCount"]}')
            logger.info(f'RetryAttempts: {response["ResponseMetadata"]["RetryAttempts"]}')
            
        except Exception as error:
            logger.exception(f'PutRecordBatch failed')
            raise error

    return response


def get_subreddit(reddit, subreddit_name, limit=1000):
    
        try:

            subreddit = reddit.subreddit(subreddit_name).new(limit=limit)
            
        except Exception as err:
            logger.error("Failed to create Reddit instance")
            raise err
            
        return subreddit
    

def extract_posts(subreddit, subreddit_name):
        start_extract = timer()
        
        collected_posts = []
        
        req_data = {
            "platform": "Reddit",
            "subreddit_name": subreddit_name,
            "req_timestamp": int(time.time()),
            "req_uuid": str(uuid.uuid4()),
            "limit": PRAW_LIMIT,
            "useragent": PRAW_USERAGENT
        }
        
        try:
            for idx0, post in enumerate(subreddit):
                
                post_vars = vars(post)
                
                post_dict = {
                    "id": post_vars["id"],
                    "title": post_vars["title"],
                    "clickable_url": "https://www.reddit.com" + post_vars["permalink"],
                    "feed_position": idx0 + 1,
                    "created_utc": int(post_vars["created_utc"]),
                    "author": str(post_vars["author"]),
                    "selftext": post_vars["selftext"].replace('\n', ''),
                    "num_comments": post_vars["num_comments"],
                    "distinguished": post_vars["distinguished"],
                    "link_flair_text": post_vars["link_flair_text"],
                    "score": post_vars["score"],
                    "upvote_ratio": post_vars["upvote_ratio"],
                    "url": post_vars["url"],
                    "name": post_vars["name"]
                }
                
                # Significantly increases execution time because of PRAW's rate limiting, beware
                #post_dict["comments"] = extract_comments(post, 10)
                
                post_dict.update(req_data)
                collected_posts.append(post_dict)

            num_collected = len(collected_posts)

            for post in collected_posts:
                post['num_posts_collected'] = num_collected
                post["req_duration"] = timer() - start_extract

        except Exception as err:
            logger.error("Failed to extract posts")
            raise err
        
        return collected_posts
    
    
def extract_comments(post, num_comment=10):
    
    comments = []
    
    for comment in post.comments[:num_comment]:
        comment_dict = {
            "id": comment.id,
            "link_id": comment.link_id,
            "created_utc": int(comment.created_utc),
            "distinguished": comment.distinguished,
            "score": comment.score,
            "body": comment.body.replace('\n', ''),
            "clickable_url": "https://www.reddit.com" + comment.permalink
        }
        
        try:
            comment_dict["author"] = comment.author.name
        except Exception as err:
            logger.warn(f'No author: {err}')
            comment_dict["author"] = ""
        
        comments.append(comment_dict)
        
    return comments


def collect_posts(subreddit_name, limit):

    start_collect = timer()

    try:
        reddit = praw.Reddit(client_id=PRAW_CID,
                            client_secret=PRAW_SECRET, password=PRAW_PASSWORD,
                            user_agent=PRAW_USERAGENT, username=PRAW_USERNAME)

        user = reddit.user.me()

        if user != PRAW_USERNAME:
            raise Exception(f'Error: Incorrect user: "{user}"')
        else:
            logger.info(f'Logged in user {user}')

    except Exception as error:
        logger.exception(f'Error: Unable to login: "{user}"')
        raise error
    
    # Get subreddit instance and record time
    logger.info(f'Creating Reddit instance')
    subreddit = get_subreddit(reddit, subreddit_name, limit=limit)

    # Collect posts
    logger.info(f'Extracting posts data...')
    start_extract = timer()
    collected_posts = extract_posts(subreddit=subreddit, subreddit_name=subreddit_name)
    stop_extract = timer() - start_extract
    logger.info(f"{len(collected_posts)} posts extracted in {round(stop_extract, 2)} s")
    
    stop_collect = timer() - start_collect
    logger.info(f"Total Elapsed time: {round(stop_collect, 2)} s")
    
    return collected_posts


# Export to handler
def stream_posts(subreddit_name, delivery_stream, limit):

    logger.info(f'********BEGIN COLLECTION********')
    logger.info(f'Username: {PRAW_USERNAME}')
    logger.info(f'Agent: {PRAW_USERAGENT}')
    logger.info(f'Max posts: {limit}')
    logger.info(f'Subreddit: "{subreddit_name}"')
    logger.info(f'{"https://www.reddit.com/r/" + subreddit_name}')
    
    try:
        # Collect media posts
        data = collect_posts(subreddit_name=subreddit_name, limit=limit)

        if not data:
            logger.info('No data, skipping streaming')
            logger.info(f'********END COLLECTION********')
            return 0

        start_stream = timer()
        
        # Group into chunks of size n posts
        n = 250
        data_chunks = [data[i:i+n] for i in range(0, len(data), n)]
        
        # Batch stream to Kinesis Firehose
        response = process_or_store_batch(data_chunks, delivery_stream)
        stop_stream = timer() - start_stream
        logger.info("-----------------------------------")
        batch_or_batches = "batches" if len(data_chunks) > 1 else "batch"
        logger.info(f"{len(data_chunks)} {batch_or_batches} of {len(data)} posts streamed in {round(stop_stream, 2)} s")

        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            raise Exception(f'Bad Response: {status_code}')
        
        logger.info(f'********END COLLECTION********')

    except Exception as err:
        logger.exception(err)
        raise err
    
    return 0
