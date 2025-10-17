import boto3

sqs = boto3.client('sqs',region_name="us-east-1")
s3 = boto3.client('s3',region_name="us-east-1")
"""
sqs.create_queue(
            QueueName='1235578190-req-queue',
            Attributes={
                'MaximumMessageSize':'1024',
                'VisibilityTimeout': '10'

            }
        )

sqs.create_queue(
            QueueName='1235578190-res-queue',
            Attributes={
                'MaximumMessageSize':'1024',
                'VisibilityTimeout': '10'

            }
        )

s3.create_bucket(
            Bucket='1235578190-in-bucket'
        )
s3.create_bucket(
            Bucket='1235578190-out-bucket'
        )
"""

import boto3

ec2 = boto3.client("ec2", region_name="us-east-1")

# Configuration
ami_id = "ami-060ee5998362ff0f2"        # Replace with your AMI ID
instance_type = "t2.micro"              # Adjust as needed
key_name = "web-instance"                # Replace with your key pair name
security_group_ids = ["sg-073c56e59306bf46d"]  # Replace with your security group(s)

num_instances = 15
instances_to_launch = []

# Prepare TagSpecifications for each instance
for i in range(1, num_instances + 1):
    tag_spec = {
        "ResourceType": "instance",
        "Tags": [
            {"Key": "category", "Value": "app-tier"},
            {"Key": "Name", "Value": f"app-tier-instance-{i}"}
        ]
    }
    instances_to_launch.append(tag_spec)

# Launch instances one by one with unique tags
launched_instances = []
try:
    for tag_spec in instances_to_launch:
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroupIds=security_group_ids,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[tag_spec],
            IamInstanceProfile={"Name": "EC2S3AccessRole"} 
        )
        instance_id = response['Instances'][0]['InstanceId']
        launched_instances.append(instance_id)
        print(f"Launched instance {instance_id} with Name tag {tag_spec['Tags'][1]['Value']}")

except Exception as e:
    print(f"Error launching instances: {e}")

print(f"All launched instance IDs: {launched_instances}")
 
