#python -m marbles test_semantic_column_types.py

import unittest
from marbles.mixins import mixins
import marbles
import pandas as pd
import requests
from pandas.testing import assert_frame_equal
from pyspark.sql import SparkSession
import psycopg2 as pg
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType
import psycopg2 as pg
from src.utils.testing_utils import crear_features_test, get_clean_data_test
#from src.features.build_features import crear_features

from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)


class TestSemanticColumnsTypes(marbles.core.TestCase):
    '''
    Verifica que la cantidad de columnas en semantic.rita
    sean las esperadas

    '''

    def test_all_column_types(self):

        connection = pg.connect(user=MY_USER , # Usuario RDS
                                      password=MY_PASS, # password de usuario de RDS
                                      host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                      port=MY_PORT, # cambiar por el puerto
                                      database=MY_DB ) # Nombre de la base de datos
        df = pd.read_sql_query('select * from semantic.rita limit 1;',con=connection)
        df_types = df.dtypes.to_frame()
        lol = df.dtypes.to_dict()
        csv = get_clean_data_test()
        fe = crear_features_test(csv)
        fe = fe.toPandas()
        fe = fe.astype(lol)

        ###########################
        ###########################
        ###########################
        ###########################
        ### FALLLO DE PRUEBA ######
        ###########################
        ###########################
        ###########################

        #Descomentar la siguiente línea para que falle la prueba
        #fe = fe['year'] = fe['year'].astype(str)
        csv_types = fe.dtypes.to_frame()

        return assert_frame_equal(df_types, csv_types)
