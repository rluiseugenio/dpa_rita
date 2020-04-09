import boto3
import os
from botocore.config import Config
import sys
import random
import time
import psycopg2

from src.d00_utils.log_utils import setup_logging
logger = setup_logging(__name__, "d00_utils.rds_objects")

# GLOBALS
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

os.environ['AWS_PROFILE'] = MY_PROFILE
os.environ['AWS_DEFAULT_REGION'] = MY_REGION
boto_config = Config(retries=dict(max_attempts=20))
rds_client = boto3.client('rds',config=boto_config, region_name=MY_REGION)

#==============================================================
#METHODS
# get all of the db instances
def describe_db():
    try:
        dbs = rds_client.describe_db_instances()
        #print(dbs['DBInstances'])
        for db in dbs['DBInstances']:
            print(db)
            print ("User name: ", db['MasterUsername'], \
            ", Endpoint: ", db['Endpoint'],    \
            ", Address: ", db['Endpoint']['Address'],    \
            ", Port: ", db['Endpoint']['Port'],       \
            ", Status: ", db['DBInstanceStatus'],     \
            ", ID =", db['DBInstanceIdentifier'] )
    except Exception as error:
        print (error)

def create_db(nuevo_id, db_security):
    try:

        response = rds_client.create_db_security_group(
                DBSecurityGroupName=db_security,
                DBSecurityGroupDescription='prueba',
                Tags=[
                    {
                        'Key': 'string',
                        'Value': 'string'
                    },
                ]
            )

        db_vars = {
            "DBInstanceIdentifier":nuevo_id,
             "MasterUsername":'dpa',
             "MasterUserPassword":'dpa01_largo',
             "DBInstanceClass":'db.t2.micro',
             "Engine":'postgres',
             "AllocatedStorage":5,
             "Port":5432,
             "DBSecurityGroups": [db_security],
             "PubliclyAccessible":"True"
             #"DBName":'metadatos'
        }
        rds_client.create_db_instance(**db_vars)
    except Exception as error:
        print(error)



def delete_db(id_borrar):
    try:
        response = rds_client.delete_db_instance(
        DBInstanceIdentifier=id_borrar,
        SkipFinalSnapshot=True)
        print (response)
    except Exception as error:
        print (error)


def execute_query(query):
    try:
        conn = psycopg2.connect(user="dpa", # Usuario RDS
                                      password="dpa01_largo", # password de usuario de RDS
                                      host=host,#"127.0.0.1", # cambiar por el endpoint adecuado
                                      port="5432", # cambiar por el puerto
                                      database=db_name) # Nombre de la base de datos

        cursor = conn.cursor()
        cursor.execute(query)
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    except Exception as error:
        print (error)


#==============================================================
def show_select(postgreSQL_select_Query):
    try:
        host="rita-db.clx22b04cf2j.us-west-2.rds.amazonaws.com"
        connection = psycopg2.connect(user="postgres", # Usuario RDS
                                     password="oEaAGKDQx1wLD9y1HVce", # password de usuario de RDS
                                     host=host,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port="5432", # cambiar por el puerto
                                     database="postgres") # Nombre de la base de datos
        cursor = connection.cursor()

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from mobile table using cursor.fetchall")
        mobile_records = cursor.fetchall()
        print(len(mobile_records))
        print("Print each row and it's columns values")
        for row in mobile_records:
           print(row)
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")




#==============================================================

# MAIN
#url = "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_1988_11.zip"
#postgreSQL_select_Query = "select * from metadatos.extract where task_status = '" + str(url) + "';"
#show_select(postgreSQL_select_Query)

#postgreSQL_select_Query = "select * from metadatos.extract;"
#show_select(postgreSQL_select_Query)
#create_db('metadatos')
#describe_db()
#delete_db('metadatos')
#delete_db('postgres')
#describe_db()
#create_db()
#describe_db()
#execute_query(query)
