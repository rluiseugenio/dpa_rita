'''
RESTART:
aws s3 rm s3://models-dpa --recursive
drop from metadata.bias
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
from src.utils.db_utils import create_db, execute_sql
from src.utils.ec2_utils import create_ec2

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

class CreateS3(luigi.Task):
    bucname = luigi.Parameter()

    def output(self):
        dir = CURRENT_DIR + "/target/create_s3_" + str(self.bucname) + ".txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        create_bucket(str(self.bucname))
        z = str(self.bucname)
        with self.output().open('w') as output_file:
            output_file.write(z)

# Create RDS.
class CreateRDS(luigi.Task):
    rdsname = luigi.Parameter()

    def output(self):
        dir = CURRENT_DIR + "/target/create_rds_" + str(this.rdsname) + ".txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        create_db(str(this.rdsname))
        z = str(self.rdsname)
        with self.output().open('w') as output_file:
            output_file.write(z)

# Create tables and squemas
# "metada_extract.sql"
class CreateTables(PostgresQuery):
    filename = luigi.Parameter()
    update_id = luigi.Parameter()

    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST
    table = "metadatos"

    file_dir = "./utils/sql/metada_extract.sql"
    query = open(file_dir, "r").read()



class RunTables(luigi.Task):
    filename = luigi.Parameter()
    update_id = luigi.Parameter()

    def requires(self):
        return CreateTables(self.filename, self.update_id)

    def run(self):
        z = str(self.filename) + " " + str(self.update_id)

        with self.output().open('w') as output_file:
            output_file.write(z)

    def output(self):
        dir = CURRENT_DIR + "/target/create_tables.txt"
        return luigi.local_target.LocalTarget(dir)



# Create EC2
class CreateEC2(luigi.Task):
    def output(self):
        dir = CURRENT_DIR + "/target/create_ec2.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        resp = create_ec2()

        with self.output().open('w') as output_file:
            output_file.write(resp)
