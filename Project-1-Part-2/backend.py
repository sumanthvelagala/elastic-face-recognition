import boto3
from io import BytesIO
from face_recognition import face_match
import time

sqs = boto3.client('sqs', region_name="us-east-1")
s3 = boto3.client('s3', region_name="us-east-1")

request_url = sqs.get_queue_url(QueueName='1235578190-req-queue')['QueueUrl']
response_url = sqs.get_queue_url(QueueName='1235578190-resp-queue')['QueueUrl']

while True:
    try:
        # get request from request queue
        response = sqs.receive_message(
            QueueUrl=request_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            MessageAttributeNames=['All']
        )
        # check if the message is still available or processed by other app-tier
        if 'Messages' not in response:
            continue

        message = response['Messages'][0]
        receipt_handle = message["ReceiptHandle"]

        # extract request_id and image name
        attributes = message.get('MessageAttributes', {})
        request_id = attributes.get('request_id', {}).get('StringValue')
        img_nam = attributes.get('image_name', {}).get('StringValue')

        # get image data from s3 in bytes
        obj = s3.get_object(Bucket='1235578190-in-bucket', Key=img_nam)
        image_bytes = obj['Body'].read()

        # run recognition model
        name, dist = face_match(BytesIO(image_bytes), 'data.pt')
        predict = str(name)

        image_name_no_ext = img_nam.split('.')[0]

        # push recognition result to s3 bucket
        s3.put_object(
            Bucket="1235578190-out-bucket",
            Key=image_name_no_ext,
            Body=predict
        )

        # push the recognition result to the response queue along with request_id
        sqs.send_message(
            QueueUrl=response_url,
            MessageBody=predict,
            MessageAttributes={
                "request_id": {
                    "StringValue": request_id,
                    "DataType": "String"
                }
            }
        )

        # delete the processed message from request queue
        sqs.delete_message(QueueUrl=request_url, ReceiptHandle=receipt_handle)

    except Exception as e:
        print(e)
        time.sleep(3)