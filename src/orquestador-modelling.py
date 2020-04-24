# PYTHONPATH='.' AWS_PROFILE=dpa luigi \
# --module orquestador-modelling RunModel --local-scheduler \
# --bucname models-dpa --numIt 1 --numPCA 2

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


class CreateMetadataTable(luigi.Task):
    def output(self):
        dir = CURRENT_DIR + "/target/metadata_model.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        file_dir = "./sql/metada_model.sql"
        execute_sql(file_dir)

        z = str(file_dir)
        with self.output().open('w') as output_file:
            output_file.write(z)


class CreateModelBucket(luigi.Task):
    bucname = luigi.Parameter()

    def output(self):
        dir = CURRENT_DIR + "/target/create_s3_" + str(self.bucname) + ".txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        create_bucket(str(self.bucname))
        z = str(self.bucname)
        with self.output().open('w') as output_file:
            output_file.write(z)


class RunModel(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname), CreateMetadataTable()

    def output(self):
        # Chance y aqui podemos guardar el mejor modelo en una S3
        objetivo = "cancelled"
        model_name = "LR"
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = "cancelled"
        model = "LR"
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model, hyperparams, True)



#========================================================================
#================== GRIDSEARCH EN PARALELO ==============================
#========================================================================



class RunModelGenerico(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    objetivo = luigi.Parameter()
    modelname = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname), CreateMetadataTable()

    def output(self):
        # Chance y aqui podemos guardar el mejor modelo en una S3
        objetivo = str(self.objetivo)
        model_name = str(self.modelname)
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = str(self.objetivo)
        model_name = str(self.modelname)
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        # Esta funcion ya guarda los metadatos en un BD
        # Corre los modelos y el mejor lo guarda en un S3 y guarda toda la info
        # Toma la base de semantic
        run_model(objetivo, model, hyperparams, True)
