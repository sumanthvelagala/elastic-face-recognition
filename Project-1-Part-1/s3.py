import boto3
import os   
from dotenv import load_dotenv


load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ID = os.getenv("ID")
client = boto3.client('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

try :
    client.create_bucket(Bucket=f"{ID}-in-bucket")
    print("successfull")
except Exception as e:
    print(e)































