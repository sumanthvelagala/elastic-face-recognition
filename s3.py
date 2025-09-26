import boto3
import os   
from dotenv import load_dotenv


load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET = os.getenv("BUCKET")
client = boto3.client('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

try :
    client.create_bucket(Bucket=BUCKET)
    print("successfull")
except Exception as e:
    print(e)































