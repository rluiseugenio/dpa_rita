'''
MODELLING
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline --local-scheduler  --bucname models-dpa --numIt 2 --numPCA 3  --model LR --obj 0-1.5

PREDICT
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline --local-scheduler  --bucname models-dpa --numIt 1 --numPCA 2  --model LR
'''

import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

from src.orquestadores.bias import EvaluateBias
from src.orquestadores.predictions import GetPredictions

class Pipeline(luigi.WrapperTask):
    type = luigi.Parameter()

    def requires(self):
        if self.type == "train":
            yield EvaluateBias(self) #bucket #parametros
        if self.type == "predict":
            yield ValidacionPrediciones(self)
