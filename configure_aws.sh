#!/bin/bash

mkdir -p ~/.aws

cat > ~/.aws/credentials <<- EOM
[default]
aws_access_key_id = $BUCKETEER_AWS_ACCESS_KEY_ID
aws_secret_access_key = $BUCKETEER_AWS_SECRET_ACCESS_KEY
EOM

cat > ~/.aws/config <<- EOM
[default]
region = $BUCKETEER_AWS_REGION
EOM
