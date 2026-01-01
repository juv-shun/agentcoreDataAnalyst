"""S3 バケットスタック.

データ分析エージェント用の S3 バケットを作成する。
"""

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class StorageStack(Stack):
    """S3 バケットを作成するスタック.

    Attributes:
        bucket: 作成された S3 バケット

    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        """StorageStack を初期化する.

        Args:
            scope: CDK スコープ
            construct_id: スタック ID
            **kwargs: Stack の追加引数

        """
        super().__init__(scope, construct_id, **kwargs)

        # S3 バケット作成
        self.bucket = s3.Bucket(
            self,
            "DataAnalystBucket",
            bucket_name="juv-shun.data-analyst-agent-trial",
            removal_policy=RemovalPolicy.DESTROY,  # 検証用なので削除可能
            auto_delete_objects=True,  # バケット削除時にオブジェクトも削除
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # 出力
        CfnOutput(
            self,
            "BucketName",
            value=self.bucket.bucket_name,
            description="S3 bucket name for data analyst agent",
        )
        CfnOutput(
            self,
            "BucketArn",
            value=self.bucket.bucket_arn,
            description="S3 bucket ARN for data analyst agent",
        )
