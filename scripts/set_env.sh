#!/usr/bin/env bash

STAGE=dev
APP_NAME=reddit-pipeline
APP_VERSION=1
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
STACK_NAME=$STAGE-$APP_NAME-$APP_VERSION-$REGION

# Reddit API Params
CLIENT_ID=aYSpDVIL9aTSlA
CLIENT_SECRET=19fpWQf5zO_VDg6FjMb5dwvcwuU
USERAGENT=ssrp-$ACCOUNT_ID
USERNAME=abk7x4
PASSWORD=abkg2r0e2g0

SSM_KEY=$STAGE-$APP_NAME/$APP_VERSION/$REGION
