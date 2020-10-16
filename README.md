

serverless-streaming-reddit-pipeline
==============================

Uses scheduled Lambdas, SQS and Kinesis Firehose to stream JSON data of new posts from any number of Reddit forums to an S3 data lake. A Glue Crawler determines the schema and makes the data available for query through Athena or for analytics with Quicksight. Can be run at any interval and scale for collecting data.

This service employs a fan-out architecture where a cron scheduled Lambda function retrieves a list of subreddits (`config/load-subreddits.json`) from an S3 bucket, sends them to an SQS queue which triggers Lambda workers to process data collection from each subreddit in parallel. The worker then streams the data to a Kinesis Firehose stream into an S3 data lake. Allows for monitoring and collecting real-time data at scale without the hassle of provisioning servers.

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

3. Input Reddit API credentials in `scripts/set_parameters.sh`:
   ```
   # Reddit API Params
   CLIENT_ID= #CLIENT_ID
   CLIENT_SECRET= #CLIENT_SECRET
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   USERAGENT=ssrp-$ACCOUNT_ID
   USERNAME= #USERNAME
   PASSWORD= #PASSWORD
   ```

### Deploy AWS Infrastructure
These instructions will deploy a stack named `prod-reddit-pipeline-us-east-1` using AWS CloudFormation.

   Run `scripts/deploy.sh` to deploy the stack:
   ```
   cd serverless-streaming-reddit-pipeline
   bash scripts/deploy.sh
   ```

### Deploy Serverless Framework
   ```
   cd src/functions/pipeline &&
   serverless deploy
   ```

### Invoke Lambda
   ```
   cd src/functions/pipeline
   serverless invoke --function queueSubreddits \
   --stage dev \
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