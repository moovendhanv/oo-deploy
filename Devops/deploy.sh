#!/bin/bash

set -e

ENVIRONMENT=$1

get_stack_output_value() {
    local stack_name=$1
    local output_key=$2
    local region=$AWS_REGION

    local output_value=$(aws cloudformation describe-stacks \
        --stack-name "$stack_name" \
        --region "$region" \
        --query "Stacks[0].Outputs[?OutputKey=='${output_key}'].OutputValue" \
        --output text 2>/dev/null)

    if [[ -z "$output_value" || "$output_value" == "None" ]]; then
        echo "Output key '$output_key' not found in stack '$stack_name'"
        return 1
    fi

    echo "$output_value"
    return 0
}

export VPC_ID=$(get_stack_output_value "${RESOURCE_PREFIX}-${ENVIRONMENT}-backend-network-stack" "VPCId")
export SUBNET_IDS=$(get_stack_output_value "${RESOURCE_PREFIX}-${ENVIRONMENT}-backend-network-stack" "PrivateSubnet1Id")
export SUBNET_IDS+=" "$(get_stack_output_value "${RESOURCE_PREFIX}-${ENVIRONMENT}-backend-network-stack" "PrivateSubnet2Id")
export WEBSOCKET_URL=$(get_stack_output_value "${RESOURCE_PREFIX}-${ENVIRONMENT}-websocket" "LoadBalancerURL")
export REDIS_ENDPOINT=$(get_stack_output_value "oo-redis-${ENVIRONMENT}-resources" "RedisConnectionString")

# Get account ID for S3 bucket
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

S3_BUCKET="${RESOURCE_PREFIX}-${ENVIRONMENT}-backend-artifact-bucket"

STACK_NAME="${RESOURCE_PREFIX}-${ENVIRONMENT}-${RESOURCE_TYPE}-stack"

# Build
sam build

# Deploy
sam deploy \
  --stack-name "$STACK_NAME" \
  --s3-bucket "$S3_BUCKET" \
  --capabilities CAPABILITY_IAM \
  --region "$AWS_REGION" \
  --parameter-overrides \
    Environment="$ENVIRONMENT" \
    VpcId="$VPC_ID" \
    SubnetIds="$SUBNET_IDS" \
    ResourcePrefix="$RESOURCE_PREFIX" \
    ResourceType="$RESOURCE_TYPE" \
    RedisEndpoint="$REDIS_ENDPOINT" \
    MaxRetryAttempts="$MAX_RETRY_ATTEMPTS" \
    TimeoutDurationSeconds="$TIMEOUT_DURIATION" \
    BidPercentage="$BID_PERCENTAGE" \
    MinvCpus="$MIN_VCPUS" \
    MaxvCpus="$MAX_VCPUS" \
    DesiredvCpus="$DESIRED_VCPUS" \
    JobVcpus="$JOB_VCPUS" \
    JobMemory="$JOB_MEMORY"


echo "Deployment complete!"