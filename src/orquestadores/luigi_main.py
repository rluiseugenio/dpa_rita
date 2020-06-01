'''
MODELLING
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline --local-scheduler  --type train

PREDICT
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline --local-scheduler  --type predict
'''

import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

from src.orquestadores.bias import EvaluateBias
from src.orquestadores.predictions import CreatePredictions

class Pipeline(luigi.WrapperTask):
    type = luigi.Parameter()

    def requires(self):
        if self.type == "train":
            yield EvaluateBias()
        if self.type == "predict":
            yield CreatePredictions()
