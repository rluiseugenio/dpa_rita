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
from src.utils.testing_utils import crear_features_test, get_clean_data_test
#from src.features.build_features import crear_features

from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)




class TestSemanticColumns(marbles.core.TestCase):
    '''
    Verifica que la cantidad de columnas en semantic.rita
    sean las esperadas

    '''

    def test_that_all_columns_are_present(self):


        connection = pg.connect(user=MY_USER , # Usuario RDS
                                      password=MY_PASS, # password de usuario de RDS
                                      host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                      port=MY_PORT, # cambiar por el puerto
                                      database=MY_DB ) # Nombre de la base de datos
        df = pd.read_sql_query('select * from semantic.rita limit 1;',con=connection)
        col_len_df = len(df.columns)
        csv = get_clean_data_test()
        fe = crear_features_test(csv)
        fe = fe.toPandas()
        col_len_csv = len(fe.columns)
        self.assertEqual(col_len_df, col_len_csv)
