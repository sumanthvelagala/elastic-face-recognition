import boto3
import csv
import os 

from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ID = os.getenv("ID")
client = boto3.client('sdb',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name='us-east-1')

domain = f"{ID}-simpleDB"
try :
    client.create_domain(Domain_Name = domain)
    print("succesful")
except exception as e:
    print(e)

with open("classification_face_images_1000.csv",'r') as file:
    read = csv.reader(file)
    next(read)
    for line in read:
        file_name, person_name  = line
        try:
            client.put_attributes(
                DomainName=domain,
                ItemName=file_name,
                Attributes=[
                    {
                        'Name': 'person_name',
                        'Value': person_name,
                        'Replace': True|False
                    },
                    ]
                )
        except exception as e:
            print(e)
