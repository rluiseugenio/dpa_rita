#python -m marbles test_semantic_columns.py
import unittest
from marbles.mixins import mixins
import pandas as pd
import requests
from pyspark.sql import SparkSession
import psycopg2 as pg
import pandas as pd
import marbles
import marbles.core
from pyspark.sql.types import StructType, StructField, StringType
#from src.features.build_features import crear_features
from src.models.predict_model import get_predictions
from src.utils.db_utils import get_select

class TestPredictColumns(marbles.core.TestCase):
    '''
    Verifica que la cantidad de columnas en predictions.test
    sean las esperadas

    '''

    def check_columns(self):

        query = 'select * from predictions.test limit 1;'
        df = get_select(query)

        len_db = len(df[0])

        df_pred, s3_name = get_predictions()
        len_pred = len(df_pred.columns)

        info = "Tamaño esperado " + str(len_db) + " tamaño recibido " +   str(len_pred)

        # PARA QUE FALLE
        #len_pred = 2
        self.assertEqual(len_db, len_pred, note=info)
