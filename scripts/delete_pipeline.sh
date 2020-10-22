#!/usr/bin/env bash

source $(dirname "$0")/set_env.sh
read -p "This will delete all resources and data. Continue? " -n 1 -r
echo && echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting"
    [[ "$0" = "$BASH_SOURCE" ]] && exit 0 || return 0
fi

echo -e "\e[38;5;0;48;5;255m******* Deleting Serverless resources... *******\e[0m"
# Delete serverless resources
cd src/functions/pipeline && \
serverless remove

echo -e "\e[38;5;0;48;5;255m******* Deleting S3 buckets and objects... *******\e[0m"
# Get and delete objects on cfn bucket
S3_CFN_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME-s3 \
    --query "Stacks[0].Outputs[?OutputKey=='CFNBucketName'].OutputValue" \
    --output text)
aws s3 rm --recursive s3://$S3_CFN_BUCKET
echo "Deleted S3 bucket: $S3_CFN_BUCKET"

# Get and delete objects on data bucket
S3_DATA_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='DataBucketName'].OutputValue" \
    --output text)
aws s3 rm --recursive s3://$S3_DATA_BUCKET
echo "Deleted S3 bucket: $S3_DATA_BUCKET"

# Get and delete objects on config bucket
S3_CONFIG_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='ConfigBucketName'].OutputValue" \
    --output text)
aws s3 rm --recursive s3://$S3_CONFIG_BUCKET
echo "Deleted S3 bucket: $S3_CONFIG_BUCKET"

# Get and delete objects on scripts bucket
S3_SCRIPTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query "Stacks[0].Outputs[?OutputKey=='GlueScriptsBucketName'].OutputValue" \
    --output text)
aws s3 rm --recursive s3://$S3_SCRIPTS_BUCKET
echo "Deleted S3 bucket: $S3_SCRIPTS_BUCKET"

# Delete stacks
echo -e "\e[38;5;0;48;5;255m******* Deleting CloudFormation stacks... *******\e[0m"

# Delete CloudFormation nested stack
aws cloudformation delete-stack \
--stack-name $STACK_NAME
echo "Deleted stack: $STACK_NAME"

# Delete S3 stack
aws cloudformation delete-stack \
--stack-name $STACK_NAME-s3
echo "Deleted stack: $STACK_NAME-s3"

# Delete SSM Parameters
echo -e "\e[38;5;0;48;5;255m******* Deleting SSM Parameters... *******\e[0m"
aws ssm delete-parameter --name /$SSM_KEY/praw_cid
aws ssm delete-parameter --name /$SSM_KEY/praw_secret
aws ssm delete-parameter --name /$SSM_KEY/praw_useragent
aws ssm delete-parameter --name /$SSM_KEY/praw_username
aws ssm delete-parameter --name /$SSM_KEY/praw_password

echo "Finished"

exit 0