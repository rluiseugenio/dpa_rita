# existe un bug con bot3 y luigi para pasar las credenciales
# necesitas enviar el parametro AWS_PROFILE e indicar el profile
# con el que quieres que se corra

# PYTHONPATH='.' AWS_PROFILE=dpa luigi --module orquestador CreateS3 --local-scheduler --bucname prueba --rdsname prueba2
# PYTHONPATH='.' AWS_PROFILE=dpa luigi --module orquestador RunTables --local-scheduler --filename metada_extract.sql --update-id 4
# PYTHONPATH='.' AWS_PROFILE=dpa luigi --module orquestador RunTables --local-scheduler --filename metada_extract.sql --update-id 4

import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

from src.d00_utils.s3_utils import create_bucket
from src.d00_utils.db_utils import create_db, execute_sql
from src.d00_utils.ec2_utils import create_ec2

from src import(
MY_USER,
MY_PASS,
MY_HOST,
MY_PORT,
MY_DB,
)

from luigi.contrib.postgres import CopyToTable,PostgresQuery

# ===============================
CURRENT_DIR = os.getcwd()
# ===============================
# Create S3
class CreateS3(luigi.Task):
    bucname = luigi.Parameter()

    def output(self):
        dir = CURRENT_DIR + "/target/create_s3_" + str(this.bucname) + ".txt"
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

    file_dir = "./d00_utils/sql/metada_extract.sql"
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
