from langchain_aws import ChatBedrockConverse
from .credentials import Credentials

CLAUDE_3_HAIKU = "us.anthropic.claude-3-haiku-20240307-v1:0"
CLAUDE_3_5_SONNET = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
CLAUDE_3_7_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

def get_bedrock_llm(
        credentials:Credentials,
        # model_id:str = CLAUDE_3_HAIKU,
        # model_id:str = CLAUDE_3_5_SONNET,
        model_id:str = CLAUDE_3_7_SONNET,
        region_name:str="us-east-1",
):
    return ChatBedrockConverse(
        model_id=model_id,
        aws_access_key_id=credentials.access_key_id,
        aws_secret_access_key=credentials.secret_access_key,
        aws_session_token=credentials.session_token,
        region_name=region_name,
        temperature=0.0,
    )
