#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.codepipeline import CodepipelineStack


app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)

CodepipelineStack(app, "AwscdkCodepipelineStack", env=env)

app.synth()
