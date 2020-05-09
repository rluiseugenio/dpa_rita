from marbles.mixins import mixins
import marbles.core
import pandas as pd
import unittest
from datetime import date, datetime

class TestingBucket(unittest.TestCase):
    '''
    Prueba para conocer si el tamano del zip en de los metadatos coincide con el del archivo
    descargado api de rita (considerando como parametro la fecha actual)
    '''

    def test_zip_size_in_bucket(self):

        # Consultamos el bucket
        zip_bucket = my_bucket.Object(key="RITA/YEAR="+str(anio)+"/"+str(anio)+"_"+str(mes)+".zip").content_length

        # Consultamos tamano de archivo en disco
        dir_name="./src/data/"
        name_to_zip = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

        zip_disk = Path(dir_name+name_to_zip+str(anio)+"_"+str(mes)+".zip").stat().st_size

        self.assertEqual(zip_bucket,zip_disk)
