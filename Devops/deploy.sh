#!/usr/bin/env bash
set -e
# Accept the environment argument
arg=$1
# Source the environment variables from the given file
source ../../../env/$arg.env.sh

required_vars=("CODESTAR_CONNECTION_ARN" "RESOURCE_TYPE_COMPUTE" "RESOURCE_PREFIX" "GITHUB_COMPUTE_REPO" "GITHUB_BRANCH" "GITHUB_OWNER" "REGION" "ENVIRONMENT" "SECRET_NAME" "PIPELINE_SECRET_NAME" "VPC_ID" "SUBNET_IDS")

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "ERROR: $var is not set. Please check your $ENV_FILE file."
    exit 1
  fi
done
echo "All required environment variables are set."

ENVIRONMENT=$arg
echo "ENVIRONMENT=$ENVIRONMENT"
echo "REGION=$REGION"
echo "RESOURCE_PREFIX=$RESOURCE_PREFIX"
echo "GITHUBBRANCH=$GITHUB_BRANCH"
echo "GITHUBOWNER=$GITHUB_OWNER"
echo "GITHUBCOMPUTEREPO=$GITHUB_COMPUTE_REPO"
echo "RESOURCETYPE3=$RESOURCE_TYPE_COMPUTE"
echo "CODESTARCONNECTIONARN=$CODESTAR_CONNECTION_ARN"
echo "SECRETNAME=$SECRET_NAME"
echo "PIPELINESECRETNAME=$PIPELINE_SECRET_NAME"

ARTIFACT_BUCKET="${RESOURCE_PREFIX}-${ENVIRONMENT}-${RESOURCE_TYPE_COMPUTE}-artifact-bucket"

echo "Checking if artifact bucket $ARTIFACT_BUCKET exists..."
BUCKET_EXISTS="false"
if aws s3api head-bucket --bucket "$ARTIFACT_BUCKET" 2>/dev/null; then
  echo "Bucket $ARTIFACT_BUCKET already exists."
  BUCKET_EXISTS="true"
else
  echo "Bucket $ARTIFACT_BUCKET does not exist. CloudFormation will create it."
fi

sam deploy \
  -t pipeline.yaml \
  --stack-name "${RESOURCE_PREFIX}-${ENVIRONMENT}-${RESOURCE_TYPE_COMPUTE}-pipeline-stack" \
  --region "${REGION}" \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --tags Environment="${ENVIRONMENT}" Project="${RESOURCE_PREFIX}" ResourceType="${RESOURCE_TYPE_COMPUTE}" \
  --parameter-overrides \
      Environment="${ENVIRONMENT}" \
      ResourcePrefix="${RESOURCE_PREFIX}" \
      Region="${REGION}" \
      GitHubBranch="${GITHUB_BRANCH}" \
      GitHubOwner="${GITHUB_OWNER}" \
      GitHubRepository="${GITHUB_COMPUTE_REPO}" \
      CodeStarConnectionArn="${CODESTAR_CONNECTION_ARN}" \
      ResourceType="${RESOURCE_TYPE_COMPUTE}" \
      SecretName="${SECRET_NAME}" \
      MaxRetryAttempts="$MAX_RETRY_ATTEMPTS" \
      TimeoutDurationSeconds="$TIMEOUT_DURIATION" \
      BidPercentage="$BID_PERCENTAGE" \
      MinvCpus="$MIN_VCPUS" \
      MaxvCpus="$MAX_VCPUS" \
      DesiredvCpus="$DESIRED_VCPUS" \
      JobVcpus="$JOB_VCPUS" \
      JobMemory="$JOB_MEMORY" \
      VpcId="$VPC_ID" \
      SubnetIds="$SUBNET_IDS" \
      CreateBucket=$([[ $BUCKET_EXISTS == "false" ]] && echo "true" || echo "false") \
  --no-fail-on-empty-changeset