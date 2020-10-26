

serverless-streaming-reddit-pipeline
==============================

Streams JSON data from any number of Reddit forums (subreddits) into an S3 bucket and converts to Parquet. Uses Lambdas, SQS, Kinesis Firehose, and AWS Glue to build a serverless data lake which can be queried with Athena or Visualized with Quicksight.

## Description
Subreddits are queued by a scheduled Lambda function and assigned to individual Lambda functions which collect all available posts for that subreddit. The JSON data is streamed to an S3 bucket using Kinesis Firehose, crawled by a Glue Crawler, converted to Parquet by a Glue ETL Job, and re-crawled. 

![AWS Architecture](img/architecture.png)

## Getting Started

### Prerequisites
* [awscli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and [credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
* [Serverless](https://www.serverless.com/framework/docs/getting-started/) framework
* [Docker](https://docs.docker.com/get-docker/)
* [Reddit API credentials](https://www.reddit.com/prefs/apps) - click the button "create another app..."

### Setting up Environment
1. Clone this repo:
   ```
   git clone \
       --branch master --single-branch --depth 1 --no-tags \
       https://github.com/abk7777/serverless-streaming-reddit-pipeline.git
   ```
2. Install Serverless Python Requirements plugin
   ```
   cd serverless-streaming-reddit-pipeline
   npm install --save serverless-python-requirements
   ```

3. Input Reddit API credentials in `scripts/set_env.sh`:
   ```
   # set_env.sh

   STAGE=prod
   APP_NAME=reddit-pipeline
   REGION=us-east-1
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   STACK_NAME=$STAGE-$APP_NAME-$APP_VERSION-$REGION

   # Reddit API Params
   CLIENT_ID=<CLIENT_ID>
   CLIENT_SECRET=<CLIENT_SECRET>
   USERAGENT=ssrp
   USERNAME=<USERNAME>
   PASSWORD=<PASSWORD>
   ```

### Deploy AWS Infrastructure
These instructions will deploy a stack named `prod-reddit-pipeline-1-us-east-1` using AWS CloudFormation.

   Run `scripts/deploy.sh` to deploy the stack:
   ```
   cd serverless-streaming-reddit-pipeline
   bash scripts/deploy.sh
   ```

The script will prompt to update SSM Parameters and deploy Serverless Framework, respond with 'y' for the first deployment and 'n' for stack updates.

### Invoke Lambda
   ```
   cd src/functions/pipeline
   serverless invoke --function queueSubreddits \
   --stage prod \
   --region us-east-1 \
   --log
   ```

Once `queueSubreddits` has run you can view the worker logs while they collect subreddit data in the CloudWatch log group for the `collectData` function.

### Querying in Athena

### Cleaning up
   Run `scripts/delete_pipeline.sh` to delete the stack (WARNING: this will delete all the data!):
   ```
   cd serverless-streaming-reddit-pipeline
   bash scripts/delete_pipeline.sh
   ```
   
## Contributors

**Primary (Contact) : [Gregory Lindsey](https://github.com/abk7777)**

[contributors-shield]: https://img.shields.io/github/contributors/abk7777/serverless-streaming-reddit-pipeline.svg?style=flat-square
[contributors-url]: https://github.com/abk7777/serverless-streaming-reddit-pipeline/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/abk7777/serverless-streaming-reddit-pipeline.svg?style=flat-square
[forks-url]: https://github.com/abk7777/serverless-streaming-reddit-pipeline/network/members
[stars-shield]: https://img.shields.io/github/stars/abk7777/serverless-streaming-reddit-pipeline.svg?style=flat-square
[stars-url]: https://github.com/abk7777/serverless-streaming-reddit-pipeline/stargazers
[issues-shield]: https://img.shields.io/github/issues/abk7777/serverless-streaming-reddit-pipeline.svg?style=flat-square
[issues-url]: https://github.com/abk7777/serverless-streaming-reddit-pipeline/issues
[license-shield]: https://img.shields.io/github/license/abk7777/serverless-streaming-reddit-pipeline.svg?style=flat-square
[license-url]: https://github.com/abk7777/serverless-streaming-reddit-pipeline/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/gregory-lindsey/