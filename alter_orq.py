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

# Inicializa la clase que reune los metadatos
MiLinajeExt = Linaje_raw() # extract y load
# ===============================
CURRENT_DIR = os.getcwd()
# ===============================s
# Tasks de Luigi

# ======================================================
# Etapa Extract
# ======================================================

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
                        MiLinajeExt.task_status = "Successful"

                        # Insertamos metadatos a DB
                        print(MiLinajeExt.to_upsert())
                        EL_metadata(MiLinajeExt.to_upsert())

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

        os.system('echo OK > extract_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "extract_ok.txt"
        return luigi.LocalTarget(output_path)

# ======================================================
# Prueba unitaria de la etapa load
# ======================================================

from testing.test_absent_hearders import TestingHeaders
MetadatosLoadTesting = Linaje_load_testing()

class Load_Testing(luigi.Task):
    '''
    Prueba unitaria de estructura de archivos descargados
    '''
    def requires(self):
        return Extraction()

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

        os.system('echo "ok"> testing_load_ok.txt')

    def output(self):
        output_path='testing_load_ok.txt'
        return luigi.LocalTarget(output_path)

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
# Etapa Load
# ======================================================

MiLinaje = Linaje_load()

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
                    os.remove(dir_name+item)

                    EL_load(MiLinaje.to_upsert())
                    #cantidad_csv_insertados=cantidad_csv_insertados+1
                except:
                    print("Carga de "+item)

        #Cantidad de renglones en metadatos.load
        # tam1 = load_verif_query()

        os.system('echo "ok" >load_ok.txt')

    def output(self):
        # Ruta en donde se guarda el target del task
        output_path = "load_ok.txt"
        return luigi.LocalTarget(output_path)

#-----------------------------------------------------------------------------------------------------------------------------
# ======================================================
# Pruebas unitarias clean
# ======================================================
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




# ======================================================
# Limpieza de datos
# ======================================================
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

# ======================================================
# Pruebas unitarias de la etapa SEMANTIC
# ======================================================

from testing.test_semantic_columns import TestSemanticColumns
MetadatosSemanticTesting = Linaje_semantic1_testing()

#PRUEBA DE MARBLES
class Semantic_Testing_col(luigi.Task):
    '''
    Prueba unitaria de estructura de archivos descargados
    '''
    def requires(self):
        return GetCleanData()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosSemanticTesting.fecha =  datetime.now()
    MetadatosSemanticTesting.usuario = getpass.getuser()

    def run(self):
        # Obtiene anio y mes correspondiente fecha actual de ejecucion del script
        now = datetime.now()

        # Recolectamos parametros de mes y anio de solicitud descarga a API Rita para metadatos_utils
        MetadatosSemanticTesting.year = now.year
        MetadatosSemanticTesting.month = now.month

        unit_test_semantic = TestSemanticColumns()
        unit_test_semantic.test_that_all_columns_are_present()

        os.system('echo "ok"> target/testing_semantic_ok.txt')

    def output(self):
        output_path='target/testing_semantic_ok.txt'
        return luigi.LocalTarget(output_path)

@Semantic_Testing_col.event_handler(Event.SUCCESS)
def on_success(self):
    MetadatosSemanticTesting.msg_error = ""
    MetadatosSemanticTesting.task_status ="Successful"
    print(MetadatosSemanticTesting.to_upsert())
    FE_testing_semantic(MetadatosSemanticTesting.to_upsert())

@Semantic_Testing_col.event_handler(Event.FAILURE)
def on_failure(self,exception):
    MetadatosSemanticTesting.msg_error = "Columnas FE distintas."
    MetadatosSemanticTesting.task_status ="Failure"
    print(MetadatosSemanticTesting.to_upsert())
    FE_testing_semantic(MetadatosSemanticTesting.to_upsert())

#PRUEBA DE pandas
from testing.test_semantic_column_types import TestSemanticColumnsTypes
MetadatosSemanticTestingTypes = Linaje_semantic2_testing()

class Semantic_Testing(luigi.Task):
    '''
    Prueba unitaria de estructura de archivos descargados
    '''
    def requires(self):
        return Semantic_Testing_col()

    # Recolectamos fecha y usuario para metadatos a partir de fecha actual
    MetadatosSemanticTestingTypes.fecha =  datetime.now()
    MetadatosSemanticTestingTypes.usuario = getpass.getuser()

    def run(self):
        # Obtiene anio y mes correspondiente fecha actual de ejecucion del script
        now = datetime.now()

        # Recolectamos parametros de mes y anio de solicitud descarga a API Rita para metadatos_utils
        MetadatosSemanticTestingTypes.year = now.year
        MetadatosSemanticTestingTypes.month = now.month

        unit_test_semantic = TestSemanticColumnsTypes()
        unit_test_semantic.test_all_column_types()

        os.system('echo "ok"> target/testing_pandas_semantic_ok.txt')

    def output(self):
        output_path='target/testing_pandas_semantic_ok.txt'
        return luigi.LocalTarget(output_path)

@Semantic_Testing.event_handler(Event.SUCCESS)
def on_success(self):
    MetadatosSemanticTestingTypes.msg_error = ""
    MetadatosSemanticTestingTypes.task_status ="Successful"
    print(MetadatosSemanticTestingTypes.to_upsert())
    FE_testing_semantic(MetadatosSemanticTestingTypes.to_upsert())

@Semantic_Testing.event_handler(Event.FAILURE)
def on_failure(self,exception):
    MetadatosSemanticTestingTypes.msg_error = "Algunas variables enviadas a modeling tienen su tipo de variable incorrecto."
    MetadatosSemanticTestingTypes.task_status ="Failure"
    print(MetadatosSemanticTestingTypes.to_upsert())
    FE_testing_semantic(MetadatosSemanticTestingTypes.to_upsert())


#-----------------------------------------------------------------------------------------------------------------------------
#FEATURE ENGINERING------------------------------------------------------------------------------------------------------------
# Crear caracteristicas DATOS
CURRENT_DIR = os.getcwd()


#metadata FE
MiLinajeSemantic = Linaje_semantic()

#Creamos features nuevas
class GetFEData(luigi.Task):

	def requires(self):
		return Semantic_Testing()

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
