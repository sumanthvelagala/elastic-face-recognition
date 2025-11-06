import boto3
import time

ec2 = boto3.client("ec2", region_name="us-east-1")
sqs = boto3.client("sqs", region_name="us-east-1")

req_q_url = sqs.get_queue_url(QueueName="1235578190-req-queue")['QueueUrl']

def get_queue_length():
    response = sqs.get_queue_attributes(
        QueueUrl=req_q_url,
        AttributeNames=["ApproximateNumberOfMessages"]
    )
    return int(response["Attributes"]["ApproximateNumberOfMessages"])

def start_instances(instances):
    if instances:
        response = ec2.start_instances(InstanceIds=instances)
        
def stop_instances(instances):
    if instances:
        response = ec2.stop_instances(InstanceIds=instances)

def get_instance_state(state):
    response = ec2.describe_instances(
        Filters=[
            {"Name": "tag:category", "Values": ["app-tier"]},
            {"Name": "instance-state-name", "Values": [state]}
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance["InstanceId"])
    
    return instances

if __name__ == "__main__":
    try:
        while True:
            q_len = get_queue_length()
            stopped_inst = get_instance_state("stopped")
            running_inst = get_instance_state("running")
            running_inst_count = len(running_inst)

            if q_len > running_inst_count and stopped_inst:
                needed_count = min(q_len - running_inst_count, len(stopped_inst))
                start_instances(stopped_inst[:needed_count])
            
            elif q_len == 0 and running_inst_count > 0:
                stop_instances(running_inst)
            
            time.sleep(2)
            
    except Exception as e:
        print(e)

