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
from src.models.train_model import run_model
from src.models.save_model import parse_filename
from src.utils.metadatos_utils import Linaje_extract_testing, EL_testing_extract
from src.utils.metadatos_utils import Linaje_load_testing, EL_testing_load

# Inicializa la clase que reune los metadatos
MiLinajeExt = Linaje_raw() # extract y load
# ===============================
CURRENT_DIR = os.getcwd()
# ===============================s
# Tasks de Luigi

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

                        ##Escribimos el archivo descargado al bucket
                        # Autenticación en S3 con boto3
                        ses = boto3.session.Session(profile_name='dpa', region_name='us-east-1')
                        s3_resource = ses.resource('s3')
                        obj = s3_resource.Bucket("test-aws-boto")
                        print(ses)

                        #Escritura
                        output_path = "RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip"
                        dir_name="./src/data/"
                        name_to_zip = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

                        obj.upload_file(dir_name+name_to_zip+str(anio)+"_"+str(mes)+".zip", output_path)

                        # Recolectamos nombre del .zip y path con el que se guardara consulta a
                        # API de Rita en S3 para metadatos
                        MiLinajeExt.ruta_s3 = "s3://test-aws-boto/"+"RITA/YEAR="+str(anio)+"/"
                        MiLinajeExt.nombre_archivo =  str(anio)+"_"+str(mes)+".zip"

                        # Recolectamos tamano del archivo recien escrito en S3 para metadatos
                        ses = boto3.session.Session(profile_name="dpa", region_name='us-east-1')
                        s3 = ses.resource('s3')
                        bucket_name = "test-aws-boto"
                        my_bucket = s3.Bucket(bucket_name)
                        MiLinajeExt.tamano_zip = my_bucket.Object(key="RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip").content_length

                        # Recolectamos status para metadatos
                        MiLinajeExt.task_status = "Successful"

                        # Insertamos metadatos a DB
                        print(MiLinajeExt.to_upsert())
                        EL_metadata(MiLinajeExt.to_upsert())


        os.system('echo OK > extract_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "extract_ok.txt"
        return luigi.LocalTarget(output_path)

MiLinaje = Linaje_load()

class Load(luigi.Task):
    '''
    Carga hacia RDS los datos de la carpeta data
    '''
    #def requires(self):
        #return Extract()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MiLinaje.fecha =  datetime.now()
    MiLinaje.usuario = getpass.getuser()

    def run(self):
        # Ip metadatos
        MiLinaje.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

        # Unzips de archivos csv

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
                #os.remove(dir_name+'readme.html')

        #Subimos de archivos csv
        extension_csv = ".csv"

        #Cantidad de renglones en metadatos.load
        tam0 = load_verif_query()
        cantidad_csv_insertados=0

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
                    os.remove(dir_name+item)

                    EL_load(MiLinaje.to_upsert())
                    cantidad_csv_insertados=cantidad_csv_insertados+1
                except:
                    print("Error en carga de "+item)

        #Cantidad de renglones en metadatos.load
        tam1 = load_verif_query()

        os.system('echo "ok" >load_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "load_ok.txt"
        return luigi.LocalTarget(output_path)

#-----------------------------------------------------------------------------------------------------------------------------
# Limpiar DATOS
CURRENT_DIR = os.getcwd()

#Limpiamos los datos
class GetCleanData(luigi.Task):

	def requires(self):
		return Load()

	def output(self):
		dir = CURRENT_DIR + "/target/data_clean.txt"
		return luigi.local_target.LocalTarget(dir)

	def run(self):
		clean()

		z = "Limpia Datos"
		with self.output().open('w') as output_file:
			output_file.write(z)

#-----------------------------------------------------------------------------------------------------------------------------
#FEATURE ENGINERING------------------------------------------------------------------------------------------------------------
# Crear caracteristicas DATOS
CURRENT_DIR = os.getcwd()


#metadata FE
MiLinajeSemantic = Linaje_semantic()

#Creamos features nuevas
class GetFEData(luigi.Task):

	def requires(self):
		return GetCleanData()

	def output(self):
		dir = CURRENT_DIR + "/target/data_semantic.txt"
		return luigi.local_target.LocalTarget(dir)

	def run(self):
		df_util = crear_features()#CACHE.get_clean_data()

		MiLinajeSemantic.ip_ec2 = str(df_util.count())
		MiLinajeSemantic.fecha =  str(datetime.now())
		MiLinajeSemantic.nombre_task = 'GetFEData'
		MiLinajeSemantic.usuario = str(getpass.getuser())
		MiLinajeSemantic.year = str(datetime.today().year)
		MiLinajeSemantic.month = str(datetime.today().month)
		MiLinajeSemantic.ip_ec2 =  str(socket.gethostbyname(socket.gethostname()))
		MiLinajeSemantic.variables = "findesemana,quincena,dephour,seishoras"
		MiLinajeSemantic.ruta_s3 = "s3://test-aws-boto/semantic"
		MiLinajeSemantic.task_status = 'Successful'
		# Insertamos metadatos a DB
		print(MiLinajeSemantic.to_upsert())
		semantic_metadata(MiLinajeSemantic.to_upsert())
		## Inserta archivo y elimina csv
		#os.system('bash ./src/utils/inserta_semantic_rita_to_rds.sh')
		#os.system('rm semantic.csv')

		z = "CreaFeaturesDatos"
		with self.output().open('w') as output_file:
			output_file.write(z)


# ------------------- MODELLING ----------------------------
#--bucname models-dpa --numIt 1 --numPCA 2 --obj 0-1.5 --model LR

class CreateModelBucket(luigi.Task):
	bucname = luigi.Parameter()
	def requires():
		return GetFEData()

	def output(self):
		dir = CURRENT_DIR + "/target/create_s3_" + str(self.bucname) + ".txt"
		return luigi.local_target.LocalTarget(dir)

	def run(self):
		create_bucket(str(self.bucname))
		z = str(self.bucname)
		with self.output().open('w') as output_file:
			output_file.write(z)


class RunModel(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	obj = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return GetFEData()

	def output(self):
		objetivo = self.obj
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = self.obj
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)


# =======================================================
# ALL TARGETS
# 1) "0-1.5"
# 2) "1.5-3.5"
# 3) "3.5-"
# 4) "cancelled"
# =======================================================
TARGET_A = "0-1.5"
TARGET_B = "1.5-3.5"
TARGET_C =  "3.5-"
TARGET_D = "cancelled"

class RunAllTargets(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return CreateModelBucket(self.bucname), \
		 RunTargetA(self.bucname, self.numIt, self.numPCA, self.model), \
		 RunTargetB(self.bucname,self.numIt, self.numPCA, self.model), \
		 RunTargetC(self.bucname,self.numIt, self.numPCA, self.model), \
		 RunTargetD(self.bucname,self.numIt, self.numPCA, self.model)

	def output(self):
		dir = CURRENT_DIR + "/target/run_all_models.txt"
		return luigi.local_target.LocalTarget(dir)

	def run(self):
		z = str(TARGET_A) + "_" + str(TARGET_D)
		with self.output().open('w') as output_file:
			output_file.write(z)

class RunTargetA(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return GetFEData()

	def output(self):
		objetivo = TARGET_A
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = TARGET_A
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)

class RunTargetB(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return GetFEData()

	def output(self):
		objetivo = TARGET_B
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = TARGET_B
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)

class RunTargetC(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return GetFEData()

	def output(self):
		objetivo = TARGET_C
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = TARGET_C
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)


class RunTargetD(luigi.Task):
	bucname = luigi.Parameter()
	numIt = luigi.Parameter()
	numPCA = luigi.Parameter()
	model = luigi.Parameter()

	def requires(self):
		return GetFEData()

	def output(self):
		objetivo = TARGET_D
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = TARGET_D
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)
