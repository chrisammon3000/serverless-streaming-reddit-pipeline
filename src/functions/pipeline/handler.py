import os
import logging
import time
import random
import boto3
from libs.utils import stream_posts, s3_get_json
from libs.sqs_utils import pack_subreddit_message, get_queue, send_messages

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.debug(os.environ)

# PRAW API params
PRAW_LIMIT = int(os.environ["PRAW_LIMIT"])

# AWS Resources
DELIVERY_STREAM = os.environ["DELIVERY_STREAM"]
S3_CONFIG_BUCKET = os.environ['S3_CONFIG_BUCKET']
SQS_QUEUE = os.environ['SQS_QUEUE']

# Files
S3_LOAD_SUBREDDITS = os.environ['S3_LOAD_SUBREDDITS']

# Batch send subreddits to SQS (fan out)
def queue_subreddits(event, context):

    logger.debug(os.environ)

    logger.info(f'Retrieving config file "{S3_LOAD_SUBREDDITS}" from S3 bucket "{S3_CONFIG_BUCKET}"')
    load_subreddits = s3_get_json(S3_CONFIG_BUCKET, S3_LOAD_SUBREDDITS)

    subreddits = load_subreddits["subreddits"]
    logger.debug(f'Queuing subreddits: {subreddits}')

    # Pack messages
    messages = [pack_subreddit_message(subreddit) for subreddit in subreddits]

    # Break into sublists of length 10 for batching
    messages_list = [messages[x:x+10] for x in range(0, len(messages), 10)]

    # Send batches
    sqs = boto3.resource('sqs')
    logger.info(f'Initializing SQS queue: "{SQS_QUEUE}"...')
    queue = get_queue(sqs, SQS_QUEUE)

    logger.info(f'Posting messages to queue "{SQS_QUEUE}"')
    for messages in messages_list:
        send_messages(queue, messages)

    return 0


# Collect individual subreddit data
def collect_data(event, context):

    logger.debug(f'Received event: {event}')
    logger.debug(os.environ)

    subreddit_name = str(event['Records'][0]["body"])

    # Avoid too many requests at once
    sleep = random.uniform(1, 3)
    logger.info(f'Waiting {round(sleep, 2)} s...')
    time.sleep(sleep)

    success = stream_posts(subreddit_name=subreddit_name, delivery_stream=DELIVERY_STREAM, limit=PRAW_LIMIT)

    return success



