from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, lower, regexp_replace, split
import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

def clean(df):
    #Pasar a minusculas los nombres de columnas
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower())

    #Seleccionar columnas no vacias
    base = df.select(df.year,df.quarter, df.month, df.dayofmonth, df.dayofweek, df.flightdate, df.reporting_airline, df.dot_id_reporting_airline, df.iata_code_reporting_airline, df.tail_number, df.flight_number_reporting_airline, df.originairportid, df.originairportseqid, df.origincitymarketid, df.origin, df.origincityname, df.originstate, df.originstatefips, df.originstatename, df.originwac, df.destairportid, df.destairportseqid, df.destcitymarketid, df.dest, df.destcityname, df.deststate, df.deststatefips, df.deststatename, df.destwac, df.crsdeptime, df.deptime, df.depdelay, df.depdelayminutes, df.depdel15, df.departuredelaygroups, df.deptimeblk, df.taxiout, df.wheelsoff, df.wheelson, df.taxiin, df.crsarrtime, df.arrtime, df.arrdelay, df.arrdelayminutes, df.arrdel15, df.arrivaldelaygroups, df.arrtimeblk, df.cancelled, df.diverted, df.crselapsedtime, df.actualelapsedtime, df.airtime, df.flights, df.distance, df.distancegroup, df.divairportlandings )

    #agregar columna con clasificación de tiempo en horas de atraso del vuelo 0-1.5, 1.5-3.5,3.5-, cancelled

    from pyspark.sql import functions as f
    base = base.withColumn('rangoatrasohoras', f.when(f.col('cancelled') == 1, "cancelled").when(f.col('depdelayminutes') < 90, "0-1.5").when((f.col('depdelayminutes') > 90) & (f.col('depdelayminutes')<210), "1.5-3.5").otherwise("3.5-"))

    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    from pyspark.sql.functions import col, lower, regexp_replace, split

    #Función limpiar texto: minúsculas, espacios por guiones, split
    def clean_text(c):
        c = lower(c)
        c = regexp_replace(c, " ", "_")
        c = f.split(c, '\,')[0]
        return c


    # Aplicación de la función limpieza texto
    string_cols = [item[0] for item in base.dtypes if item[1].startswith('string')]
    for x in string_cols:
        base = base.withColumn(x, clean_text(col(x)))

    return base

def crear_features(base):
    
    from pyspark.sql import functions as f
    
    base = base.withColumn('findesemana', f.when(f.col('dayofweek') == 5, 1).when(f.col('dayofweek') == 6, 1).when(f.col('dayofweek') == 7, 1).otherwise(0))
    
    base = base.withColumn('quincena', f.when(f.col('dayofmonth') == 15, 1).when(f.col('dayofmonth') == 14, 1).when(f.col('dayofmonth') == 16, 1).when(f.col('dayofmonth') == 29, 1).when(f.col('dayofmonth') == 30, 1).when(f.col('dayofmonth') == 31, 1).when(f.col('dayofmonth') == 1, 1).when(f.col('dayofmonth') == 2, 1).when(f.col('dayofmonth') == 3, 1).otherwise(0))
    
    base = base.withColumn('dephour',f.when(f.length('crsdeptime')==3,f.col('crsdeptime').substr(0,1).cast("float")).otherwise(f.col('crsdeptime').substr(0,2).cast("float")) )
    
    base = base.withColumn('seishoras', f.when(f.col('dephour') == 6, 1).when(f.col('dephour') == 12, 1).when(f.col('dephour') == 18, 1).when(f.col('dephour') == 0, 1).otherwise(0))
    
    return(base)


def get_data():
    

    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.jars", "./postgresql-9.4.1207.jar") \
        .getOrCreate()

    df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://MY_HOST/MY_DB") \
        .option("dbtable", "raw.rita_light") \
        .option("user", "MY_USER") \
        .option("password", "MY_PASS") \
        .option("driver", "org.postgresql.Driver") \
        .load()

    return df

def init_data_luigi():
    df = get_data()
    return df

def get_clean_data():
    

    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.jars", "./postgresql-9.4.1207.jar") \
        .getOrCreate()

    df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://MY_HOST/MY_DB") \
        .option("dbtable", "clean.rita") \
        .option("user", "MY_USER") \
        .option("password", "MY_PASS") \
        .option("driver", "org.postgresql.Driver") \
        .load()

    return df

def init_data_clean_luigi():
    df = get_clean_data()
    return df
