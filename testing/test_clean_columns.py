#python -m marbles test_clean_columns.py

import unittest
from marbles.mixins import mixins
import pandas as pd
import requests
from pyspark.sql import SparkSession
import psycopg2 as pg
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType
from src.features.build_features import get_clean_data
import socket
from src.utils.metadatos_utils import Linaje_clean_data, clean_metadata_rds
from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)

class Test_Columns_Case(unittest.TestCase, mixins.CategoricalMixins):
    '''
    
    Verifica que la cantidad de columnas en clean.rita 
    sean las esperadas

    '''

	def test_that_all_ranges_are_present(self):


		df_clean = clean().limit(10)
		clean_rita	= get_clean_data().limit(10)
		self.assertEqual(len(df_clean.columns), len(clean_rita.columns))

