#!/usr/bin/env python3
import subprocess

import aws_cdk as cdk
from aws_cdk import App

from cdk import config, stack

deployment = config.Deployment(_env_file=".env")

app = App()

git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
try:
    git_tag = subprocess.check_output(["git", "describe", "--tags"]).decode().strip()
except subprocess.CalledProcessError:
    git_tag = "no-tag"

tags = {
    "Project": "ghgc",
    "Owner": deployment.owner,
    "Client": "nasa-impact",
    "Stack": deployment.stage,
    "GitCommit": git_sha,
    "GitTag": git_tag,
}

ingestor_api = stack.StacIngestionApi(
    app,
    construct_id=deployment.stack_name,
    config=deployment,
    tags={
        "Project": "ghgc",
        "Owner": deployment.owner,
        "Client": "nasa-impact",
        "Stack": deployment.stage,
    },
    env=deployment.env,
)

if deployment.cf_distribution_arn:
    stack.CloudfrontUpdate(
        app,
        construct_id=deployment.stack_name,
        api_url=ingestor_api.ingestor_api.url,
        config=deployment,
    )

for key, value in tags.items():
    cdk.Tags.of(app).add(key, value)

app.synth()
