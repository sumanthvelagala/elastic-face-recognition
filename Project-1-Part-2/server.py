from fastapi import FastAPI, UploadFile
import aioboto3
from fastapi.responses import PlainTextResponse
import asyncio

session = aioboto3.Session(region_name="us-east-1")
app = FastAPI()

# get queue url's on startup
@app.on_event("startup")
async def get_url():
    global request_url, response_url
    async with session.client("sqs") as sqs:
                request = await sqs.get_queue_url(
                    QueueName='1235578190-req-queue')
                request_url=request['QueueUrl']

                response = await sqs.get_queue_url(
                    QueueName='1235578190-resp-queue')
                response_url=response['QueueUrl']

# push post request to the request_queue
async def send_to_sqs(message): 
    async with session.client("sqs") as sqs: 
        await sqs.send_message(QueueUrl=request_url,MessageBody=message)

# store the image in s3
async def send_to_s3(image, image_name):
    async with session.client("s3") as s3: 
        await s3.upload_fileobj(image,"1235578190-in-bucket",image_name)
    
# get detected face result from the response queue
async def get_from_sqs(file_name):
    async with session.client("sqs") as sqs:
        while True:
            response = await sqs.receive_message(
                QueueUrl=response_url,
                MaxNumberOfMessages=1
                )
            if "Messages" not in response:
                await asyncio.sleep(1)
                continue
            message = response["Messages"][0]
            result = message["Body"]
            name_with_no_ext = file_name.split(".")[0]
            if result.startswith(name_with_no_ext):
                await sqs.delete_message(QueueUrl=response_url,ReceiptHandle=message["ReceiptHandle"])
                return result

# push the request to app tier through request queue and get result through response queue
@app.post("/",response_class=PlainTextResponse)
async def request_data(inputFile:UploadFile, response_class=PlainTextResponse):
    try:
        file_name = inputFile.filename
        inputFile.file.seek(0)
        await send_to_s3(inputFile.file,file_name)
        await send_to_sqs(inputFile.filename)
        result = await get_from_sqs(file_name)
        return result
    except Exception as e:
        print(e)
        raise