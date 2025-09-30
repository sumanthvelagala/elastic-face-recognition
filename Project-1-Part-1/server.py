import boto3
from fastapi import FastAPI,UploadFile
from fastapi.responses import PlainTextResponse
 
s3_client = boto3.client('s3',region_name="us-east-1")
sdb_client = boto3.client('sdb',region_name="us-east-1")
app = FastAPI()

def send_to_s3(image, image_name):
    try:
        s3_client.upload_fileobj(image,"1235578190-in-bucket",image_name)
        return True
    except Exception as e:
        print(e)
        return False

def get_person_name(image_name):
    try:
        response = sdb_client.get_attributes(DomainName="1235578190-simpleDB",ItemName=image_name,AttributeNames=["person_name"])
        return response["Attributes"][0]["Value"]

    except Exception as e:
        print(e)
        return None

@app.post("/", response_class=PlainTextResponse)
def request_data(inputFile: UploadFile):
    file_name = inputFile.filename
    file_name_no_ext = file_name.split('.')[0]
    if not file_name:
        return "No file selected"
    inputFile.file.seek(0)
    if not send_to_s3(inputFile.file,file_name):
        return "Couldn't upload file to s3"
    result = get_person_name(file_name_no_ext)

    if result is None:
        return "No match found"
    return f"{file_name_no_ext}:{result}"


    

