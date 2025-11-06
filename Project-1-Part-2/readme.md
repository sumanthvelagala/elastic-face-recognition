# Elastic Face Recognition Application (IaaS)

## Project Overview

This project implements a **fully elastic cloud-based face recognition system** using Amazon AWS IaaS components: EC2, S3, and SQS.  
It consists of three main tiers:

1. **Web Tier** (`server.py`, `controller.py`)
   - Accepts image uploads from users via HTTP POST `/`
   - Stores images in **S3 input bucket**
   - Sends file names as messages to **SQS request queue**
   - Waits for results on **response SQS queue**
   - Returns recognition result in plain text format:  
     `<filename>:<prediction>`

2. **Application Tier** (`backend.py`)
   - Deployed using EC2 instances created from a custom AMI.
   - Polls messages from the request SQS queue.
   - Downloads images from S3 input bucket.
   - Runs the deep learning face recognition model.
   - Uploads inference results to S3 output bucket.
   - Sends results to the response SQS queue.
   - Deletes processed messages and temporary files.

3. **Autoscaling Controller** (`controller.py`)
   - Monitors SQS queue length.
   - Starts or stops app-tier instances based on queue size.
   - Maintains scaling between 0 and 15 app-tier EC2 instances.
   - Ensures zero running instances when no requests exist.



## AWS Cloud Architecture

    ┌─────────────────────────┐
    │       Web Tier (FastAPI)│
    │   - server.py           │
    │   - controller.py       │
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │ SQS Request Queue       │
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │ App Tier (EC2 AMI)      │
    │ - backend.py            │
    │ - Face Recognition Model│
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │  S3 Input & Output      │
    │  Buckets                │
    └────────────┬────────────┘
                 │
                 ▼
    ┌─────────────────────────┐
    │  SQS Response Queue     │
    └─────────────────────────┘


---

## Setup Instructions

### 1. AWS Resource Setup

1. **Create S3 buckets**(user desired names)
in-bucket
out-bucket

text

2. **Create SQS queues**(use desired names)
req-queue
resp-queue

- Set **max message size** to **1KB** for the request queue.

3. **IAM Role Permissions**
Attach following managed policies for EC2 instances:
- `AmazonS3FullAccess`
- `AmazonSQSFullAccess`

---

### 2. Setup Application Tier (AMI)

1. **Launch a Base EC2 Instance**  
   - **AMI**: Amazon Linux 2  
   - **Instance Type**: t2.micro (or higher)

2. **Install Required Dependencies**
sudo yum update -y
sudo yum install -y python3 git
pip3 install boto3 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

3. **Copy Backend and Model Files**
scp -i your-key.pem backend.py data.pt ec2-user@<instance-public-ip>:/home/ec2-user/

4. **Install Node.js and PM2**  
PM2 helps keep the backend continuously running in the background, restarting automatically after reboots.

curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
sudo npm install pm2 -g

Verify installation:
node -v
pm2 -v

5. **Run and Register Backend with PM2**
cd /home/ec2-user
pm2 start backend.py --interpreter python3 --name backend-server
pm2 list

6. **Enable PM2 Auto-Start on Boot**
pm2 startup 
run the command provided by the terminal after running startup
pm2 save


7. **Create the AMI**
- Once set up, go to the AWS Console → EC2 → *Your instance* → **Actions > Image and templates > Create Image**.
- Name it **app-tier-ami**.

**All future app-tier instances** will use this AMI for autoscaling.

---

### 3. Setup Web Tier (FastAPI)

1. **Launch an EC2 Instance for Web Tier**
   - **Name**: `web-instance`
   - **Assign a static Elastic IP**

2. **Install FastAPI and Dependencies**
sudo yum install python3 -y
pip install fastapi uvicorn aioboto3 boto3

3. **Install Node.js and PM2**
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
sudo npm install pm2 -g

Verify installation:
node -v
pm2 -v

4. **Upload the Following Files**
- `server.py`
- `controller.py`

5. **Start FastAPI App Using PM2 for Process Management**
pm2 start uvicorn --name web-server --
server:app --host 0.0.0.0 --port 8000
pm2 list

This keeps your server running, auto-restarts on crash, supports logs, and works after reboot.

6. **Enable PM2 Startup on Boot**
pm2 startup 
run the command provided by the terminal after running startup
pm2 save


The web server listens on port **8000** and is now managed by PM2 for persistent, reliable uptime.

---

### 4. Autoscaling Controller

1. The controller runs on the same **web-tier instance**.
2. It monitors the request queue’s length and performs:
- Start EC2 instances when messages pile up.
- Stop EC2 instances when requests are completed.
3. It ensures **0 active** app-tier instances when idle.
4. **Run the controller with PM2 for process management:**
Start the controller script with PM2:
pm2 start controller.py --interpreter python3 --name autoscaling-controller
pm2 list
5. **Enable PM2 Startup on Boot**
pm2 startup 
run the command provided by the terminal after running startup
pm2 save
---

## Expected Output

HTTP Response Example:
test_001:Paul


## Directory Structure

Project-2-Part-2
│
├── web-tier/
│ ├── server.py
│ └── controller.py
│
└── app-tier/
  ├── Face Detection Model
  └── backend.py

---

## Notes
- Model used for detection is available at https://github.com/CSE546-Cloud-Computing/CSE546-SPRING-2025/tree/model 
- **Message size limit:** Request queue = 1KB  (To avoid pushing the entire image into queue)
- **Scaling limit:** Maximum 15 app-tier instances  
- Attach IAM Role to web-tier EC2 and app-tier EC2 with permissions to S3 and SQS.



# Stage - 1 (Creating AMI)
Transfer the model from local machine to cloud EC2 instance using scp
scp -i <path-to-pem_file> -r <path-to-folder> ec2-user@<DNS-Name_of_ec2>:<path-to-folder-in-ec2>
get 
- get request from request sqs which have the file name
- download the image to a local path to ec2 from s3 bucket
- use this image for model inference
- store the result in s3 output bucket
- push result into sqs response queue

## Useful commands
# To test the web-tier with an image
curl -X POST "http://<EC2-PUBLIC-IP>:8000/" -F "inputFile=@/path/to/face_test.jpg"

# To empty items from bucket
aws s3 rm s3://<bucket-name> --recursive --region us-east-1

# To remove all the messages in the queue
aws sqs purge-queue --queue-url <queu-url> --region us-east-1
