#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.code_interpreter_stack import CodeInterpreterStack
from stacks.storage_stack import StorageStack

app = cdk.App()

env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region="ap-northeast-1",
)

storage_stack = StorageStack(app, "DataAnalystStorageStack", env=env)
code_interpreter_stack = CodeInterpreterStack(
    app,
    "DataAnalystCodeInterpreterStack",
    bucket=storage_stack.bucket,
    env=env,
)

code_interpreter_stack.add_dependency(storage_stack)

app.synth()
