import logging
import sys
import boto3
from botocore.exceptions import ClientError

"""
Functions in this module were adapted from Python Code Samples for Amazon SQS:
https://docs.aws.amazon.com/code-samples/latest/catalog/code-catalog-python-example_code-sqs.html
"""


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_queue(sqs, name):
    """
    Gets an SQS queue by name.

    :param sqs: The boto3 sqs resource instance.
    :param name: The name that was used to create the queue.
    :return: A Queue object.
    """
    try:
        queue = sqs.get_queue_by_name(QueueName=name)
        logger.info(f'Got queue "{name}" with URL={queue.url}')
    except ClientError as error:
        logger.exception(f'Error getting queue: "{name}"')
        raise error
    else:
        return queue


def pack_subreddit_message(subreddit):
    return {
        'body': subreddit,
        'attributes': {
            'subreddit_url': {'StringValue': f'http://reddit.com/r/{subreddit}/', 'DataType': 'String'}
        }
    }


def send_messages(queue, messages):
    """
    Send a batch of messages in a single request to an SQS queue.
    This request may return overall success even when some messages were not sent.
    The caller must inspect the Successful and Failed lists in the response and
    resend any failed messages.

    :param queue: The queue to receive the messages.
    :param messages: The messages to send to the queue. These are simplified to
                     contain only the message body and attributes.
    :return: The response from SQS that contains the list of successful and failed
             messages.
    """
    try:
        entries = [{
            'Id': str(ind),
            'MessageBody': msg['body'],
            'MessageAttributes': msg['attributes']
        } for ind, msg in enumerate(messages)]

        response = queue.send_messages(Entries=entries)

        if 'Successful' in response:
            for msg_meta in response['Successful']:
                logger.info(
                    "Message sent: %s: %s",
                    msg_meta['MessageId'],
                    messages[int(msg_meta['Id'])]['body']
                )
        if 'Failed' in response:
            for msg_meta in response['Failed']:
                logger.warning(
                    "Failed to send: %s: %s",
                    msg_meta['MessageId'],
                    messages[int(msg_meta['Id'])]['body']
                )
                
    except ClientError as error:
        logger.exception(f'Send messages failed to queue: {queue}')
        raise error
    else:
        return response
