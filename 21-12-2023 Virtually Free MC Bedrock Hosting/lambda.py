import boto3
region = "REGION_CODE_HERE"
instances = ["INSTANCE_ID_HERE"]
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    ec2.start_instances(InstanceIds=instances)