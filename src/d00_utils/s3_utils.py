import boto3
import os
from botocore.config import Config
import sys
import random
import time

#import rita
from src.d00_utils.log_utils import setup_logging
#logger = setup_logging(__name__, "d00_utils.s3_objects")

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


ses = boto3.session.Session(profile_name=MY_PROFILE, region_name=MY_REGION,)
s3 = ses.resource('s3')
bucket_name = BUCKET

# listar los buckets que están en este perfil y región.
def describe_s3():
    try:
        for bucket in s3.buckets.all():
            print(bucket.name)
        logger.debug("Prints buckets")
    except Exception as error:
        print (error)
        logger.error("Error printing bucket names")


def get_s3_objects(bucket_name):
    try:
        my_bucket = s3.Bucket(bucket_name)
        for my_bucket_object in my_bucket.objects.all():
            print(my_bucket_object)
    except Exception as error:
        print (error)
        logger.error("{} Bucket not found".format(bucket_name))

def delete_object_s3(bucket_name, file_name):
    try:
        my_bucket = s3.Bucket(bucket_name)
        s3.Object(bucket_name, file_name).delete()
    except Exception as error:
        print (error)
        logger.error("{} Bucket or {} file not found".format(bucket_name,
         filename))


def delete_s3(bucket_name):
    try:
        my_bucket = s3.Bucket(bucket_name)
        my_bucket.delete()
    except Exception as error:
        print (error)
        logger.error("{} Bucket not found".format(bucket_name))

def create_bucket(bucket_name):
    try:
        s3.create_bucket(Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': MY_REGION,},
                ACL='private')
    except Exception as error:
        print (error)
        logger.error("{} Error in bucket".format(bucket_name))



## ========================================
#describe_s3()
#get_s3_objects(BUCKET)
