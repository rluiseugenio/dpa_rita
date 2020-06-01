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
###librerias para clean
#from pyspark.sql import SparkSession
#from src.features.build_features import clean, crear_features

#Pruebas unitarias Load 
from testing.test_absent_hearders import TestingHeaders

###  Imports desde directorio de proyecto dpa_rita
## Credenciales
from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB
)

## Utilidades
from src.utils.metadatos_utils import Linaje_extract_testing, EL_testing_extract, Linaje_raw
from src.utils.metadatos_utils import EL_verif_query, EL_metadata, Linaje_raw,EL_load,clean_metadata_rds
from src.utils.metadatos_utils import Linaje_clean_data, Linaje_semantic, semantic_metadata, Insert_to_RDS
from src.utils.metadatos_utils import rita_light_query,Linaje_load,load_verif_query
from src.utils.metadatos_utils import Linaje_extract_testing, EL_testing_extract
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load
from src.utils.metadatos_utils import Linaje_semantic1_testing, Linaje_semantic2_testing, FE_testing_semantic

from src.utils.metadatos_utils import Linaje_load

from src.utils.db_utils import save_rds


# Inicializa la clase que reune los metadatos
MiLinajeExt = Linaje_raw() # extract y load
# ===============================
CURRENT_DIR = os.getcwd()
# ===============================s
# Tasks de Luigi

# ======================================================
# Etapa Extract
# ======================================================

meta_extract = []

