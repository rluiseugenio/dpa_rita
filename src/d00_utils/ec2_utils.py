#=====================================
# Resources:
#https://blog.ipswitch.com/how-to-create-and-configure-an-aws-vpc-with-python
#https://blog.ipswitch.com/how-to-create-an-ec2-instance-with-python
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#vpc
#=====================================
import boto3
import os
from botocore.config import Config
import pandas as pd
import subprocess

from src.d00_utils.log_utils import setup_logging
logger = setup_logging(__name__, "d00_utils.rds_objects")

from src import (
    BUCKET,
    MY_REGION,
    MY_REGION2,
    MY_PROFILE,
    MY_KEY,
    MY_AMI ,
    MY_VPC ,
    MY_GATEWAY,
    MY_SUBNET,
    MY_GROUP
)

#==================================
# GLOBALS: En un futuro poner el conf
MY_REGION = "us-west-2"
MY_REGION2 = "us-west-2a"
MY_PROFILE = "dpa"
MY_KEY = 'ec2-keypair'
MY_AMI = "ami-0d1cd67c26f5fca19"
MY_VPC = "vpc-0cffc8f100e5271b3"
MY_GATEWAY = "igw-08da14e5eaa65c84d"
MY_SUBNET = "subnet-087d35547d07c26c6"
MY_GROUP ="sg-0fa1c85891a994d1b"
#==================================

#==================================
# CONEXION
os.environ['AWS_PROFILE'] = MY_PROFILE
os.environ['AWS_DEFAULT_REGION'] = MY_REGION
boto_config = Config(retries=dict(max_attempts=20))

ec2_client = boto3.client('ec2',config=boto_config, region_name=MY_REGION)
ses = boto3.session.Session(profile_name=MY_PROFILE, region_name=MY_REGION)
ec2_resource = ses.resource('ec2')
#==================================

#==================================
# METODOS
def describe_ec2():
    response = ec2_client.describe_instances()
    print(response)
    av_zones, instance_ids, state_names= [], [], []
    for res in response['Reservations']:
        for ins in res['Instances']:
            av_zones.append(ins['Placement']['AvailabilityZone'])
            instance_ids.append(ins['InstanceId'])
            state_names.append(ins['State']['Name'])
    return pd.DataFrame({
        'InstanceId': instance_ids,
        'Availibility Zone': av_zones,
        'State': state_names
    })

def excute_bash(bashCommand):
    try:
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(output, error)
    except Exception as error:
        print(error)


def create_keys(key_name):
    try:
        # call the boto ec2 function to create a key pair
        key_pair = ec2_resource.create_key_pair(KeyName=key_name)
        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        outfile.write(KeyPairOut)

        excute_bash('echo "ec2-keypair.pem" > .gitignore')
        excute_bash('sudo chmod 400 ec2-keypair.pem')

    except Exception as error:
        print(error)

def configure_network(my_block = '172.16.0.0/16', vpa_name  = "vpc_dpa"):
    try:
        vpc = ec2_resource.create_vpc(CidrBlock='172.16.0.0/16')
        vpc.create_tags(Tags=[{"Key": "Name", "Value": vpa_name }])
        vpc.wait_until_available()
        print(vpc.id)


        # enable public dns hostname so that we can SSH into it later
        ec2_client .modify_vpc_attribute( VpcId = vpc.id ,
                                        EnableDnsSupport = { 'Value': True } )
        ec2_client .modify_vpc_attribute( VpcId = vpc.id ,
                                        EnableDnsHostnames = { 'Value': True } )

        # create an internet gateway and attach it to VPC
        internetgateway = ec2_resource.create_internet_gateway()
        vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)

        # create a route table and a public route
        routetable = vpc.create_route_table()
        route = routetable.create_route(DestinationCidrBlock='0.0.0.0/0',
                                        GatewayId=internetgateway.id)

        # create subnet and associate it with route table
        subnet = ec2_resource.create_subnet(CidrBlock='172.16.1.0/24', VpcId=vpc.id,
         AvailabilityZone=MY_REGION2)
        routetable.associate_with_subnet(SubnetId=subnet.id)


        # Create a security group and allow SSH inbound rule through the VPC
        securitygroup = ec2_resource.create_security_group(GroupName='SSH-ONLY',
                            Description='only allow SSH traffic', VpcId=vpc.id)

        securitygroup.authorize_ingress(CidrIp='0.0.0.0/0', IpProtocol='tcp',
                                        FromPort=22, ToPort=22)

        return vpc.id, internetgateway.id, subnet.id, securitygroup.group_id
    except Exception as error:
        print(error)



def create_ec2():
    try:
        ec2_resource.create_instances(
         ImageId= MY_AMI,
         InstanceType='t2.micro',
         MaxCount=1,
         MinCount=1,
         NetworkInterfaces=[{
             'SubnetId': MY_SUBNET,
             'DeviceIndex': 0,
             'AssociatePublicIpAddress': True,
             'Groups': [MY_GROUP]
             }],
         KeyName= MY_KEY,
         Placement={
        'AvailabilityZone': MY_REGION2,
        }
        )
    except Exception as error:
        print(error)


#==================================

#==================================
# MAIN
#describe_ec2()
#MY_VPC, MY_GATEWAY, MY_SUBNET, MY_GROUP = configure_network()
#print("VPC: ", MY_VPC, "GATEWAY: ",  MY_GATEWAY, "SUBNET: ",MY_SUBNET,
#        "GROUP: ", MY_GROUP)
#create_ec2()
#describe_ec2()


# Retrieves all regions/endpoints that work with EC2
#response = ec2_client.describe_regions()
#print('Regions:', response['Regions'])

# Boto 3
#ec2.instances.filter(InstanceIds=ids).stop()
#ec2.instances.filter(InstanceIds=ids).terminate()

# Retrieves availability zones only for region of the ec2 object
#response = ec2_client.describe_availability_zones()
#print('Availability Zones:', response['AvailabilityZones'])

#ec2.start_instances(InstanceIds=list(data_ec2.loc[data_ec2['State'] == 'stopped', 'InstanceId']))
#ec2.stop_instances(InstanceIds=list(data_ec2.loc[data_ec2['State'] == 'running', 'InstanceId']))
#==================================
