from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, lower, regexp_replace, split
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType
from src.utils.metadatos_utils import Linaje_clean_data, clean_metadata_rds
from datetime import date, datetime
import getpass
import socket
import requests
import psycopg2
import os
import re
from pyspark.sql.functions import UserDefinedFunction

from pyspark.sql.types import *
from src import (
    MY_USER ,
    MY_PASS ,
    MY_HOST ,
    MY_PORT,
    MY_DB
)


def clean():
    #====================================================================
    # Task: Pasar a minusculas los nombres de columnas
    #====================================================================
    meta_clean = [] # arreglo para reunir tuplas de metadatos
    df = get_raw_data()

    # Inicializa clase para reunir metadatos
    MiLinaje_clean = Linaje_clean_data()

    # Recolectamos fecha, usuario IP, nobre de task para metadatos
    MiLinaje_clean.fecha =  datetime.now()
    MiLinaje_clean.nombre_task = "Colnames_to_lower"
    MiLinaje_clean.usuario = getpass.getuser()
    MiLinaje_clean.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

    MiLinaje_clean.variables_limpias = "All_from_raw data"

    counting_cols = 0

    for col in df.columns:
        counting_cols = counting_cols +1
        df = df.withColumnRenamed(col, col.lower())

    # Metadadatos de columnas o registros modificados
    MiLinaje_clean.num_columnas_modificadas = counting_cols
    MiLinaje_clean.variables_limpias = counting_cols

    # Subimos los metadatos al RDS
    #clean_metadata_rds(MiLinaje_clean.to_upsert())
    meta_clean.append(MiLinaje_clean.to_upsert())

    #====================================================================
    # Task: Seleccionar columnas no vacias
    #====================================================================

    # Inicializa clase para reunir metadatos
    Mi_Linaje_clean = Linaje_clean_data()

    # Recolectamos fecha, usuario IP, nobre de task para metadatos
    MiLinaje_clean.fecha =  datetime.now()
    MiLinaje_clean.nombre_task = "Colnames_selection"
    MiLinaje_clean.usuario = getpass.getuser()
    MiLinaje_clean.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

    # Seleccion de columnas
    n0 = len(df.columns)

    base = df.select(df.year,df.quarter, df.month, df.dayofmonth, df.dayofweek, df.flightdate, df.reporting_airline, df.dot_id_reporting_airline, df.iata_code_reporting_airline, df.tail_number, df.flight_number_reporting_airline, df.originairportid, df.originairportseqid, df.origincitymarketid, df.origin, df.origincityname, df.originstate, df.originstatefips, df.originstatename, df.originwac, df.destairportid, df.destairportseqid, df.destcitymarketid, df.dest, df.destcityname, df.deststate, df.deststatefips, df.deststatename, df.destwac, df.crsdeptime, df.deptime, df.depdelay, df.depdelayminutes, df.depdel15, df.departuredelaygroups, df.deptimeblk, df.taxiout, df.wheelsoff, df.wheelson, df.taxiin, df.crsarrtime, df.arrtime, df.arrdelay, df.arrdelayminutes, df.arrdel15, df.arrivaldelaygroups, df.arrtimeblk, df.cancelled, df.diverted, df.crselapsedtime, df.actualelapsedtime, df.airtime, df.flights, df.distance, df.distancegroup, df.divairportlandings )

    n1 = len(base.columns)

    # Metadadatos de columas o registros modificados
    MiLinaje_clean.num_columnas_modificadas = n1 - n0
    MiLinaje_clean.variables_limpias = "year,quarter, month, dayofmonth, dayofweek,\
     flightdate, reporting_airline, dot_id_reporting_airline, iata_code_reporting_airline,\
     tail_number, flight_number_reporting_airline, originairportid, originairportseqid,\
     origincitymarketid, origin, origincityname, originstate, originstatefips, originstatename,\
     originwac, destairportid, destairportseqid, destcitymarketid, dest, destcityname, deststate,\
     deststatefips, deststatename, destwac, crsdeptime, deptime, depdelay, depdelayminutes,\
     depdel15, departuredelaygroups, deptimeblk, taxiout, wheelsoff, wheelson, taxiin, crsarrtime,\
     arrtime, arrdelay, arrdelayminutes, arrdel15, arrivaldelaygroups, arrtimeblk, cancelled,\
     diverted, crselapsedtime, actualelapsedtime, airtime, flights, distance, distancegroup,\
     divairportlandings"

    # Subimos los metadatos al RDS
    #clean_metadata_rds(MiLinaje_clean.to_upsert())
    meta_clean.append(MiLinaje_clean.to_upsert())

    #========================================================================================================
    # agregar columna con clasificación de tiempo en horas de atraso del vuelo 0-1.5, 1.5-3.5,3.5-, cancelled
    #========================================================================================================

    # Inicializa clase para reunir metadatos
    Mi_Linaje_clean = Linaje_clean_data()

    # Recolectamos fecha, usuario IP, nobre de task para metadatos
    MiLinaje_clean.fecha =  datetime.now()
    MiLinaje_clean.nombre_task = "creation_of_categories"
    MiLinaje_clean.usuario = getpass.getuser()
    MiLinaje_clean.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

    from pyspark.sql import functions as f

    # Seleccion de columnas
    n0 = len(df.columns)

    base = base.withColumn('rangoatrasohoras', f.when(f.col('cancelled') == 1, "cancelled").when(f.col('depdelayminutes') < 90, "0-1.5").when((f.col('depdelayminutes') > 90) & (f.col('depdelayminutes')<210), "1.5-3.5").otherwise("3.5-"))

    n1 = len(base.columns)

    # Metadadatos de columas o registros modificados
    MiLinaje_clean.num_columnas_modificadas = n1 - n0

    # Metadadatos de columas o registros modificados
    MiLinaje_clean.num_filas_modificadas = df.count()

    MiLinaje_clean.variables_limpias = "year,quarter, month, dayofmonth, dayofweek,\
         flightdate, reporting_airline, dot_id_reporting_airline, iata_code_reporting_airline,\
         tail_number, flight_number_reporting_airline, originairportid, originairportseqid,\
         origincitymarketid, origin, origincityname, originstate, originstatefips, originstatename,\
         originwac, destairportid, destairportseqid, destcitymarketid, dest, destcityname, deststate,\
         deststatefips, deststatename, destwac, crsdeptime, deptime, depdelay, depdelayminutes,\
         depdel15, departuredelaygroups, deptimeblk, taxiout, wheelsoff, wheelson, taxiin, crsarrtime,\
         arrtime, arrdelay, arrdelayminutes, arrdel15, arrivaldelaygroups, arrtimeblk, cancelled,\
         diverted, crselapsedtime, actualelapsedtime, airtime, flights, distance, distancegroup,\
         divairportlandings,rangoatrasohoras,cancelled,0-1.5,1.5-3.5,3.5-"

    # Subimos los metadatos al RDS
    #clean_metadata_rds(MiLinaje_clean.to_upsert())
    meta_clean.append(MiLinaje_clean.to_upsert())

    #===================================================================
    # Aplicación de la función limpieza texto
    #===================================================================

    # Función limpiar texto: minúsculas, espacios por guiones, split
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    from pyspark.sql.functions import col, lower, regexp_replace, split

    def clean_text(c):
        c = lower(c)
        c = regexp_replace(c, " ", "_")
        c = f.split(c, '\,')[0]
        return c

    # Inicializa clase para reunir metadatos
    Mi_Linaje_clean = Linaje_clean_data()

    # Recolectamos fecha, usuario IP, nobre de task para metadatos
    MiLinaje_clean.fecha =  datetime.now()
    MiLinaje_clean.nombre_task = "cleaning_text_spaces_and_others"
    MiLinaje_clean.usuario = getpass.getuser()
    MiLinaje_clean.ip_ec2 = str(socket.gethostbyname(socket.gethostname()))

    string_cols = [item[0] for item in base.dtypes if item[1].startswith('string')]
    for x in string_cols:
        base = base.withColumn(x, clean_text(col(x)))

    # Metadadatos de columas o registros modificados
    MiLinaje_clean.num_filas_modificadas = df.count()
    MiLinaje_clean.num_columnas_modificadas = len(df.columns)

    MiLinaje_clean.variables_limpias = "year,quarter, month, dayofmonth, dayofweek,\
             flightdate, reporting_airline, dot_id_reporting_airline, iata_code_reporting_airline,\
             tail_number, flight_number_reporting_airline, originairportid, originairportseqid,\
             origincitymarketid, origin, origincityname, originstate, originstatefips, originstatename,\
             originwac, destairportid, destairportseqid, destcitymarketid, dest, destcityname, deststate,\
             deststatefips, deststatename, destwac, crsdeptime, deptime, depdelay, depdelayminutes,\
             depdel15, departuredelaygroups, deptimeblk, taxiout, wheelsoff, wheelson, taxiin, crsarrtime,\
             arrtime, arrdelay, arrdelayminutes, arrdel15, arrivaldelaygroups, arrtimeblk, cancelled,\
             diverted, crselapsedtime, actualelapsedtime, airtime, flights, distance, distancegroup,\
             divairportlandings,rangoatrasohoras,cancelled,0-1.5,1.5-3.5,3.5-"

    # Subimos los metadatos al RDS
    #clean_metadata_rds(MiLinaje_clean.to_upsert())
    meta_clean.append(MiLinaje_clean.to_upsert())

    datos_clean = pd.DataFrame(meta_clean, columns=["fecha",\
    "nombre_task","usuario","ip_ec2","num_columnas_modificadas","num_filas_modificadas",\
    "variables_limpias","task_status"])
    datos_clean.to_csv("metadata/clean_metadata.csv",index=False,header=False)

    base.show(2)
    print((base.count(), len(base.columns)))
    # Guardamos los DATOS
    save_rds(base,"clean.rita")
    return base


