from luigi.contrib.postgres import CopyToTable
import pandas as pd
import luigi
import psycopg2

import io
import psycopg2
import psycopg2.extras
from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)


# ===============================
# Clases para reunir metadatos
# ===============================

## Clase para reunir los metadatos de la etapa Raw (tabla metadatos.raw)
class Linaje_raw():
    def __init__(self, url = 0, fecha=0, year=0, month=0, usuario=0, ip_ec2=0,\
     tamano_zip=0, nombre_archivo=0, ruta_s3=0,task_status=0):
        self.url = url
        self.fecha = fecha # time stamp
        self.nombre_task = self.__class__.__name__#nombre_task
        self.year = year #
        self.month = month #
        self.usuario = usuario # Usuario de la maquina de GNU/Linux que corre la instancia
        self.ip_ec2 = ip_ec2
        self.tamano_zip = tamano_zip
        self.nombre_archivo = nombre_archivo
        self.ruta_s3= ruta_s3
        self.task_status= task_status

    def to_upsert(self):
        return (self.fecha, self.nombre_task, self.year, self.month, self.usuario,\
         self.ip_ec2, self.tamano_zip, self.nombre_archivo, self.ruta_s3,\
          self.task_status)

## Clase para reunir los metadatos de la etapa load (tabla metadatos.load)
class Linaje_load():
    def __init__(self, fecha=0, usuario=0, ip_ec2=0,\
     tamano_csv=0, nombre_archivo=0, num_columnas=0,num_renglones=0):
        self.fecha = fecha # time stamp
        self.nombre_task = self.__class__.__name__#nombre_task
        self.usuario = usuario # Usuario de la maquina de GNU/Linux que corre la instancia
        self.ip_ec2 = ip_ec2
        self.tamano_csv = tamano_csv
        self.nombre_archivo = nombre_archivo
        self.num_columnas = num_columnas
        self.num_renglones = num_renglones

    def to_upsert(self):
        return (self.fecha, self.nombre_task, self.usuario,\
         self.ip_ec2, self.tamano_csv, self.nombre_archivo, self.num_columnas,\
          self.num_renglones)

# Clase para reunir los metadatos de la etapa de limpieza de datos (tabla metadatos.clean)
class Linaje_clean_data():
    def __init__(self, fecha=0, nombre_task=0, usuario=0, ip_clean=0, num_columnas_modificadas=0,num_filas_modificadas=0, variables_limpias=0, task_status=0):
        self.fecha = fecha # time stamp
        self.nombre_task = self.__class__.__name__#nombre_task
        self.usuario = usuario # Usuario de la maquina de GNU/Linux que corre la instancia
        self.ip_clean = ip_clean #Corresponde a la dirección IP desde donde se ejecuto la tarea
        self.num_columnas_modificadas = num_columnas_modificadas #    número de columnas modificados
        self.num_filas_modificadas = num_filas_modificadas #    número de registros modificados
        self.variables_limpias = variables_limpias #variables limpias con las que se pasará a la siguiente parte
        self.task_status = "Successful" # estatus de ejecución: Fallido, exitoso, etc.

    def to_upsert(self):
        return (self.fecha, self.nombre_task, self.usuario,\
         self.ip_clean, self.num_columnas_modificadas,self.num_filas_modificadas, self.variables_limpias,\
          self.task_status)

# ==========================================
# Funciones para insertar metadatos a RDS
# ==========================================


def Insert_to_RDS(data_file, nombre_esquema, nombre_tabla):
    '''
    Funcion para insertar metadatos a una tabla y esquema del RDS desde un data_file (por ejemplo, un csv)
    '''

    conn = psycopg2.connect(database= MY_DB,
    	user=MY_USER,
    	password=MY_PASS,
    	host=MY_HOST,
    	port='5432')


    with conn.cursor() as cursor:
    	print('nombre_tabla: ' + nombre_tabla)

    	#Query
    	sql_statement = f"copy "+ nombre_esquema + "." + nombre_tabla + " from stdin with csv delimiter as ','"
    	print(sql_statement)
    	buffer = io.StringIO()

    	with open(data_file,'r') as data:
    		buffer.write(data.read())
    		buffer.seek(0)
    		cursor.copy_expert(sql_statement, file=buffer)

    return print("Insertion in "+ nombre_esquema + "." + nombre_tabla + " is done!!")



class InsertExtractMetada(CopyToTable):
    '''
    Task de luigi para insertar renglones en renglones en tabla de metadatos
    de la extraccion y load de metadatos a S3 (no usada)
    '''

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
        r = [MiLinaje.to_upsert()]

        # Insertamos renglones en tabla
        for element in r:
            yield element

