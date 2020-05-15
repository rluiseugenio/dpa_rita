# PYTHONPATH='.' AWS_PROFILE=educate1 luigi --module alter_orq downloadDataS3 --local-scheduler

# PARA UN MODELO
#PYTHONPATH='.' AWS_PROFILE=dpa luigi --module alter_orq  RunModel --local-scheduler  --bucname models-dpa --numIt 2 --numPCA 3  --model LR --obj 0-1.5

# PARA TODOS LOS MODELOS
# PYTHONPATH='.' AWS_PROFILE=dpa luigi --module alter_orq  RunAllTargets --local-scheduler  --bucname models-dpa --numIt 1 --numPCA 2  --model LR

# CENTRAL scheduler
#PYTHONPATH='.' AWS_PROFILE=dpa luigi --module alter_orq  RunAllTargets  --bucname models-dpa --numIt 1 --numPCA 2  --model LR

###  Librerias necesarias
import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
from luigi.contrib.postgres import CopyToTable,PostgresQuery
import boto3
from datetime import date, datetime
import getpass # Usada para obtener el usuario
from io import BytesIO
import socket #import publicip
import requests
import os, subprocess, ast
import pandas as pd
import psycopg2
from psycopg2 import extras
from zipfile import ZipFile
from pathlib import Path
###librerias para clean
from pyspark.sql import SparkSession
from src.features.build_features import clean, crear_features

###  Imports desde directorio de proyecto dpa_rita
## Credenciales
from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)

## Utilidades
from src.utils.s3_utils import create_bucket
from src.utils.db_utils import create_db, execute_sql, save_rds
from src.utils.ec2_utils import create_ec2
from src.utils.metadatos_utils import EL_verif_query, EL_metadata, Linaje_raw,EL_load,clean_metadata_rds,Linaje_clean_data, Linaje_semantic, semantic_metadata, Insert_to_RDS, rita_light_query,Linaje_load,load_verif_query
from src.utils.db_utils import execute_sql
#from src.models.train_model import run_model
from src.models.save_model import parse_filename
from src.utils.metadatos_utils import Linaje_extract_testing, EL_testing_extract
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load
from src.utils.metadatos_utils import Linaje_semantic1_testing, Linaje_semantic2_testing, FE_testing_semantic

from tasks.extract import Extraction
from tasks.load_test import Load_Testing
from tasks.load import Load
from tasks.clean_column_testing import CleanColumn_Testing
#-----------------------------------------------------------------------------------------------------------------------------
# ======================================================
# Pruebas unitarias clean
# ======================================================
from src.utils.metadatos_utils import C_testing_clean_columns,C_testing_clean_rangos
from src.utils.metadatos_utils import Linaje_clean_columns_testing, Linaje_clean_rangos_testing

from testing.test_clean_columns import Test_Columns_Case
from testing.test_clean_rangos import Test_Ranges_Case

MetadatosCleanRangoTesting = Linaje_clean_rangos_testing()
class CleanRango_Testing(luigi.Task):
    '''
    Prueba unitaria levels de columna rangoatrasohoras de clean son
    los correctos
    '''
    def requires(self):
         return CleanColumn_Testing()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosCleanRangoTesting.fecha =  datetime.now()
    MetadatosCleanRangoTesting.usuario = getpass.getuser()

    def run(self):
        unit_test_cleanrangos = Test_Ranges_Case()
        unit_test_cleanrangos.test_that_all_ranges_are_present()
        os.system('echo "ok" >target/clean_ran_ok.txt')

    def output(self):
        #Ruta en donde se guarda el target del task
        output_path = "target/clean_ran_ok.txt"
        return luigi.LocalTarget(output_path)

@CleanRango_Testing.event_handler(Event.SUCCESS)
def on_success(self):
    MetadatosCleanRangoTesting.ip_ec2 = ""
    MetadatosCleanRangoTesting.task_status ="Successful"
    print(MetadatosCleanRangoTesting.to_upsert())
    C_testing_clean_rangos(MetadatosCleanRangoTesting.to_upsert())

@CleanRango_Testing.event_handler(Event.FAILURE)
def on_failure(self,exception):
    MetadatosCleanRangoTesting.ip_ec2 = "levels no coinciden"
    MetadatosCleanRangoTesting.task_status ="Failure"
    print(MetadatosCleanRangoTesting.to_upsert())
    C_testing_clean_rangos(MetadatosCleanRangoTesting.to_upsert())
