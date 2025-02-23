import os
from dotenv import load_dotenv

load_dotenv('.env')

def get_env() -> 'Env':
    return Env()

class Env:
    @property
    def aws_account_id(self):
        return os.environ['AWS_ACCOUNT_ID']
    
    @property
    def system_admin_role(self):
        return os.environ['SYSTEM_ADMIN_ROLE']
