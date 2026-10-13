#!/usr/bin/env bash
set -euo pipefail

: "${GLUE_JOB_NAME:?Set GLUE_JOB_NAME}"
: "${DATA_BUCKET:?Set DATA_BUCKET}"
: "${ENV:?Set ENV}"
: "${AWS_REGION:?Set AWS_REGION}"

echo "Starting Glue integration test"

JOB_RUN_ID=$(aws glue start-job-run \
  --job-name "$GLUE_JOB_NAME" \
  --arguments "--DATA_BUCKET=$DATA_BUCKET,--ENV=$ENV" \
  --region "$AWS_REGION" \
  --query JobRunId \
  --output text)

echo "Glue Job Run ID: $JOB_RUN_ID"

while true; do
  STATUS=$(aws glue get-job-run \
    --job-name "$GLUE_JOB_NAME" \
    --run-id "$JOB_RUN_ID" \
    --region "$AWS_REGION" \
    --query "JobRun.JobRunState" \
    --output text)

  echo "Glue Status: $STATUS"

  case "$STATUS" in
    SUCCEEDED)
      echo "Glue integration test passed"
      break
      ;;
    FAILED|ERROR|TIMEOUT|STOPPED)
      echo "Glue integration test failed with status: $STATUS"
      exit 1
      ;;
    *)
      sleep 30
      ;;
  esac
done

echo "Checking curated output"
aws s3 ls "s3://$DATA_BUCKET/$ENV/curated/orders/" --recursive --region "$AWS_REGION"

echo "Checking gold output"
aws s3 ls "s3://$DATA_BUCKET/$ENV/gold/order_summary/" --recursive --region "$AWS_REGION"

echo "Integration test completed"
