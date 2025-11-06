import boto3

# Initialize EC2 client
ec2 = boto3.client("ec2", region_name="us-east-1")

# Filter for instances tagged as app-tier
response = ec2.describe_instances(
    Filters=[{"Name": "tag:category", "Values": ["app-tier"]}]
)

# Collect instance IDs (only those not terminated)
instance_ids = [
    instance["InstanceId"]
    for reservation in response["Reservations"]
    for instance in reservation["Instances"]
    if instance["State"]["Name"] != "terminated"
]

if instance_ids:
    print(f"Found {len(instance_ids)} instance(s) to terminate: {instance_ids}")
    ec2.terminate_instances(InstanceIds=instance_ids)
    print("Termination initiated for all matching instances.")
else:
    print("No instances found with tag category=app-tier.")