def save_rds(base, table_name):
    #base.coalesce(1).write.option("header", "false").csv("aux.csv")
    df_pandas = base.toPandas()
    if table_name == "semantic.rita":
        df_pandas = df_pandas.replace(to_replace = "", value ="null")
        df_pandas = df_pandas.replace(to_replace = "None", value ="null")
    df_pandas.iloc[1:].to_csv('aux.csv', index = False, header = False, na_rep = "null")
    # ---------------------------
    # Copy to postgres
    connection = psycopg2.connect(user=MY_USER , # Usuario RDS
                                 password=MY_PASS, # password de usuario de RDS
                                 host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                 port=MY_PORT, # cambiar por el puerto
                                 database=MY_DB ) # Nombre de la base de datos
    cursor = connection.cursor()

    file_name = "aux.csv"
    f = open(file_name, 'r')
    cursor.copy_from(f, table_name, sep=',', null = "null")
    f.close()

    connection.commit()
    cursor.close()
    connection.close()

    #Delete auxilary file
    os.remove("aux.csv")


def get_raw_data():

   schema = StructType([StructField('year', StringType(), True),
					 StructField('quarter', StringType(), True),
                     StructField('month', StringType(), True),
                     StructField('dayofmonth', StringType(), True),
                     StructField('dayofweek', StringType(), True),
                     StructField('flightdate', StringType(), True),
                     StructField('reporting_airline', StringType(), True),
                     StructField('dot_id_reporting_airline', StringType(), True),
                     StructField('iata_code_reporting_airline', StringType(), True),
                     StructField('tail_number', StringType(), True),
                     StructField('flight_number_reporting_airline', StringType(), True),
                     StructField('originairportid', StringType(), True),
                     StructField('originairportseqid', StringType(), True),
                     StructField('origincitymarketid', StringType(), True),
                     StructField('origin', StringType(), True),
                     StructField('origincityname', StringType(), True),
                     StructField('originstate', StringType(), True),
                     StructField('originstatefips', StringType(), True),
                     StructField('originstatename', StringType(), True),
                     StructField('originwac', StringType(), True),
                     StructField('destairportid', StringType(), True),
                     StructField('destairportseqid', StringType(), True),
                     StructField('destcitymarketid', StringType(), True),
                     StructField('dest', StringType(), True),
                     StructField('destcityname', StringType(), True),
                     StructField('deststate', StringType(), True),
                     StructField('deststatefips', StringType(), True),
                     StructField('deststatename', StringType(), True),
                     StructField('destwac', StringType(), True),
                     StructField('crsdeptime', StringType(), True),
                     StructField('deptime', StringType(), True),
                     StructField('depdelay', StringType(), True),
                     StructField('depdelayminutes', StringType(), True),
                     StructField('depdel15', StringType(), True),
                     StructField('departuredelaygroups', StringType(), True),
                     StructField('deptimeblk', StringType(), True),
                     StructField('taxiout', StringType(), True),
                     StructField('wheelsoff', StringType(), True),
                     StructField('wheelson', StringType(), True),
                     StructField('taxiin', StringType(), True),
                     StructField('crsarrtime', StringType(), True),
                     StructField('arrtime', StringType(), True),
                     StructField('arrdelay', StringType(), True),
                     StructField('arrdelayminutes', StringType(), True),
                     StructField('arrdel15', StringType(), True),
                     StructField('arrivaldelaygroups', StringType(), True),
                     StructField('arrtimeblk', StringType(), True),
                     StructField('cancelled', StringType(), True),
                     StructField('cancellationcode', StringType(), True),
                     StructField('diverted', StringType(), True),
                     StructField('crselapsedtime', StringType(), True),
                     StructField('actualelapsedtime', StringType(), True),
                     StructField('airtime', StringType(), True),
                     StructField('flights', StringType(), True),
                     StructField('distance', StringType(), True),
                     StructField('distancegroup', StringType(), True),
                     StructField('carrierdelay text', StringType(), True),
                     StructField('weatherdelay text', StringType(), True),
                     StructField('nasdelay text', StringType(), True),
                     StructField('securitydelay text', StringType(), True),
                     StructField('lateaircraftdelay text', StringType(), True),
                     StructField('firstdeptime', StringType(), True),
                     StructField('totaladdgtime', StringType(), True),
                     StructField('longestaddgtime', StringType(), True),
                     StructField('divairportlandings', StringType(), True),
                     StructField('divreacheddest', StringType(), True),
                     StructField('divactualelapsedtime ', StringType(), True),
                     StructField('divarrdelay', StringType(), True),
                     StructField('divdistance', StringType(), True),
                     StructField('div1airport', StringType(), True),
                     StructField('div1airportid', StringType(), True),
                     StructField('div1airportseqid', StringType(), True),
                     StructField('div1wheelson', StringType(), True),
                     StructField('div1totalgtime', StringType(), True),
                     StructField('div1longestgtime', StringType(), True),
                     StructField('div1wheelsoff', StringType(), True),
                     StructField('div1tailnum', StringType(), True),
                     StructField('div2airport', StringType(), True),
                     StructField('div2airportid', StringType(), True),
                     StructField('div2airportseqid', StringType(), True),
                     StructField('div2wheelson', StringType(), True),
                     StructField('div2totalgtime', StringType(), True),
                     StructField('div2longestgtime', StringType(), True),
                     StructField('div2wheelsoff', StringType(), True),
                     StructField('div2tailnum', StringType(), True),
                     StructField('div3airport', StringType(), True),
                     StructField('div3airportid', StringType(), True),
                     StructField('div3airportseqid', StringType(), True),
                     StructField('div3wheelson', StringType(), True),
                     StructField('div3totalgtime', StringType(), True),
                     StructField('div3longestgtime', StringType(), True),
                     StructField('div3wheelsoff', StringType(), True),
                     StructField('div3tailnum', StringType(), True),
                     StructField('div4airport', StringType(), True),
                     StructField('div4airportid', StringType(), True),
                     StructField('div4airportseqid', StringType(), True),
                     StructField('div4wheelson', StringType(), True),
                     StructField('div4totalgtime', StringType(), True),
                     StructField('div4longestgtime', StringType(), True),
                     StructField('div4wheelsoff', StringType(), True),
                     StructField('div4tailnum', StringType(), True),
                     StructField('div5airport', StringType(), True),
                     StructField('div5airportid', StringType(), True),
                     StructField('div5airportseqid', StringType(), True),
                     StructField('div5wheelson', StringType(), True),
                     StructField('div5totalgtime', StringType(), True),
                     StructField('div5longestgtime', StringType(), True),
                     StructField('div5wheelsoff', StringType(), True),
                     StructField('div5tailnum', StringType(), True),
                     StructField('fffff', StringType(), True)
                     ])

   config_psyco = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(MY_HOST,MY_DB,MY_USER,MY_PASS)
   connection = pg.connect(config_psyco)
   pdf = pd.read_sql_query('select * from raw.rita order by random() limit 15000;',con=connection)
   spark = SparkSession.builder.config('spark.driver.extraClassPath', 'postgresql-9.4.1207.jar').getOrCreate()
   df = spark.createDataFrame(pdf, schema=schema)
   return df




