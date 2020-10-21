#!/usr/bin/env bash

UPDATE_SSM=${1:-true}

source $(dirname "$0")/set_env.sh

echo -e "\e[38;5;0;48;5;255m####### Confirm SSM parameters: #######\e[0m"
echo "Client ID: $CLIENT_ID"
echo "Client secret: $CLIENT_SECRET"
echo "Useragent: $USERAGENT"
echo "Username: $USERNAME"
echo "Password: $PASSWORD"
printf "SSM key: $SSM_KEY\n\n"

read -p "Continue? " -n 1 -r
echo && echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting"
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

if [[ ! $UPDATE_SSM = true ]]
then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 0 || return 0
fi

echo
echo -e "\e[38;5;0;48;5;255m******* Updating SSM parameters... *******\e[0m"
echo

aws ssm put-parameter \
  --name /$SSM_KEY/praw_cid \
  --type SecureString \
  --value $CLIENT_ID \
  --description "PRAW Client Id" \
  --overwrite >/dev/null 2>&1

aws ssm put-parameter \
  --name /$SSM_KEY/praw_secret \
  --type SecureString \
  --value $CLIENT_SECRET \
  --description "PRAW Client Secret" \
  --overwrite >/dev/null 2>&1

aws ssm put-parameter \
  --name /$SSM_KEY/praw_useragent \
  --type String \
  --value $USERAGENT \
  --description "PRAW Useragent" \
  --overwrite >/dev/null 2>&1

aws ssm put-parameter \
  --name /$SSM_KEY/praw_username \
  --type SecureString \
  --value $USERNAME \
  --description "PRAW Username" \
  --overwrite >/dev/null 2>&1

aws ssm put-parameter \
  --name /$SSM_KEY/praw_password \
  --type SecureString \
  --value $PASSWORD \
  --description "PRAW password" \
  --overwrite >/dev/null 2>&1

# Get parameters from Parameter Store
aws ssm get-parameter \
  --name /$SSM_KEY/praw_cid \
  #--query Parameter.Value

aws ssm get-parameter \
  --name /$SSM_KEY/praw_secret \
  #--query Parameter.Value

aws ssm get-parameter \
  --with-decryption \
  --name /$SSM_KEY/praw_password \
  #--query Parameter.Value

aws ssm get-parameter \
  --name /$SSM_KEY/praw_useragent \
  #--query Parameter.Value

aws ssm get-parameter \
  --with-decryption \
  --name /$SSM_KEY/praw_username \
  #--query Parameter.Value

exit 0