def EL_verif_query(url,anio,mes):
    '''
    Funcion para verificar si cierto month y year ya estan en metadatos.extract
    considerando el tamanio resultante de un query
    '''
    import psycopg2
    import psycopg2.extras
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para verificacion a la base de datos
    postgreSQL_select_Query = "SELECT * from metadatos.extract WHERE year = '" + str(anio) + "' AND month = '"+ str(mes)+"';"
    cursor.execute(postgreSQL_select_Query)
    #print("Query de verificacion "+str(anio)+"/"+"str(mes)")
    select_Query = cursor.fetchall()
    tam = len(select_Query)
    cursor.close()
    connection.close()
    #print("PostgreSQL connection is closed")

    return tam

def load_verif_query():
    '''
    Funcion para verificar si cierto month y year ya estan en metadatos.extract
    considerando el tamanio resultante de un query
    '''
    import psycopg2
    import psycopg2.extras
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para verificacion a la base de datos
    postgreSQL_select_Query = """SELECT count(*) from metadatos.load;"""
    cursor.execute(postgreSQL_select_Query)
    #print("Query de verificacion "+str(anio)+"/"+"str(mes)")
    select_Query = cursor.fetchall()
    tam = len(select_Query)
    cursor.close()
    connection.close()

    return tam


def rita_light_query():
    '''
    Crea una base raw de rita para prueba
    '''
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para verificacion a la base de datos
    postgreSQL_select_Query = """CREATE TABLE raw.rita_light AS (SELECT * FROM raw.rita LIMIT 1000);"""
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    cursor.close()
    connection.close()
    #print("PostgreSQL connection is closed")

    return print("raw.rita_light ha sido creada")


def EL_metadata(record_to_insert):
    '''
    Funcion para insertar metadatos de cierto month y year a metados.extract
    '''
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para insertar metadatos
    postgres_insert_query = """ INSERT INTO metadatos.extract (fecha, nombre_task,\
     year, month, usuario, ip_ec2, tamano_zip, nombre_archivo, ruta_s3, \
     task_status) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) """
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    cursor.close()
    connection.close()

    return print("Metadadata Insertion Done - PostgreSQL connection is closed")


def EL_load(record_to_insert):
    '''
    Funcion auxiliar para insertar a metadatos.load
    '''
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para insertar metadatos
    postgres_insert_query = """ INSERT INTO metadatos.load (fecha, nombre_task,\
     usuario, ip_ec2, tamano_csv, nombre_archivo, num_columnas, \
     num_renglones) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s) """
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    cursor.close()
    connection.close()

    return print("metadatos.load insertion Done - PostgreSQL connection is closed")

def clean_metadata_rds(record_to_insert):
    '''
    Funcion para insertar metadatos de cierto month y year a metados.extract
    '''
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para insertar metadatos
    postgres_insert_query = """ INSERT INTO metadatos.clean (fecha, nombre_task,\
     usuario, ip_ec2, num_columnas_modificadas, num_filas_modificadas, variables_limpias, \
     task_status) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s) """
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    cursor.close()
    connection.close()

    return print("Metadadata Insertion Done - PostgreSQL connection is closed")



#-------------------------------------------------------------------------------------------------------------

# Preparamamos una clase para reunir los metadatos de la etapa Raw
class Linaje_semantic():
    def __init__(self, num_filas_modificadas=0, fecha=0, nombre_task=0, usuario=0, year=0, month=0, ip_ec2=0, variables=0, ruta_s3=0, task_status=0):
        self.num_filas_modificadas = num_filas_modificadas
        self.fecha = fecha # time stamp
        self.nombre_task =  "self.__class__.__name__"#nombre_task
        self.usuario = usuario # Usuario de la maquina de GNU/Linux que corre la instancia
        self.year = year #
        self.month = month #
        self.ip_ec2 = ip_ec2
        self.variables = variables
        self.ruta_s3= ruta_s3
        self.task_status= task_status

    def to_upsert(self):
        return (str(self.num_filas_modificadas), str(self.fecha), str(self.nombre_task), str(self.usuario), str(self.year), str(self.month), str(self.ip_ec2), str(self.variables), str(self.ruta_s3), str(self.task_status))

def semantic_metadata(record_to_insert):
    '''
    Funcion para insertar metadatos de cierto month y year a metados.extract
    '''
    # Conexion y cursor para query
    connection = psycopg2.connect(user = MY_USER, # Usuario RDS
                                 password = MY_PASS, # password de usuario de RDS
                                 host = MY_HOST,# endpoint
                                 port="5432", # cambiar por el puerto
                                 database=MY_DB) # Nombre de la base de datos
    cursor = connection.cursor()

    # Query para insertar metadatos
    postgres_insert_query = """ INSERT INTO metadatos.semantic  VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
    cursor.execute(postgres_insert_query, record_to_insert)
    connection.commit()
    cursor.close()
    connection.close()

    return print("Metadadata Insertion Done - PostgreSQL connection is closed")
