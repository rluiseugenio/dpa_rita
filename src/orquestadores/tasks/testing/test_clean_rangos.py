#python -m marbles test_clean_rangos.py

import unittest
from marbles.mixins import mixins
import pandas as pd
import requests
from pyspark.sql import SparkSession
import psycopg2 as pg
import pandas as pd
from pyspark.sql.types import StructType, StructField, StringType
from src.features.build_features import get_clean_data

class Test_Ranges_Case(unittest.TestCase, mixins.CategoricalMixins):
	'''
    Verifica que los valores de la columna rangoatrasohoras 
    sean los indicados

    '''

	def test_that_all_ranges_are_present(self):


		df = get_clean_data()
		RANGOS=['cancelled', '0-1.5', '1.5-3.5' ,'3.5-']
		self.assertCategoricalLevelsEqual(list(df.toPandas()["rangoatrasohoras"].unique()), RANGOS)
