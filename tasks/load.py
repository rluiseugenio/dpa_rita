###  Librerias necesarias
import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
from luigi.contrib.postgres import CopyToTable, PostgresQuery
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
from src.utils.db_utils import save_rds
from src.utils.metadatos_utils import Linaje_load

from tasks.extract import Extraction
from tasks.load_test import Load_Testing
# ======================================================
# Etapa load
# ======================================================

MiLinaje = Linaje_load()
meta_load = [] # lista para insertar metadatos

class Load(luigi.Task):
    '''
    Carga hacia RDS los datos de la carpeta data
    '''
    def requires(self):
        return Load_Testing()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MiLinaje.fecha =  datetime.now()
    MiLinaje.usuario = getpass.getuser()

    def run(self):
        # Ip metadatos
        MiLinaje.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

        #Subimos de archivos csv
        extension_csv = ".csv"
        dir_name="./src/data/"

        for item in os.listdir(dir_name):
            if item.endswith(extension_csv):
                table_name = "raw.rita"

                MiLinaje.nombre_archivo = item

                # Numero de columnas y renglones para metadatos
                df = pd.read_csv(dir_name + item, low_memory=False)
                MiLinaje.num_columnas = df.shape[1]
                MiLinaje.num_renglones = df.shape[0]

                MiLinaje.tamano_csv = Path(dir_name+item).stat().st_size

                try:
                    print(item)
                    save_rds(dir_name+item, table_name)
                    #os.remove(dir_name+item)

                    meta_load.append(MiLinaje.to_upsert())
                except:
                    print("Carga de "+item)


        os.system('echo "ok" >target/load_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "target/load_ok.txt"
        return luigi.LocalTarget(output_path)
