# AWS Data Engineering CI/CD - Day 2 Code Kit

This repository supports the Day 2 instructor lab for CI/CD in AWS Data Engineering.

## What the lab demonstrates

1. Store Lambda and Glue source code in GitHub.
2. Run Python unit tests automatically.
3. Use AWS CodeBuild and `buildspec.yml` to package and deploy Lambda code.
4. Upload the version-controlled Glue ETL script to the Glue job's S3 script location.
5. Run a Lambda smoke test after deployment.
6. Optionally start the Glue job and validate S3 outputs as an integration test.
7. Show GitHub Actions as an alternative automation engine.
8. Introduce Terraform with a small S3 infrastructure example.

## Recommended classroom environment

- One AWS account for the lab
- One region for the CI/CD project, recommended in the instructor guide
- Logical DEV resources for the hands-on session
- TEST and PROD explained as extensions

## Repository layout

```text
aws-de-cicd-orders/
|-- lambda_src/
|   |-- __init__.py
|   `-- lambda_function.py
|-- glue/
|   `-- orders_etl.py
|-- tests/unit/
|   `-- test_lambda_function.py
|-- sample-data/
|   `-- orders.csv
|-- events/
|   |-- valid-order.json
|   `-- invalid-order.json
|-- scripts/
|   `-- run_glue_integration.sh
|-- .github/workflows/
|   |-- ci.yml
|   `-- deploy-dev-example.yml
|-- terraform/
|   |-- main.tf
|   |-- variables.tf
|   |-- outputs.tf
|   `-- terraform.tfvars.example
|-- iam/
|   |-- glue-s3-access-policy.json
|   |-- codebuild-deploy-policy.json
|   |-- codeconnections-use-policy.json
|   `-- github-oidc-trust-policy-example.json
|-- buildspec.yml
|-- requirements-dev.txt
|-- .gitignore
`-- README.md
```

## 1. Run unit tests locally

From the repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/unit -v
```

Expected result: four tests pass.

## 2. Prepare S3

Create a globally unique bucket and create these prefixes:

```text
dev/input/orders/
dev/curated/orders/
dev/gold/order_summary/
scripts/dev/
artifacts/
```

Upload `sample-data/orders.csv` to:

```text
dev/input/orders/orders.csv
```

## 3. Prepare Lambda

Create a Python Lambda function named:

```text
de-cicd-orders-validator-dev
```

Handler:

```text
lambda_function.lambda_handler
```

The initial code can be temporary. CodeBuild will replace the function code.

## 4. Prepare Glue

Create an IAM role for Glue with AWS Glue service permissions plus access to your classroom bucket. Use `iam/glue-s3-access-policy.json` as a least-privilege training template after replacing `<BUCKET_NAME>`.

Upload `glue/orders_etl.py` once to:

```text
s3://<BUCKET_NAME>/scripts/dev/orders_etl.py
```

Create a Glue Spark job named:

```text
de-cicd-orders-etl-dev
```

Set the script location to the S3 path above and add these job parameters:

```text
--DATA_BUCKET = <BUCKET_NAME>
--ENV         = dev
```

Run the Glue job manually once and verify Parquet files appear under the curated and gold prefixes.

## 5. Push repository to GitHub

```bash
git init
git add .
git commit -m "Initial AWS data engineering CI/CD project"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

## 6. Configure CodeBuild

Create a CodeBuild project called:

```text
de-cicd-orders-dev
```

Source: GitHub through the current AWS GitHub connection mechanism available in your console.

Buildspec:

```text
buildspec.yml
```

Add environment variables:

```text
AWS_REGION=<YOUR_REGION>
ENV=dev
DATA_BUCKET=<BUCKET_NAME>
LAMBDA_FUNCTION_NAME=de-cicd-orders-validator-dev
GLUE_JOB_NAME=de-cicd-orders-etl-dev
```

Attach the permissions in `iam/codebuild-deploy-policy.json` after replacing placeholders. If your GitHub connection setup requires CodeBuild to use a specific connection ARN, also apply `iam/codeconnections-use-policy.json`.

## 7. What CodeBuild does

`buildspec.yml` performs this sequence:

```text
Install Python test dependencies
        |
        v
Run pytest
        |
        v
Package Lambda ZIP
        |
        v
Update Lambda function code
        |
        v
Upload Glue script to S3
        |
        v
Invoke Lambda smoke test
```

A failing unit test stops the build before deployment.

## 8. Best classroom demonstration

1. Get one successful green build.
2. Change `pipeline_version` in `lambda_src/lambda_function.py` from `v1` to `v2`.
3. Commit and push.
4. Watch GitHub trigger CodeBuild automatically.
5. Confirm Lambda was updated without manual upload.
6. Break the amount validation intentionally.
7. Commit and push again.
8. Watch pytest fail and show that deployment does not proceed.
9. Restore the correct code and push once more.

## 9. Optional Glue integration test

Set these shell environment variables in the build environment or terminal:

```text
GLUE_JOB_NAME=de-cicd-orders-etl-dev
DATA_BUCKET=<BUCKET_NAME>
ENV=dev
AWS_REGION=<YOUR_REGION>
```

Then run:

```bash
bash scripts/run_glue_integration.sh
```

The script starts the Glue job, waits for completion, and lists curated and gold output files.

## 10. GitHub Actions

`.github/workflows/ci.yml` runs unit tests for pull requests and pushes to `main`.

`deploy-dev-example.yml` is a teaching example for AWS deployment from GitHub Actions using OIDC. Replace placeholders before enabling it. Do not store long-lived AWS access keys in the repository.

## 11. Terraform intro

From `terraform/`:

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

When finished with the demo:

```bash
terraform destroy
```

The Terraform example intentionally creates only a simple S3 bucket so students can focus on the IaC workflow rather than a large amount of HCL.

## 12. Cleanup checklist

After the class, remove resources you no longer need:

- CodeBuild project
- GitHub/AWS connection if it was created only for training
- Lambda function
- Glue job
- Glue and CodeBuild training IAM roles/policies
- Training S3 objects and bucket
- Terraform demo bucket (prefer `terraform destroy`)

## Important teaching message

GitHub is the source of truth. Once CI/CD is established, do not casually edit Lambda or Glue code directly in the AWS console. Make the change in source control, test it, and let the pipeline deploy it.
