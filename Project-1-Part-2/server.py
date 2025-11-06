from fastapi import FastAPI, UploadFile
import boto3
from fastapi.responses import PlainTextResponse
import uuid
import time
import threading

sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

request_url = sqs.get_queue_url(QueueName='1235578190-req-queue')['QueueUrl']
response_url = sqs.get_queue_url(QueueName='1235578190-resp-queue')['QueueUrl']

app = FastAPI()

responses_store = {}
lock = threading.Lock()

# get detected face result from the response queue using background thread
def pull_response_thread():
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=response_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10,
                MessageAttributeNames=['All']
            )

            if 'Messages' in response:
                for message in response['Messages']:
                    attributes = message.get('MessageAttributes', {})
                    request_id = attributes.get('request_id', {}).get('StringValue')
                    result = message['Body']
                    
                    if request_id:
                        # lock while writing to dictionary
                        with lock:
                            responses_store[request_id] = result
                        
                        # delete the processed message
                        sqs.delete_message(
                            QueueUrl=response_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
        except Exception as e:
            print(e)
            time.sleep(3)

# start the thread
response_thread = threading.Thread(target=pull_response_thread, daemon=True)
response_thread.start()

# push post request to the request_queue
def send_to_sqs(image_name):
    request_id = str(uuid.uuid4())
    
    sqs.send_message(
        QueueUrl=request_url,
        MessageBody=image_name,
        MessageAttributes={
            'request_id': {'StringValue': request_id, 'DataType': 'String'},
            'image_name': {'StringValue': image_name, 'DataType': 'String'}
        }
    )
    return request_id

# store the image in s3
def send_to_s3(image_file, image_name):
    s3.upload_fileobj(image_file, "1235578190-in-bucket", image_name)

# get prediction result from request store
def get_response(request_id):
    while True:
        with lock:
            if request_id in responses_store:
                # delete the processed result
                result = responses_store.pop(request_id)
                return result
  

# push the request to app tier through request queue and get result through response queue
@app.post("/", response_class=PlainTextResponse)
def request_data(inputFile: UploadFile):
    try:
        file_name = inputFile.filename
        inputFile.file.seek(0)

        send_to_s3(inputFile.file, file_name)
        
        request_id = send_to_sqs(file_name)
        prediction = get_response(request_id)
        
        # remove extension
        no_ext_file_name = file_name.split(".")[0]
        return f"{no_ext_file_name}:{prediction}"
        
    except Exception as e:
        print(f"Request error: {e}")
        raise