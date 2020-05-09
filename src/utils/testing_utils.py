#python -m marbles test_semantic_columns.py

import unittest
from marbles.mixins import mixins
import pandas as pd
import requests
from pyspark.sql import SparkSession
import psycopg2 as pg
import pandas as pd
import marbles
from pyspark.sql.types import StructType, StructField, StringType
import psycopg2 as pg
#from src.features.build_features import crear_features

from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)


def get_clean_data_test():
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
    pdf = pd.read_sql_query('select * from clean.rita limit 1;',con=connection)
    spark = SparkSession.builder.config('spark.driver.extraClassPath', 'postgresql-9.4.1207.jar').getOrCreate()
    df = spark.createDataFrame(pdf, schema=clean_rita)

    return df


def crear_features_test(base):

    from pyspark.sql import functions as f


    base = base.withColumn('findesemana', f.when(f.col('dayofweek') == 5, 1).when(f.col('dayofweek') == 6, 1).when(f.col('dayofweek') == 7, 1).otherwise(0))
    base = base.withColumn('quincena', f.when(f.col('dayofmonth') == 15, 1).when(f.col('dayofmonth') == 14, 1).when(f.col('dayofmonth') == 16, 1).when(f.col('dayofmonth') == 29, 1).when(f.col('dayofmonth') == 30, 1).when(f.col('dayofmonth') == 31, 1).when(f.col('dayofmonth') == 1, 1).when(f.col('dayofmonth') == 2, 1).when(f.col('dayofmonth') == 3, 1).otherwise(0))


    base = base.withColumn('dephour',  f.when(f.col('dayofweek') == 5, 1).otherwise(0))
    base = base.withColumn('seishoras', f.when(f.col('dephour') == 6, 1).when(f.col('dephour') == 12, 1).when(f.col('dephour') == 18, 1).when(f.col('dephour') == 0, 1).otherwise(0))


    return base
