#PYTHONPATH='.' AWS_PROFILE=dpa luigi --module orquestador-clean GetCleanData --local-scheduler
import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

from pyspark.sql import SparkSession
from src.features.build_features import clean, init_data_luigi

from luigi.contrib.postgres import CopyToTable,PostgresQuery

CURRENT_DIR = os.getcwd()

class DataLocalStorage():
    def __init__(self, df_clean= None):
        self.df_clean =df_clean

    def get_data(self):
        return self.df_clean

CACHE = DataLocalStorage()

class GetDataSet(luigi.Task):

    def output(self):
        dir = CURRENT_DIR + "/target/gets_data.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        df_clean = init_data_luigi()
        CACHE.df_clean = df_clean

        z = "Obtiene Datos"
        with self.output().open('w') as output_file:
            output_file.write(z)
class GetCleanData(luigi.Task):

    def requires(self):
        return GetDataSet()

    def output(self):

        dir = CURRENT_DIR + "/target/data_clean.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):


        df_clean = CACHE.get_data()

        clean(df_clean)

        z = "Limpia Datos"
        with self.output().open('w') as output_file:
            output_file.write(z)

