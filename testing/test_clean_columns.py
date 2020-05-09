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

class Test_Columns_Case(unittest.TestCase, mixins.CategoricalMixins):
	'''
    Verifica que la cantidad de columnas en clean.rita 
    sean las esperadas

    '''

	def test_that_all_ranges_are_present(self):


		df = get_clean_data()		
		self.assertEqual(len(df.columns), 57)
