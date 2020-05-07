from marbles.mixins import mixins
import marbles.core
import pandas as pd
import unittest
from datetime import date, datetime
import os

#from db_utils import execute_query
#from metadatos_utils import load_verif_query

class TestingCoherence(unittest.TestCase):
    '''
    Prueba para conocer si la ingesta de datos considera el mes actual desde el
    api de rita (considerando como parametro la fecha actual)
    '''

    def test_create_resource(self):

        # texto para formarm URL de rita
        BASE_URL="https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"

        # Fecha a probar (ultima disponible al 6 de mayo 2020)
        anio= "2020"
        mes= "2"

        # Bajamos archivo y lo descomprimimos
        url_act = BASE_URL+str(anio)+"_"+str(mes)+".zip"
        comando_descarga = 'wget ' + url_act
        print("Inicia descarga de "+str(anio)+"_"+str(mes)+".zip")
        os.system(comando_descarga)

        print("Inicia descompresion de "+str(anio)+"_"+str(mes)+".zip")
        comando_descomprimir = "unzip "+ "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"+str(anio)+"_"+str(mes)+".zip"
        os.system(comando_descomprimir)

        csv_name = "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_"+str(anio)+"_"+str(mes)+".csv"
        df = pd.read_csv(csv_name)
        df = df.iloc[:,:-1] # tiramos una columna para que falle

        # elimina archivos descargados
        os.system('rm readme.html' )
        os.system("rm " + "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"+str(anio)+'_'+str(mes)+".zip")

        # Obtiene el numero de columnas del archivo recien descargado
        df = pd.read_csv('On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_'+str(anio)+'_'+str(mes)+'.csv',low_memory=False )
        numero_columnas = df.shape[1]
        # probamos el numero de columnas del archivo
        self.assertEqual(numero_columnas,110)
