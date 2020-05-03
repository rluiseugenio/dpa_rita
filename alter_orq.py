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
import os
import pandas as pd
import psycopg2
from psycopg2 import extras
from zipfile import ZipFile

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
from src.utils.metadatos_utils import EL_verif_query, EL_metadata, Linaje_raw,EL_rawdata,clean_metadata_rds,Linaje_clean_data, Linaje_semantic, semantic_metadata, Insert_to_RDS, rita_light_query
from src.utils.db_utils import execute_sql
from src.models.train_model import run_model
from src.models.save_model import parse_filename

# Inicializa la clase que reune los metadatos
MiLinaje = Linaje_raw() # extract y load
# ===============================
CURRENT_DIR = os.getcwd()
# ===============================s
# Tasks de Luigi

class Extract(luigi.Task):
	'''
	Descarga en zip los datos de Rita (encarpeta data)
	'''
	#def requires(self):
	#    return Create_Tables_Schemas()

	#Definimos los URL base para poder actualizarlo automaticamente despues
	BASE_URL="https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

	# Recolectamos fecha y usuario para metadatos a partir de fecha actual
	MiLinaje.fecha =  datetime.now()
	MiLinaje.usuario = getpass.getuser()

	def run(self):

		# Obtiene anio y mes correspondiente fecha actual de ejecucion del script
		now = datetime.now()
		current_year = now.year
		current_month = now.month

		# Obtiene anio y mes base (tres anios hacia atras)
		base_year = current_year - 0
		base_month = current_month

		# Recolectamos IP para metadatos
		MiLinaje.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

		for anio in range(base_year,current_year+1):
			for mes in range(1,12+1):

				# Recolectamos parametros de mes y anio de solicitud descarga a API Rita para metadatos
				MiLinaje.year = str(anio)
				MiLinaje.month = str(mes)

				# Verificamos si en metadatos ya hay registro de esta anio y mes
				# En caso contario, se intenta descarga

				if (anio <= current_year) & (mes <= current_month):

					#URL para hacer peticion a API rita en anio y mes indicado
					url_act = self.BASE_URL+str(anio)+"_"+str(mes)+".zip" #url actualizado
					tam = EL_verif_query(url_act,anio,mes)

					# Intentamos descargar los datos
					r=requests.get(url_act)

					if tam == 0 & r.status_code == 200:
						#Descargamos los datos desde la API, en formato zip del periodo en cuestion

						print("Carga: " +str(anio)+" - "+str(mes))

						## Escribimos los archivos que se consultan al API Rita en S3
						# Autenticación en S3 con boto3
						#ses = boto3.session.Session(profile_name='dpa', region_name='us-east-1')
						#s3_resource = ses.resource('s3')
						#obj = s3_resource.Bucket("test-aws-boto")
						#print(ses)

						# Escribimos el archivo al bucket, usando el binario
						#output_path = "RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip"
						#obj.put_object(Key=output_path,Body=r.content)

						# Recolectamos nombre del .zip y path con el que se guardara consulta a
						# API de Rita en S3 para metadatos
						MiLinaje.ruta_s3 = "s3://test-aws-boto/"+"RITA/YEAR="+str(anio)+"/"
						MiLinaje.nombre_archivo =  str(anio)+"_"+str(mes)+".zip"

						# Escribimos el zip a data
						with open(str(anio)+"_"+str(mes)+".zip", 'wb') as f:
							f.write(r.content)

						# Recolectamos tamano del archivo recien escrito en S3 para metadatos
						#ses = boto3.session.Session(profile_name="dpa", region_name='us-east-1')
						#s3 = ses.resource('s3')
						#bucket_name = "test-aws-boto"
						#my_bucket = s3.Bucket(bucket_name)
						#MiLinaje.tamano_zip = my_bucket.Object(key="RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip").content_length

						# Recolectamos tatus para metadatos
						MiLinaje.task_status = "Successful"

						# Insertamos metadatos a DB
						EL_metadata(MiLinaje.to_upsert())

		os.system('echo OK > ./data/extract_ok.txt')

	def output(self):
		# Ruta en donde se guarda el archivo solicitado
		output_path = "./data/extract_ok.txt"
		return luigi.LocalTarget(output_path)

class Load(luigi.Task):
    '''
    Carga hacia RDS los datos de la carpeta data
    '''
    def requires(self):
        return Extract()

    def run(self):
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

        for item in os.listdir(dir_name):
            if item.endswith(extension_csv):
                table_name = "raw.rita"

                try:
                    print(item)
                    save_rds(dir_name+item, table_name)
                    os.remove(dir_name+item)
                except:
                    print("Error en carga de "+item)

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
