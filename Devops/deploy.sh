#!/bin/bash

set -e

ENVIRONMENT=$1

source ./env/$ENVIRONMENT.env.sh

# Get account ID for S3 bucket
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

S3_BUCKET="oo-co-$ENVIRONMENT-backend-artifact-bucket"

echo "Deploying stack: $STACK_NAME"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"

# Build
sam build

# Deploy
sam deploy \
  --stack-name "$STACK_NAME" \
  --s3-bucket "$S3_BUCKET" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION" \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
    Environment="$ENVIRONMENT" \
    VpcId="$VPC_ID" \
    SubnetIds="$SUBNET_IDS"


echo "Deployment complete!"