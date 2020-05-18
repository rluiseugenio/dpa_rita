'''
RESTART:
aws s3 rm s3://models-dpa --recursive
'''

import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

from pyspark.sql import SparkSession

from luigi.contrib.postgres import CopyToTable,PostgresQuery

from src.utils.db_utils import execute_sql
from src.utils.s3_utils import create_bucket
from src.models.train_model import run_model
from src.models.save_model import parse_filename

# ===============================
CURRENT_DIR = os.getcwd()
# ===============================

'''
En README:
- Construcción de RDS
- Construcción de bastión
'''
# Corre script de base de datos
class CreateTables(luigi.Task):
    def output(self):
        dir = CURRENT_DIR + "/target/metadata_model.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        file_dir = "./../utils/sql/crear_tablas.sql"
        execute_sql(file_dir)

        z = str(file_dir)
        with self.output().open('w') as output_file:
            output_file.write(z)


class CreateModelBucket(luigi.Task):
    bucname = "models-dpa"

    def output(self):
        dir = CURRENT_DIR + "/target/create_s3_" + str(self.bucname) + ".txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        create_bucket(str(self.bucname))
        z = str(self.bucname)
        with self.output().open('w') as output_file:
            output_file.write(z)

class CreatePredictionBucket(luigi.Task):
    bucname = "prediction-dpa"

    def output(self):
        dir = CURRENT_DIR + "/target/create_s3_" + str(self.bucname) + ".txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        create_bucket(str(self.bucname))
        z = str(self.bucname)
        with self.output().open('w') as output_file:
            output_file.write(z)
