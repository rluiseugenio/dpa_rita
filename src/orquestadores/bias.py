'''
SIMPLE
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module bias EvaluateBias --local-scheduler
'''
from datetime import date, datetime
from io import StringIO
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
from luigi.contrib.postgres import CopyToTable,PostgresQuery
import os
import luigi
import luigi.contrib.s3

import pandas as pd

from src.orquestadores.modelling import RunModelSimple
from src.models.bias_model import get_bias_stats
from src import (
    MY_USER ,
    MY_PASS ,
    MY_HOST ,
    MY_PORT,
    MY_DB
)

class EvaluateBias(PostgresQuery):

    def requires(self):
        return RunModelSimple()

    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST
    table ='metadatos.bias'
    update_id = "100" #Para que vuelva a correr

    data_list =  get_bias_stats()
    query = "insert into metadatos.bias values "  + str(tuple(data_list))
