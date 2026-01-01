"""Code Interpreter スタック.

S3 アクセス可能な Code Interpreter を作成する。
IAM ロールも含めて管理する。
"""

from typing import TYPE_CHECKING, Any

from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_bedrockagentcore as bedrockagentcore
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3

if TYPE_CHECKING:
    from constructs import Construct


class CodeInterpreterStack(Stack):
    """Code Interpreter を作成するスタック.

    Attributes:
        code_interpreter_role: Code Interpreter 用 IAM ロール
        code_interpreter: Code Interpreter リソース
        code_interpreter_id: Code Interpreter の ID

    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.IBucket,
        **kwargs: Any,
    ) -> None:
        """CodeInterpreterStack を初期化する.

        Args:
            scope: CDK スコープ
            construct_id: スタック ID
            bucket: S3 バケット(読み取り権限を付与する対象)
            **kwargs: Stack の追加引数

        """
        super().__init__(scope, construct_id, **kwargs)

        # Code Interpreter 用 IAM ロール
        self.code_interpreter_role = iam.Role(
            self,
            "CodeInterpreterRole",
            role_name="CodeInterpreterS3AccessRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            description="IAM role for Code Interpreter to access S3",
        )

        # S3 読み取り権限を付与
        bucket.grant_read(self.code_interpreter_role)

        # Code Interpreter 作成
        self.code_interpreter = bedrockagentcore.CfnCodeInterpreterCustom(
            self,
            "CodeInterpreter",
            name="DataAnalystS3CodeInterpreter",
            description="Code Interpreter with S3 access for data analysis",
            execution_role_arn=self.code_interpreter_role.role_arn,
            network_configuration=bedrockagentcore.CfnCodeInterpreterCustom.CodeInterpreterNetworkConfigurationProperty(
                network_mode="PUBLIC",  # SANDBOXでいいはずだが、現在なぜだか失敗するためPUBLICに
            ),
        )

        # Code Interpreter ID を出力
        self.code_interpreter_id = self.code_interpreter.attr_code_interpreter_id

        # IAM ロールの出力
        CfnOutput(
            self,
            "RoleArn",
            value=self.code_interpreter_role.role_arn,
            description="IAM role ARN for Code Interpreter",
        )
        CfnOutput(
            self,
            "RoleName",
            value=self.code_interpreter_role.role_name,
            description="IAM role name for Code Interpreter",
        )

        # Code Interpreter の出力
        CfnOutput(
            self,
            "CodeInterpreterArn",
            value=self.code_interpreter.attr_code_interpreter_arn,
            description="Code Interpreter ARN",
        )
        CfnOutput(
            self,
            "CodeInterpreterId",
            value=self.code_interpreter_id,
            description="Code Interpreter ID",
        )