class Extraction(luigi.Task):
    '''
    Descarga en zip los datos de Rita (encarpeta data)
    '''
    # texto para formarm URL de rita
    BASE_URL="https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MiLinajeExt.fecha =  datetime.now()
    MiLinajeExt.usuario = getpass.getuser()

    def run(self):
        # Obtiene anio y mes correspondiente fecha actual de ejecucion del script
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # Obtiene anio y mes base (tres anios hacia atras)
        base_year = current_year - 0
        base_month = current_month

        # Recolectamos IP para metadatos
        MiLinajeExt.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

        for anio in range(base_year,current_year+1):
            for mes in range(1,12+1):

                # Recolectamos parametros de mes y anio de solicitud descarga a API Rita para metadatos
                MiLinajeExt.year = str(anio)
                MiLinajeExt.month = str(mes)

                # check para no hacer peticiones fuera de la fecha actual
                if (anio <= current_year) & (mes <= current_month-3):
                    #URL para hacer peticion a API rita en anio y mes indicado
                    url_act = self.BASE_URL+str(anio)+"_"+str(mes)+".zip"

                    #tam = EL_verif_query(url_act,anio,mes)
                    tam=0

                    if tam==0:

                        #Descargamos los datos desde la API, en formato zip del periodo en cuestion
                        try:
                            print("Inicia descarga de "+str(anio)+"_"+str(mes)+".zip")
                            comando_descarga = 'wget ' + url_act + " -P " + "./src/data/"
                            os.system(comando_descarga)
                        except:
                            pass

                        #Escribimos el archivo descargado al bucket
                        #Autenticación en S3 con boto3
                        #ses = boto3.session.Session(profile_name='dpa', region_name='us-east-1')
                        #s3_resource = ses.resource('s3')
                        #obj = s3_resource.Bucket("test-aws-boto")
                        #print(ses)

                        #Escritura
                        output_path = "RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip"
                        dir_name="./src/data/"
                        name_to_zip = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

                        #obj.upload_file(dir_name+name_to_zip+str(anio)+"_"+str(mes)+".zip", output_path)

                        # Recolectamos nombre del .zip y path con el que se guardara consulta a
                        # API de Rita en S3 para metadatos
                        MiLinajeExt.ruta_s3 = "s3://test-aws-boto/"+"RITA/YEAR="+str(anio)+"/"
                        MiLinajeExt.nombre_archivo =  str(anio)+"_"+str(mes)+".zip"

                        #Recolectamos tamano del archivo recien escrito en S3 para metadatos
                        #ses = boto3.session.Session(profile_name="dpa", region_name='us-east-1')
                        #s3 = ses.resource('s3')
                        #bucket_name = "test-aws-boto"
                        #my_bucket = s3.Bucket(bucket_name)
                        #MiLinajeExt.tamano_zip = my_bucket.Object(key="RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip").content_length

                        # Recolectamos status para metadatos
                        MiLinajeExt.task_status = "Successfull"

                        # Insertamos metadatos a DB
                        print(MiLinajeExt.to_upsert())
                        meta_extract.append(MiLinajeExt.to_upsert())
                        #EL_metadata(MiLinajeExt.to_upsert())

        # Unzips de archivos zip recien descargados
        dir_name = "./src/data/" # directorio de zip
        extension_zip = ".zip"

        for item in os.listdir(dir_name):
            if item.endswith(extension_zip):
                #
                # Con archivo crea objeto zip y lo extrae
                zip_ref = ZipFile(dir_name+item) # create zipfile object
                zip_ref.extractall(dir_name) # extraccion al directorio
                zip_ref.close()
                # Elimina archivos residuales
                os.remove(dir_name+item)
                try:
                    os.remove(dir_name+'readme.html')
                except:
                    pass
                 #os.remove(dir_name+'readme.html')

        os.system('echo OK > target/extract_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "target/extract_ok.txt"
        return luigi.LocalTarget(output_path)


import luigi.contrib.postgres

class Metadata_Extract(luigi.contrib.postgres.CopyToTable):
    '''
    Task de luigi para insertar renglones en renglones en tabla de metadatos
    de la extraccion y load de metadatos a S3
    '''
    def requires(self):
        return Extraction()

    # Lectura de archivo de credenciales
    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST

    # Nombre de tabla donde se inserta info. Notas:
    # 1) si la tabla (sin esquema) no existe, luigi la crea con esquema publico,
    # 2) si el esquema de la tabla no existe, luigi devuelve error :(
    table = 'metadatos.extract'

    # Estructura de las columnas que integran la tabla (ver esquema)
    columns = [("fecha", "VARCHAR"),\
            ("nombre_task", "VARCHAR"),\
            ("year","VARCHAR"),\
            ("month","VARCHAR"),\
            ("usuario","VARCHAR"),\
            ("ip_ec2","VARCHAR"),\
            ("tamano_zip","VARCHAR"),\
            ("nombre_archivo","VARCHAR"),\
            ("ruta_s3","VARCHAR"),\
            ("task_status", "VARCHAR")]

    def rows(self):
        # Funcion para insertar renglones en tabla

        # Renglon o renglones (separados por coma) a ser insertado
        r = meta_extract

        # Insertamos renglones en tabla
        for element in r:
            yield element
        print('\n---Fin de  carga de metadatos de extract ---\n')


## Utilidades
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load

# ======================================================
# Prueba unitaria de la etapa load
# ======================================================

#from testing.test_absent_hearders import TestingHeaders
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

        os.system('echo "ok"> target/testing_load_ok.txt')

    def output(self):
        output_path='target/testing_load_ok.txt'
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


# ======================================================
# Metadatos de etapa load
# ======================================================

class Metadatos4_Load(luigi.contrib.postgres.CopyToTable):
    '''
    Task de luigi para insertar renglones en renglones en tabla de metadatos
    de load
    '''
    def requires(self):
        return Load()

    # Lectura de archivo de credenciales
    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST

    # Nombre de tabla donde se inserta info. Notas:
    # 1) si la tabla (sin esquema) no existe, luigi la crea con esquema publico,
    # 2) si el esquema de la tabla no existe, luigi devuelve error :(
    table = 'metadatos.load'

    # Estructura de las columnas que integran la tabla (ver esquema)
    columns = [("fecha", "VARCHAR"),\
            ("nombre_task", "VARCHAR"),\
            ("usuario","VARCHAR"),\
            ("ip_ec2","VARCHAR"),\
            ("tamano_csv","VARCHAR"),\
            ("nombre_archivo","VARCHAR"),\
            ("num_columnas", "VARCHAR"),\
            ("num_renglones", "VARCHAR")]

    def rows(self):
        # Funcion para insertar renglones en tabla

        # Renglon o renglones (separados por coma) a ser insertado
        r = meta_load

        # Insertamos renglones en tabla
        for element in r:
            yield element
        print('\n--- Carga de metadatos de load realizada con exito ---\n')