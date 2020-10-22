#!/usr/bin/env bash

STAGE=dev
APP_NAME=reddit-pipeline
APP_VERSION=2
REGION=us-east-1
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
STACK_NAME=$STAGE-$APP_NAME-$APP_VERSION-$REGION

# Reddit API Params
CLIENT_ID=hYOoZaQK3ZsJqw
CLIENT_SECRET=WenXYVT8isAzRDxddc8_e_B38Tc
USERAGENT=ssrp
USERNAME=abk7x4
PASSWORD=abkg2r0e2g0

SSM_KEY=$STAGE-$APP_NAME/$APP_VERSION/$REGION
