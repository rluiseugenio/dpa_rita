'''
SIMPLE
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module predictions CreatePredictions --local-scheduler

PYTHONPATH='.' AWS_PROFILE=dpa luigi --module predictions  PredictTestCols --local-scheduler
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
from src.utils.db_utils import execute_query
from src.unit_tests.predict_columns import TestPredictColumns

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



class PredictTestCols(luigi.Task):
    '''
    Prueba unitaria de estructura de archivos descargados
    '''
    #def requires(self):
    #    return Extraction()

    def run(self):
        try:
            unit_test = TestPredictColumns()
            unit_test.check_columns()
        except:
            raise ValueError('number of columns do not match.')


@PredictTestCols.event_handler(Event.SUCCESS)
def on_success(self):
    today = date.today()
    d1 = today.strftime("%d%m%Y")

    data_list = [d1, "check_columns", "success", "none"]
    table ='metadatos.testing_predict_cols'
    query = "insert into " + table + " values "  + str(tuple(data_list))
    execute_query(query)


@PredictTestCols.event_handler(Event.FAILURE)
def on_failure(self,exception):
    today = date.today()
    d1 = today.strftime("%d%m%Y")

    data_list = [d1, "check_columns", "failure", "number of columns do not match"]
    table ='metadatos.testing_predict_cols'
    query = "insert into " + table + " values "  + str(tuple(data_list))
    execute_query(query)
