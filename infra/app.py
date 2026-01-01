#!/usr/bin/env python3
import os

import aws_cdk as cdk
from stacks.agentcore_runtime_role_stack import AgentCoreRuntimeRoleStack
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

agentcore_runtime_role_stack = AgentCoreRuntimeRoleStack(
    app,
    "DataAnalystRuntimeRoleStack",
    code_interpreter_arn=code_interpreter_stack.code_interpreter.attr_code_interpreter_arn,
    env=env,
)
agentcore_runtime_role_stack.add_dependency(code_interpreter_stack)

app.synth()