#FEATURE ENGINEERING ------------------------------------------
def get_clean_data():
    clean_rita = StructType([StructField('year', StringType(), True),
                             StructField('quarter', StringType(), True),
                             StructField('month', StringType(), True),
                             StructField('dayofmonth', StringType(), True),
                             StructField('dayofweek', StringType(), True),
                             StructField('flightdate', StringType(), True),
                             StructField('reporting_airline', StringType(), True),
                             StructField('dot_id_reporting_airline', StringType(), True),
                             StructField('iata_code_reporting_airline', StringType(), True),
                             StructField('tail_number', StringType(), True),
                             StructField('flight_number_reporting_airline', StringType(), True),
                             StructField('originairportid', StringType(), True),
                             StructField('originairportseqid', StringType(), True),
                             StructField('origincitymarketid', StringType(), True),
                             StructField('origin', StringType(), True),
                             StructField('origincityname', StringType(), True),
                             StructField('originstate', StringType(), True),
                             StructField('originstatefips', StringType(), True),
                             StructField('originstatename', StringType(), True),
                             StructField('originwac', StringType(), True),
                             StructField('destairportid', StringType(), True),
                             StructField('destairportseqid', StringType(), True),
                             StructField('destcitymarketid', StringType(), True),
                             StructField('dest', StringType(), True),
                             StructField('destcityname', StringType(), True),
                             StructField('deststate', StringType(), True),
                             StructField('deststatefips', StringType(), True),
                             StructField('deststatename', StringType(), True),
                             StructField('destwac', StringType(), True),
                             StructField('crsdeptime', StringType(), True),
                             StructField('deptime', StringType(), True),
                             StructField('depdelay', StringType(), True),
                             StructField('depdelayminutes', StringType(), True),
                             StructField('depdel15', StringType(), True),
                             StructField('departuredelaygroups', StringType(), True),
                             StructField('deptimeblk', StringType(), True),
                             StructField('taxiout', StringType(), True),
                             StructField('wheelsoff', StringType(), True),
                             StructField('wheelson', StringType(), True),
                             StructField('taxiin', StringType(), True),
                             StructField('crsarrtime', StringType(), True),
                             StructField('arrtime', StringType(), True),
                             StructField('arrdelay', StringType(), True),
                             StructField('arrdelayminutes', StringType(), True),
                             StructField('arrdel15', StringType(), True),
                             StructField('arrivaldelaygroups', StringType(), True),
                             StructField('arrtimeblk', StringType(), True),
                             StructField('cancelled', StringType(), True),
                             StructField('diverted', StringType(), True),
                             StructField('crselapsedtime', StringType(), True),
                             StructField('actualelapsedtime', StringType(), True),
                             StructField('airtime', StringType(), True),
                             StructField('flights', StringType(), True),
                             StructField('distance', StringType(), True),
                             StructField('distancegroup', StringType(), True),
                             StructField('divairportlandings', StringType(), True),
                             StructField('rangoatrasohoras', StringType(), True)
                            ])
    config_psyco = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(MY_HOST,MY_DB,MY_USER,MY_PASS)
    connection = pg.connect(config_psyco)
    pdf = pd.read_sql_query('select * from clean.rita;',con=connection)
    spark = SparkSession.builder.config('spark.driver.extraClassPath', 'postgresql-9.4.1207.jar').getOrCreate()
    df = spark.createDataFrame(pdf, schema=clean_rita)

    return df


