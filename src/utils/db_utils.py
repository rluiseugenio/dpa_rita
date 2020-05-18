import boto3
import os
from botocore.config import Config
import sys
import random
import time
import psycopg2
import pandas as pd
from io import StringIO

from src.utils.log_utils import setup_logging
logger = setup_logging(__name__, "utils.rds_objects2")

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
    MY_GROUP,
    MY_USER ,
    MY_PASS ,
    MY_HOST ,
    MY_PORT,
    MY_DB
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
        print(len(dbs['DBInstances']))
        for db in dbs['DBInstances']:
            #print(db)
            print ("User name: ", db['MasterUsername'], \
            ", Endpoint: ", db['Endpoint'],    \
            ", Address: ", db['Endpoint']['Address'],    \
            ", Port: ", db['Endpoint']['Port'],       \
            ", Status: ", db['DBInstanceStatus'],     \
            ", ID =", db['DBInstanceIdentifier'] , \
            #", pass =", db['MasterUserPassword'] , \
            ", DBInstanceClass =", db['DBInstanceClass'] , \
            ", PubliclyAccessible =", db['PubliclyAccessible'] , \
            ", AvailabilityZone =", db['AvailabilityZone'] , \
            #", VpcSecurityGroupIds =", db['VpcSecurityGroupIds']
            )
    except Exception as error:
        print (error)

def create_db(nuevo_id):
    try:

        db_vars = {
            "DBInstanceIdentifier":nuevo_id,
             "MasterUsername":'dpa',
             "MasterUserPassword":'dpa01_largo',
             "DBInstanceClass":'db.t2.micro',
             "Engine":'postgres',
             "AllocatedStorage":5,
             "Port":5432,
             "DBSubnetGroupName":'default-vpc-0a3808edd1a4e1e9c',
             "PubliclyAccessible":True,
             "AvailabilityZone" : MY_REGION2,
             #"DBSecurityGroups": [db_security],
             "VpcSecurityGroupIds" :["sg-07aa1c02e1d427317"]
             #"DBName":'metadatos'
        }
        rds_client.create_db_instance(**db_vars)
    except Exception as error:
        print(error)

def modify_db(my_id):
    db_vars = {
        "DBInstanceIdentifier":my_id,
         #"DBName":'metadatos'
    }
    rds_client.modify_db_instance(**db_vars)

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
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        print("PostgreSQL connection is closed")
    except Exception as error:
        print (error)

def insert_query(query, record_to_insert):
    try:
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()
        cursor.execute(query, record_to_insert)
        connection.commit()
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
    except Exception as error:
        print (error)

#==============================================================
def show_select(query):
    try:
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()

        cursor.execute(query)

        print("Selecting rows from table using cursor.fetchall")
        records = cursor.fetchall()
        print(len(records))
        print("Print each row and it's columns values")
        for row in records:
           print(row)

        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

def get_select(query):
    try:
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()

        cursor.close()
        connection.close()
        return records
        print("PostgreSQL connection is closed")

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

def get_dataframe(query):
    try:
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()

        cursor.execute(query)

        #print("Selecting rows from table using cursor.fetchall")
        records = cursor.fetchall()
        df = pd.DataFrame(records)
        col_names =  [i[0] for i in cursor.description]
        df.columns = col_names
        cursor.close()
        connection.close()
        #print("PostgreSQL connection is closed")
        return df
    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)


def execute_sql(file_dir):
    try:
        connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                     password=MY_PASS, # password de usuario de RDS
                                     host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                     port=MY_PORT, # cambiar por el puerto
                                     database=MY_DB ) # Nombre de la base de datos
        cursor = connection.cursor()

        print(file_dir)
        cursor.execute(open(file_dir, "r").read())
        connection.commit()
        cursor.close()
        connection.close()
    except (Exception, psycopg2.Error) as error :
        print ("Error while executing sql file", error)



def save_rds(file_name, table_name):

    # Copy to postgres
    connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                 password=MY_PASS, # password de usuario de RDS
                                 host=MY_HOST,#"127.0.0.1", # cambiar por el endpoint adecuado
                                 port=MY_PORT, # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    df = pd.read_csv(file_name)
    records = df.values.tolist()
    buffer = StringIO()
    for line in records:
        buffer.write('~'.join([repr(x) for x in line]) + '\n')

    buffer.seek(0)

    cursor.copy_from(buffer, table_name, null='NaN', sep ='~' )
    connection.commit()
    cursor.close()
    connection.close()


def save_rds_pandas(df,table_name):

    # Copy to postgres
    connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                 password=MY_PASS, # password de usuario de RDS
                                 host=MY_HOST,#"127.0.0.1", # cambiar por el endpoint adecuado
                                 port=MY_PORT, # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    records = df.values.tolist()
    buffer = StringIO()
    for line in records:
        buffer.write('~'.join([str(x) for x in line]) + '\n')

    buffer.seek(0)

    cursor.copy_from(buffer, table_name, null='NaN', sep ='~' )
    connection.commit()
    cursor.close()
    connection.close()

#file_name = "./../../data/datos_ejemplo.csv"
#file_name = "datos_ejemplo.csv"
#table_name = "raw.rita"
#save_rds(file_name, table_name)
#==============================================================
# DE AQUI PARA ABAJO SON PRUEBAS (BASURA)
#response=rds_client.describe_security_groups()
#print(response)
#describe_db()
def main():
    execute_sql("./sql/metada_extract.sql")

    query = "INSERT INTO metadatos.extract (fecha, nombre_task, year, month, usuario, ip_ec2, tamano_zip, nombre_archivo, ruta_s3, task_status) VALUES ( '2', '2', '3','3','4','5','5', '6', '6','8' ) ;"
    execute_query(query)

    query = "SELECT * FROM metadatos.extract ; "
    show_select(query)

    query = "CREATE SCHEMA IF NOT EXISTS paola ;"
    execute_query(query)

    query = "CREATE TABLE paola.prueba (nombre VARCHAR);"
    execute_query(query)

    query = "INSERT INTO paola.prueba (nombre) VALUES ('Paola');"
    execute_query(query)

    query = "SELECT * FROM paola.prueba ; "
    show_select(query)

#execute_sql("./sql/metada_model.sql")
#query = "SELECT * FROM metadatos.models ; "
#show_select(query)

def otro():
    query = """ INSERT INTO metadatos.models (fecha, objetivo, model_name, hyperparams, AUROC, AUPR, precision, recall, f1, train_time, test_split, train_nrows ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  ) """
    values = ("d1",
             "objetivo", "model_name",
             "json.dumps(hyperparams)",
             "AUROC"," AUPR"," precision"," recall", "f1", "train_time", "test_split"," train_nrows")
    insert_query(query, values)

    query = "SELECT * FROM metadatos.models ; "
    show_select(query)


#execute_sql("metada_extract.sql")

#resp = rds_client.describe_db_subnet_groups()
#print(resp['DBSubnetGroups'])

#create_db("metadatos")
#describe_db()
#create_table()
#create_table()
#create_db("metadats")
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
