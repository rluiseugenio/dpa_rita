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
    obj = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname), CreateMetadataTable()

    def output(self):
        # Chance y aqui podemos guardar el mejor modelo en una S3
        objetivo = self.obj
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = self.obj
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model_name, hyperparams, True)


# =======================================================
# ALL TARGETS
# 1) "0-1.5"
# 2) "1.5-3.5"
# 3) "3.5-"
# 4) "cancelled"
# =======================================================
TARGET_A = "0-1.5"
TARGET_B = "1.5-3.5"
TARGET_C =  "3.5-"
TARGET_ D = "cancelled"

class RunAllTargets(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return RunTargetA(self.numIt, self.numPCA, self.model),
         RunTargetB(self.numIt, self.numPCA, self.model),
         RunTargetC(self.numIt, self.numPCA, self.model),
         RunTargetD(self.numIt, self.numPCA, self.model)

    def output(self):
        dir = CURRENT_DIR + "/target/run_all_models.txt"
        return luigi.local_target.LocalTarget(dir)

    def run(self):
        z = str(TARGET_A) + "_" + str(TARGET_D)
        with self.output().open('w') as output_file:
            output_file.write(z)

class RunTargetA(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname)

    def output(self):
        objetivo = TARGET_A
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = TARGET_A
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model_name, hyperparams, True)

class RunTargetB(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname)

    def output(self):
        objetivo = TARGET_B
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = TARGET_B
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model_name, hyperparams, True)

class RunTargetC(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname)

    def output(self):
        objetivo = TARGET_C
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = TARGET_C
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model_name, hyperparams, True)


class RunTargetD(luigi.Task):
    bucname = luigi.Parameter()
    numIt = luigi.Parameter()
    numPCA = luigi.Parameter()
    model = luigi.Parameter()

    def requires(self):
        return CreateModelBucket(self.bucname)

    def output(self):
        objetivo = TARGET_D
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        output_path = parse_filename(objetivo, model_name, hyperparams)
        output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

        return luigi.contrib.s3.S3Target(path=output_path)

    def run(self):
        objetivo = TARGET_D
        model_name = self.model
        hyperparams = {"iter": int(self.numIt),
                        "pca": int(self.numPCA)}

        run_model(objetivo, model_name, hyperparams, True)
