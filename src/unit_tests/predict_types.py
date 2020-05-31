#python -m marbles test_semantic_columns.py
import unittest
from marbles.mixins import mixins
import pandas as pd
from pandas.testing import assert_frame_equal
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


from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)




class TestColumnsTypes(marbles.core.TestCase):
    '''
    Verifica que la cantidad de columnas en semantic.rita
    sean las esperadas

    '''

    def check_column_types(self):
        connection = pg.connect(user=MY_USER , # Usuario RDS
                                      password=MY_PASS, # password de usuario de RDS
                                      host=MY_HOST ,#"127.0.0.1", # cambiar por el endpoint adecuado
                                      port=MY_PORT, # cambiar por el puerto
                                      database=MY_DB ) # Nombre de la base de datos
        df = pd.read_sql_query('select * from predictions.test limit 5;',con=connection)
        real_types = df.dtypes.to_frame()
        dict_types = df.dtypes.to_dict()
        print(real_types) #{'flight_number': dtype('float64'), 'distance': dtype('float64'), 'prediction': dtype('O'), 's3_name': dtype('O')}

        df_pred, s3_name = get_predictions()


        df_pandas = df_pred.toPandas()
        df_pandas.columns = ['flight_number', 'distance','prediction', 's3_name', 'fecha']
        df_pandas = df_pandas.astype(dict_types)

        #Descomentar la siguiente línea para que falle la prueba
        #df_pandas['distance'] = df_pandas['distance'].astype(str)

        pred_types = df_pandas.dtypes.to_frame()
        print(pred_types) #{'flight_number_reporting_airline': dtype('float64'), 'distance': dtype('O'), 'prediction': dtype('float64'), 's3_name': dtype('O')}

        assert_frame_equal(real_types, pred_types)
