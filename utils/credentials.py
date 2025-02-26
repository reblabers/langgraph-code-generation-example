import boto3

class Credentials:
    def __init__(self, credentials:dict):
        self.credentials = credentials

    @property
    def access_key_id(self):
        return self.credentials['AccessKeyId']

    @property
    def secret_access_key(self):
        return self.credentials['SecretAccessKey']

    @property
    def session_token(self):
        return self.credentials['SessionToken']


def get_default_credentials() -> Credentials:
    from .env import get_env
    env = get_env()
    return get_credentials(env.aws_account_id, env.system_admin_role)


def get_credentials(aws_account_id:str, system_admin_role:str) -> Credentials:
    # Get temporary credentials
    # session = boto3.Session(profile_name=system_admin_role)
    session = boto3.Session()
    sts_client = session.client("sts")
    assumed_role_object = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{aws_account_id}:role/power_role",
        RoleSessionName="LANGCHAIN-POWER-ROLE"
    )
    credentials = assumed_role_object['Credentials']
    return Credentials(credentials)
