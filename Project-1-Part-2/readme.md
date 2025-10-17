# Stage - 1 (Creating AMI)
Transfer the model from local machine to cloud EC2 instance using scp
scp -i <path-to-pem_file> -r <path-to-folder> ec2-user@<DNS-Name_of_ec2>:<path-to-folder-in-ec2>
get 
- get request from request sqs which have the file name
- download the image to a local path to ec2 from s3 bucket
- use this image for model inference
- store the result in s3 output bucket
- push result into sqs response queue


Dry run
pm2 start backend.py --name app-tier
pm2 start "uvicorn server:app --host 0.0.0.0 --port 8000" --name web-tier

curl -X POST "http://<EC2-PUBLIC-IP>:8000/" -F "inputFile=@/path/to/face_test.jpg"
