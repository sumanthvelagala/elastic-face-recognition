# Face Recognition Web Tier Part-1 – AWS IaaS Project (CSE546)

## Project Description

This project builds an elastic cloud-based web tier application using Amazon Web Services (AWS) Infrastructure as a Service (IaaS). It provides a scalable face recognition service that accepts image uploads from clients via HTTP POST requests, stores the images in an Amazon S3 input bucket, and returns classification results by querying a lookup table stored in Amazon SimpleDB.

Designed as the front end of a multi-tier cloud application, the web tier is implemented in Python using FastAPI and runs on a single EC2 micro instance within the US-East-1 region. For this part of the project, actual face recognition is emulated by looking up pre-populated classification data in SimpleDB rather than running a real ML model.

Part I of this project focuses on familiarizing with AWS core IaaS resources and building foundational skills needed to develop the complete face recognition cloud platform that will be expanded in Part II.

### Key features and requirements of the project include:

- Handling concurrent HTTP POST requests with image uploads.
- Storing images in a dedicated S3 input bucket named following a specific convention.
- Leveraging Amazon SimpleDB as a structured key-value store to emulate face recognition results.
- Returning recognition results as plain text responses directly to client requests.
- Securing AWS access through IAM roles rather than hardcoded credentials.
- Assigning a static Elastic IP to the EC2 instance to provide a stable public endpoint.

This project facilitates practical experience configuring and using core AWS IaaS services and demonstrates efficient cloud-native API design principles.

---

## Dataset and Classification Results

- **Face Images Dataset**: [face_images_1000.zip](https://github.com/CSE546-Cloud-Computing/CSE546-SPRING-2025/blob/datasets/face_images_1000.zip)  
  This dataset contains the input face images that must be uploaded by the web tier to the S3 input bucket and used to populate entries in the SimpleDB domain for emulated recognition lookup.

- **Classification Results File**: [classification_face_images_1000.csv](https://github.com/CSE546-Cloud-Computing/CSE546-SPRING-2025/blob/datasets/Classification%20Results%20on%20Face%20Dataset%20(1000%20images).csv)  
  This file contains the classification results that should be used to populate the SimpleDB domain as ground truth for the face recognition emulation. The web tier queries these results from SimpleDB and returns them to clients as the recognition output.

---

## Why Use Both S3 and SimpleDB?

- **Amazon S3** stores image files as scalable, inexpensive, and durable object storage since images are large binary data optimized for S3.
- **Amazon SimpleDB** provides fast lookup of recognition labels with structured, key-value queries by filename.
- Combining both leverages scalable storage with rapid, structured querying — each service performing what it does best.

---

## Performance

- Successfully processed 100 image recognition requests in under 1 second, demonstrating efficient API design and cloud infrastructure optimization.

---

## Setup Instructions

### 1. Launch & Configure EC2 Instance

- Launch an EC2 instance (Amazon Linux 2) in **us-east-1 (N. Virginia)**, name it `web-instance`.
- Instance type: `t2.micro` (Free tier eligible)
- Create a key pair for SSH access.
- Configure Security Group to allow inbound ports: 22 (SSH) and 8000 (HTTP).
- Allocate and associate an Elastic IP for a static IP address.

### 2. Create & Attach IAM Role

- Go to AWS IAM → Roles → Create role for EC2 with `AmazonS3FullAccess`.
- Name it `web-tier-role` (customizable).
- Attach this role to your EC2 instance via EC2 Console → Actions → Security → Modify IAM Role.
- This avoids hardcoding credentials and improves security.

### 3. Connect and Set Up EC2

- ssh -i /path/to/key.pem ec2-user@<your-elastic-ip>
- sudo yum update -y
- sudo yum install -y python3 git
- python3 -m pip install --user fastapi uvicorn boto3


### 4. Install Node.js & PM2 for Monitoring

- sudo yum install -y nodejs
- sudo npm install -g pm2


### 5. Upload Your Code and CSV

Use SCP from your local machine to upload files:

- scp -i </path/to/key.pem> server.py ec2-user@<your-elastic-ip>:~/
- scp -i </path/to/key.pem> classification_face_images_1000.csv ec2-user@<your-elastic-ip>:~/



### 6. Running and Persisting the FastAPI Server

Start the server with PM2:

- pm2 start "uvicorn server:app --host 0.0.0.0 --port 8000" --interpreter=python3 --name=web-server
- pm2 save
- pm2 startup


Run the sudo command that PM2 outputs, e.g.:

- sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ec2-user --hp /home/ec2-user
- pm2 save


### 7. Monitor and Manage the Web Server

- pm2 list # List all servers
- pm2 logs web-server # View logs
- pm2 restart web-server # Restart server after updates
- pm2 stop web-server # Stop server
- pm2 delete web-server # Delete server process


### 8. Testing

Test your deployed API with curl:

- curl -X POST -F "inputFile=@test_00.jpg" http://<your-elastic-ip>:8000/


Expected response (plain text):

test_00:Paul

text

---

## Response Payload Example from SimpleDB

{
"Attributes": [
{
"Name": "person_name",
"Value": "JohnDoe"
}
],
"ResponseMetadata": {
"RequestId": "abc123-xyz456",
"BoxUsage": "0.0000219907",
"HTTPStatusCode": 200,
"HTTPHeaders": {
"content-type": "text/xml",
"content-length": "123",
"x-amzn-requestid": "abc123-xyz456",
"date": "Mon, 27 Sep 2025 21:15:22 GMT"
},
"RetryAttempts": 0
}
}