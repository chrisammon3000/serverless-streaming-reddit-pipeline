#!/usr/bin/env bash

# # Stack params
# STAGE=${1:-prod}
# APP_NAME=${2:-reddit-pipeline}
# APP_VERSION=${3:-1}
# REGION=${4:-us-east-1}
# SSM_KEY=$STAGE-$APP_NAME/$APP_VERSION/$REGION

aws ssm delete-parameter --name /$SSM_KEY/praw_cid

aws ssm delete-parameter --name /$SSM_KEY/praw_secret

aws ssm delete-parameter --name /$SSM_KEY/praw_useragent

aws ssm delete-parameter --name /$SSM_KEY/praw_username

aws ssm delete-parameter --name /$SSM_KEY/praw_password

exit 0