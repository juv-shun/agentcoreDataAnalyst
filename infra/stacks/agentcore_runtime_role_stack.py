"""AgentCore Runtime Role スタック.

AgentCore Runtime 用の IAM ロールを作成する。
"""

from typing import TYPE_CHECKING, Any

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_iam as iam

if TYPE_CHECKING:
    from constructs import Construct


class AgentCoreRuntimeRoleStack(Stack):
    """AgentCore Runtime 用 IAM ロールを作成するスタック.

    Attributes:
        runtime_role: AgentCore Runtime 用 IAM ロール

    """

    def __init__(
        self,
        scope: "Construct",
        construct_id: str,
        code_interpreter_arn: str,
        **kwargs: Any,
    ) -> None:
        """AgentCoreRuntimeRoleStack を初期化する.

        Args:
            scope: CDK スコープ
            construct_id: スタック ID
            code_interpreter_arn: Code Interpreter の ARN
            **kwargs: Stack の追加引数

        """
        super().__init__(scope, construct_id, **kwargs)

        # 信頼ポリシー（Condition付き）
        self.runtime_role = iam.Role(
            self,
            "AgentCoreRuntimeRole",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:*",
                    },
                },
            ),
            description="IAM role for AgentCore Runtime execution",
        )

        # CloudWatch Logs 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:DescribeLogStreams", "logs:CreateLogGroup"],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/bedrock-agentcore/runtimes/*",
                ],
            ),
        )
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:DescribeLogGroups"],
                resources=[f"arn:aws:logs:{self.region}:{self.account}:log-group:*"],
            ),
        )
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[
                    f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*",
                ],
            ),
        )
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:PutDeliverySource",
                    "logs:PutDeliveryDestination",
                    "logs:CreateDelivery",
                    "logs:GetDeliverySource",
                    "logs:DeleteDeliverySource",
                    "logs:DeleteDeliveryDestination",
                ],
                resources=["*"],
            ),
        )

        # X-Ray 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets",
                ],
                resources=["*"],
            ),
        )

        # CloudWatch Metrics 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["cloudwatch:PutMetricData"],
                resources=["*"],
                conditions={"StringEquals": {"cloudwatch:namespace": "bedrock-agentcore"}},
            ),
        )

        # Bedrock AgentCore Identity 権限 - GetResourceApiKey
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentCoreIdentityGetResourceApiKey",
                effect=iam.Effect.ALLOW,
                actions=["bedrock-agentcore:GetResourceApiKey"],
                resources=[
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:token-vault/default",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:token-vault/default/apikeycredentialprovider/*",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default/workload-identity/*",
                ],
            ),
        )

        # Secrets Manager 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentCoreIdentityGetCredentialProviderClientSecret",
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:bedrock-agentcore-identity!default/oauth2/*",
                    f"arn:aws:secretsmanager:{self.region}:{self.account}:secret:bedrock-agentcore-identity!default/apikey/*",
                ],
            ),
        )

        # Bedrock AgentCore Identity 権限 - GetResourceOauth2Token
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentCoreIdentityGetResourceOauth2Token",
                effect=iam.Effect.ALLOW,
                actions=["bedrock-agentcore:GetResourceOauth2Token"],
                resources=[
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:token-vault/default",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:token-vault/default/oauth2credentialprovider/*",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default/workload-identity/*",
                ],
            ),
        )

        # Bedrock Model 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockModelInvocation",
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:ApplyGuardrail",
                ],
                resources=[
                    "arn:aws:bedrock:*::foundation-model/*",
                    "arn:aws:bedrock:*:*:inference-profile/*",
                    f"arn:aws:bedrock:{self.region}:{self.account}:*",
                ],
            ),
        )

        # Marketplace 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="MarketplaceSubscribeOnFirstCall",
                effect=iam.Effect.ALLOW,
                actions=["aws-marketplace:ViewSubscriptions", "aws-marketplace:Subscribe"],
                resources=["*"],
                conditions={"StringEquals": {"aws:CalledViaLast": "bedrock.amazonaws.com"}},
            ),
        )

        # Code Interpreter 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentCoreCodeInterpreter",
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock-agentcore:StartCodeInterpreterSession",
                    "bedrock-agentcore:InvokeCodeInterpreter",
                    "bedrock-agentcore:StopCodeInterpreterSession",
                    "bedrock-agentcore:GetCodeInterpreter",
                    "bedrock-agentcore:GetCodeInterpreterSession",
                    "bedrock-agentcore:ListCodeInterpreterSessions",
                ],
                resources=[
                    f"arn:aws:bedrock-agentcore:{self.region}:aws:code-interpreter/aws.codeinterpreter.v1",
                    code_interpreter_arn,
                ],
            ),
        )

        # Bedrock AgentCore Identity 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentCoreIdentity",
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock-agentcore:CreateWorkloadIdentity",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                resources=[
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:workload-identity-directory/default/workload-identity/*",
                ],
            ),
        )

        # STS 権限
        self.runtime_role.add_to_policy(
            iam.PolicyStatement(
                sid="AwsJwtFederation",
                effect=iam.Effect.ALLOW,
                actions=["sts:GetWebIdentityToken"],
                resources=["*"],
            ),
        )

        # 出力: agentcore deploy で使用
        CfnOutput(
            self,
            "AgentCoreRuntimeRoleArn",
            value=self.runtime_role.role_arn,
            description="AgentCore Runtime Role ARN",
        )
