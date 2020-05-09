from marbles.mixins import mixins
import marbles.core
import pandas as pd
import requests
import unittest
from datetime import date, datetime

#from db_utils import execute_query
#from metadatos_utils import load_verif_query


class TestingRitaApi(unittest.TestCase):
    '''
    Prueba para conocer si la ingesta de datos considera el mes actual desde el
    api de rita (considerando como parametro la fecha actual)
    '''

    def test_create_resource(self):

        # texto para formarm URL de rita
        BASE_URL="https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

        # Obtiene anio y mes correspondiente fecha actual de ejecucion del script
        #now = datetime.now()
        #current_year = now.year
        #current_month = now.month

        api_rita = BASE_URL+str(anio)+"_"+str(mes)+".zip"

        res = requests.get(api_rita)
        self.assertEqual(res.status_code,200)
