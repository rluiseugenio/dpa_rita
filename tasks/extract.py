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
#from pyspark.sql import SparkSession

from src.utils.metadatos_utils import EL_verif_query, EL_metadata, Linaje_raw,EL_load,clean_metadata_rds,Linaje_clean_data, Linaje_semantic, semantic_metadata, Insert_to_RDS, rita_light_query,Linaje_load,load_verif_query
from src.models.save_model import parse_filename
from src.utils.metadatos_utils import Linaje_extract_testing, EL_testing_extract
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load

# Inicializa la clase que reune los metadatos
MiLinajeExt = Linaje_raw() # extract y load

# ======================================================
# Etapa Extract
# ======================================================

meta_extract = [] # arreglo para reunir tuplas de metadatos

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
                if (anio <= current_year) & (mes <= current_month-2):
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
                        MiLinajeExt.tamano_zip = os.path.getsize(dir_name+name_to_zip+str(anio)+"_"+str(mes)+".zip")
                        #MiLinajeExt.tamano_zip = my_bucket.Object(key="RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip").content_length

                        # Recolectamos status para metadatos
                        MiLinajeExt.task_status = "Successfull"

                        # Insertamos metadatos a DB
                        print(MiLinajeExt.to_upsert())
                        meta_extract.append(MiLinajeExt.to_upsert())
                        #EL_metadata(MiLinajeExt.to_upsert())

        # Escritura de csv para carga de metadatos
        df = pd.DataFrame(meta_extract, columns=["fecha","nombre_task","year","month","usuario","ip_ec2","tamano_zip","nombre_archivo","ruta_s3","task_status"])
        df.to_csv("metadata/extract_metadata.csv",index=False,header=False)

        os.system('echo "ok" >target/load_ok.txt')

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

        os.system('echo OK > target/extract_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "target/extract_ok.txt"
        return luigi.LocalTarget(output_path)
