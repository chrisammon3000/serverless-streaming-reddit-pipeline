#!/usr/bin/env bash

export STAGE=${1:-prod}
export APP_NAME=${2:-reddit-pipeline}
export REGION=${3:-us-east-1}
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export STACK_NAME=$STAGE-$APP_NAME-$REGION

S3_KEY="/$APP_NAME/$STAGE/"

# Not used
CONFIG_PATH=config/load-subreddits.json

UPDATE_SSM=false
CFN_MASTER_PATH="cfn/master-stack.yml"
CFN_S3_PATH="cfn/s3-cfn.yml"
CFN_DIR=(${CFN_MASTER_PATH//\// })

# Prompt if SSM parameters need to be updated. Only necessary for the first deployment unless they change.
echo
echo "SSM Parameters must be set before the first deployment."
read -p "Update SSM parameters? " -n 1 -r
printf '\n\n'

if [[ $REPLY =~ ^[Yy]$ ]]
then
    UPDATE_SSM=true
else
    UPDATE_SSM=false
fi

# read -p "Deploy Serverless Framework? " -n 1 -r


# Confirmation of parameters
echo -e "\e[38;5;0;48;5;255m####### Confirm CloudFormation parameters: #######\e[0m"
echo "Stage: $STAGE"
echo "App name: $APP_NAME"
echo "AWS Region: $REGION"
echo "Stack name: $STACK_NAME"
echo

# Update ssm params if indicated
bash $(dirname "$0")/set_parameters.sh $STAGE $APP_NAME $REGION $UPDATE_SSM
if [[ $? != 0 ]]; then exit $?; fi

echo -e "\e[38;5;0;48;5;255m******* Deploying CloudFormation templates bucket... *******\e[0m"
aws --region $REGION cloudformation deploy \
--template-file $CFN_S3_PATH \
--stack-name $STACK_NAME-s3

S3_CFN_BUCKET=$(aws cloudformation describe-stacks \
--stack-name $STACK_NAME-s3 \
--query "Stacks[0].Outputs[?OutputKey=='CFNBucketName'].OutputValue" \
--output text)
echo

echo -e "\e[38;5;0;48;5;255m******* Syncing template files... *******\e[0m"
echo
aws s3 cp ./$CFN_DIR s3://$S3_CFN_BUCKET$S3_KEY \
--recursive
echo
echo -e "\e[38;5;0;48;5;255m******* Deploying CloudFormation stack... *******\e[0m"
echo
echo "Stack name: $STACK_NAME"
echo "CFN templates bucket: $S3_CFN_BUCKET"

aws --region $REGION cloudformation deploy \
--template-file $CFN_MASTER_PATH \
--stack-name $STACK_NAME \
--parameter-overrides CFNBucketName=$S3_CFN_BUCKET \
--capabilities CAPABILITY_NAMED_IAM

# Sync config files
echo -e "\e[38;5;0;48;5;255m******* Syncing config files... *******\e[0m"
S3_CONFIG_BUCKET=$(aws cloudformation describe-stacks \
--stack-name $STACK_NAME \
--query "Stacks[0].Outputs[?OutputKey=='ConfigBucketName'].OutputValue" \
--output text)

aws s3 cp ./$CONFIG_PATH s3://$S3_CONFIG_BUCKET/$CONFIG_PATH

exit 0