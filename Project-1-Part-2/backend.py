import boto3
import os
import subprocess

try:
    sqs = boto3.client('sqs',region_name="us-east-1")

    request_url = sqs.get_queue_url(QueueName='1235578190-req-queue')['QueueUrl']
    response_url = sqs.get_queue_url(QueueName='1235578190-resp-queue')['QueueUrl']

    s3 = boto3.client('s3',region_name="us-east-1")
    while True:

        #get request from request queue
        response = sqs.receive_message(
            QueueUrl=request_url,
            MaxNumberOfMessages=1
            )
        # check if the message is still available or processed by other app-tier
        if 'Messages' not in response:
            continue

        message = response['Messages'][0]
        img_nam = message["Body"]
        receipt_handle = message["ReceiptHandle"]

        path = f'/home/ec2-user/images/{img_nam}'
        
        #download stored image from s3 to ec2 at path
        s3.download_file(Bucket='1235578190-in-bucket',Key=img_nam,Filename=path)

        #run recognition model
        result = subprocess.run(['python3','/home/ec2-user/CSE546-FALL-2025/face_recognition.py',path],
        cwd='/home/ec2-user/CSE546-FALL-2025',
        capture_output=True,
        text=True,
        check=True)
        predict = result.stdout
        print(result.stderr)

        # exclude the extension
        image_name = img_nam.split('.')[0]

        # push recognition result to s3 bucket
        s3.put_object(Bucket="1235578190-out-bucket",Key=image_name,Body=predict)

        # push the recognition result to the respose queue
        sqs.send_message(QueueUrl=response_url,MessageBody=f'{image_name}:{predict}')

        # delete the processed message from request queue
        sqs.delete_message(QueueUrl=request_url,ReceiptHandle=receipt_handle)
        # delete the image stored at path
        os.remove(path)

except Exception as e:
    print(e)

