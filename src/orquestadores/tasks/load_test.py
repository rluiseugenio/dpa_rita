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
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load
from src.orquestadores.tasks.metadatos_extract import Metadata_Extract
from src.orquestadores.tasks.testing.test_absent_hearders import TestingHeaders
#from task.metadatos_extract import Metadata_Extract
# ======================================================
# Prueba unitaria de la etapa load
# ======================================================

#from src.orquestadores.tasks.testing.test_absent_hearders import TestingHeaders
MetadatosLoadTesting = Linaje_load_testing()

class Load_Testing(luigi.Task):
    '''
    Prueba unitaria de estructura de archivos descargados
    '''
    def requires(self):
        return Metadata_Extract()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosLoadTesting.fecha =  datetime.now()
    MetadatosLoadTesting.usuario = getpass.getuser()

    def run(self):
        # Obtiene anio y mes correspondiente fecha actual de ejecucion del script
        now = datetime.now()

        # Recolectamos parametros de mes y anio de solicitud descarga a API Rita para metadatos_utils
        MetadatosLoadTesting.year = now.year
        MetadatosLoadTesting.month = now.month

        unit_test_load = TestingHeaders()
        unit_test_load.test_create_resource()

        os.system('echo "ok"> ./target/testing_load_ok.txt')

    def output(self):
        output_path='./target/testing_load_ok.txt'
        return luigi.LocalTarget(output_path)

# Decoradores para escribir metadatos de la prueba (aun si falla)
@Load_Testing.event_handler(Event.SUCCESS)
def on_success(self):
    MetadatosLoadTesting.ip_ec2 = ""
    MetadatosLoadTesting.task_status ="Successful"
    print(MetadatosLoadTesting.to_upsert())
    EL_testing_load(MetadatosLoadTesting.to_upsert())

@Load_Testing.event_handler(Event.FAILURE)
def on_failure(self,exception):
    MetadatosLoadTesting.ip_ec2 = "Archivo csv con distinta estructura de columnas"
    MetadatosLoadTesting.task_status ="Failure"
    print(MetadatosLoadTesting.to_upsert())
    EL_testing_load(MetadatosLoadTesting.to_upsert())
