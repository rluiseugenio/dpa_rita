# PYTHONPATH='.' luigi --module clean_luigi CleanColumn_Testing --local-scheduler
# PYTHONPATH='.' luigi --module clean_luigi CleanRango_Testing --local-scheduler

###  Librerias necesarias
import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
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
import os

###  Imports desde directorio de proyecto dpa_rita
## Credenciales
from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)

from src.utils.metadatos_utils import C_testing_clean_columns,C_testing_clean_rangos
from src.utils.metadatos_utils import Linaje_clean_columns_testing, Linaje_clean_rangos_testing

from testing.test_clean_columns import Test_Columns_Case
from testing.test_clean_rangos import Test_Ranges_Case

MetadatosCleanColumnTesting = Linaje_clean_columns_testing()

class CleanColumn_Testing(luigi.Task):
    '''
    Prueba unitaria de número de columnas correctas en clean.rita
    '''
    # def requires(self):
    #     return Extraction()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosCleanColumnTesting.fecha =  datetime.now()
    MetadatosCleanColumnTesting.usuario = getpass.getuser()

    def run(self):
        
        
        unit_test_cleancolumns = Test_Columns_Case()
        unit_test_cleancolumns.test_that_all_columns_are_present()

    def output(self):
        return

@CleanColumn_Testing.event_handler(Event.SUCCESS)
def on_success(self):
    MetadatosCleanColumnTesting.ip_ec2 = ""
    MetadatosCleanColumnTesting.task_status ="Successful"
    print(MetadatosCleanColumnTesting.to_upsert())
    C_testing_clean_columns(MetadatosCleanColumnTesting.to_upsert())

@CleanColumn_Testing.event_handler(Event.FAILURE)
def on_failure(self,exception):
    MetadatosCleanColumnTesting.ip_ec2 = "Número de columnas no coincide"
    MetadatosCleanColumnTesting.task_status ="Failure"
    print(MetadatosCleanColumnTesting.to_upsert())
    C_testing_clean_columns(MetadatosCleanColumnTesting.to_upsert())



MetadatosCleanRangoTesting = Linaje_clean_rangos_testing()
class CleanRango_Testing(luigi.Task):
    '''
    Prueba unitaria levels de columna rangoatrasohoras de clean son 
    los correctos
    '''
    # def requires(self):
    #     return Extraction()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosCleanRangoTesting.fecha =  datetime.now()
    MetadatosCleanRangoTesting.usuario = getpass.getuser()

    def run(self):
       
        
        unit_test_cleanrangos = Test_Ranges_Case()
        unit_test_cleanrangos.test_that_all_ranges_are_present()

    def output(self):
        return

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

