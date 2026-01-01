from strands.models import BedrockModel

# Uses global inference profile for Claude Sonnet 4.5
# https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html
MODEL_ID = "jp.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = "ap-northeast-1"

def load_model() -> BedrockModel:
    """
    Get Bedrock model client.
    Uses IAM authentication via the execution role.
    """
    return BedrockModel(model_id=MODEL_ID, region_name=REGION)