def crear_features():

    from pyspark.sql import functions as f

    base = get_clean_data()
    udf = UserDefinedFunction(lambda x: re.sub('""','0',str(x)), StringType())
    base = base.select(*[udf(column).alias(column) for column in base.columns])

    base = base.withColumn('findesemana', f.when(f.col('dayofweek') == 5, 1).when(f.col('dayofweek') == 6, 1).when(f.col('dayofweek') == 7, 1).otherwise(0))
    base = base.withColumn('quincena', f.when(f.col('dayofmonth') == 15, 1).when(f.col('dayofmonth') == 14, 1).when(f.col('dayofmonth') == 16, 1).when(f.col('dayofmonth') == 29, 1).when(f.col('dayofmonth') == 30, 1).when(f.col('dayofmonth') == 31, 1).when(f.col('dayofmonth') == 1, 1).when(f.col('dayofmonth') == 2, 1).when(f.col('dayofmonth') == 3, 1).otherwise(0))
    #base = base.withColumn('dephour',f.when(f.length('crsdeptime')==3,f.col('crsdeptime').substr(0,1).cast("float")).otherwise(f.col('crsdeptime').substr(0,2).cast("float")) )
    base = base.withColumn('dephour',  f.when(f.col('dayofweek') == 5, 1).otherwise(0))
    base = base.withColumn('seishoras', f.when(f.col('dephour') == 6, 1).when(f.col('dephour') == 12, 1).when(f.col('dephour') == 18, 1).when(f.col('dephour') == 0, 1).otherwise(0))

    save_rds(base,"semantic.rita")
    return base




#crear_features()
