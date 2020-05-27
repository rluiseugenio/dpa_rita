'''
SIMPLE
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module predictions CreatePredictions --local-scheduler
'''
from datetime import date, datetime
from io import StringIO
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
from luigi.contrib.postgres import CopyToTable,PostgresQuery
import os
import luigi
import luigi.contrib.s3

import pandas as pd

from src.orquestadores.bias import EvaluateBias
from src.models.predict_model import save_predictions

from src import (
    MY_USER ,
    MY_PASS ,
    MY_HOST ,
    MY_PORT,
    MY_DB
)

class CreatePredictions(PostgresQuery):

    #def requires(self):
    #    return EvaluateBias()

    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST
    table ='metadatos.predictions'
    #update_id = "45" #Para que vuelva a correr

    data_list =  save_predictions()
    query = "insert into " + table + " values "  + str(tuple(data_list))
