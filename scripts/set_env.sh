#!/usr/bin/env bash

STAGE=${1:-prod}
APP_NAME=${2:-reddit-pipeline}
REGION=${3:-us-east-1}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
STACK_NAME=$STAGE-$APP_NAME-$REGION

# Reddit API Params
CLIENT_ID=aYSpDVIL9aTSlA
CLIENT_SECRET=19fpWQf5zO_VDg6FjMb5dwvcwuU
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USERAGENT=ssrp-$ACCOUNT_ID
USERNAME=abk7x4
PASSWORD=abkg2r0e2g0

echo "This is set_env"
