from marbles.mixins import mixins
import marbles.core
import pandas as pd
import unittest
from datetime import date, datetime
import os

MY_USER="postgres"
MY_PASS="cusbQnXvCyTHbK7LJGnV"
MY_HOST="postgres.ctruwx4duee9.us-east-1.rds.amazonaws.com"
MY_PORT=5432
MY_DB="postgres"

#from db_utils import execute_query
#from metadatos_utils import load_verif_query

class TestingHeaders(unittest.TestCase):
    '''
    Prueba para conocer si se ha cargado correctamente la cantidad de renglones
    para un csv que no posee header
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
        #df = df.iloc[:,:-1] # tiramos una columna para que falle

        def rita_csv_has_header(df):
            '''
            Funcion que determina si un csv tiene o no el encabezado del esquema
            '''

            rita_cols = ["Year","Quarter","Month","DayofMonth","DayOfWeek","FlightDate",\
            "Reporting_Airline","DOT_ID_Reporting_Airline","IATA_CODE_Reporting_Airline",\
            "Tail_Number","Flight_Number_Reporting_Airline","OriginAirportID","OriginAirportSeqID",\
            "OriginCityMarketID","Origin","OriginCityName","OriginState","OriginStateFips",\
            "OriginStateName","OriginWac","DestAirportID","DestAirportSeqID","DestCityMarketID",\
            "Dest","DestCityName","DestState","DestStateFips","DestStateName","DestWac",\
            "CRSDepTime","DepTime","DepDelay","DepDelayMinutes","DepDel15","DepartureDelayGroups",\
            "DepTimeBlk","TaxiOut","WheelsOff","WheelsOn","TaxiIn","CRSArrTime","ArrTime","ArrDelay",\
            "ArrDelayMinutes","ArrDel15","ArrivalDelayGroups","ArrTimeBlk","Cancelled","CancellationCode",\
            "Diverted","CRSElapsedTime","ActualElapsedTime","AirTime","Flights","Distance",\
            "DistanceGroup","CarrierDelay","WeatherDelay","NASDelay","SecurityDelay",\
            "LateAircraftDelay","FirstDepTime","TotalAddGTime","LongestAddGTime",\
            "DivAirportLandings","DivReachedDest","DivActualElapsedTime","DivArrDelay",\
            "DivDistance","Div1Airport","Div1AirportID","Div1AirportSeqID","Div1WheelsOn",\
            "Div1TotalGTime","Div1LongestGTime","Div1WheelsOff","Div1TailNum","Div2Airport",\
            "Div2AirportID","Div2AirportSeqID","Div2WheelsOn","Div2TotalGTime",\
            "Div2LongestGTime","Div2WheelsOff","Div2TailNum","Div3Airport","Div3AirportID",\
            "Div3AirportSeqID","Div3WheelsOn","Div3TotalGTime","Div3LongestGTime",\
            "Div3WheelsOff","Div3TailNum","Div4Airport","Div4AirportID","Div4AirportSeqID",\
            "Div4WheelsOn","Div4TotalGTime","Div4LongestGTime","Div4WheelsOff","Div4TailNum",\
            "Div5Airport","Div5AirportID","Div5AirportSeqID","Div5WheelsOn","Div5TotalGTime",\
            "Div5LongestGTime","Div5WheelsOff","Div5TailNum"]

            index = 1

            for col in rita_cols:
                index= index*abs(col in df.columns)

            return index

        csv_has_good_header=rita_csv_has_header(df)

        if csv_has_good_header==1:
            numero_renglones = df.shape[0]
        else:
            numero_renglones = df.shape[0]+1


        # elimina archivos descargados
        os.system('rm readme.html' )
        os.system("rm " + "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_"+str(anio)+'_'+str(mes)+".zip")

        # Obtiene el numero de columnas del archivo recien descargado
        df = pd.read_csv('On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_'+str(anio)+'_'+str(mes)+'.csv',low_memory=False)
        n=1
        df.drop(df.head(n).index,inplace=True) # quita los primeros n renglones
        numero_renglones = df.shape[0]

        import psycopg2
        import psycopg2.extras

        # Conexion y cursor para query
        connection = psycopg2.connect(user = MY_USER, password = MY_PASS, host = MY_HOST, port="5432", database=MY_DB)
        cursor = connection.cursor()

        # Query para verificacion a la base de datos
        postgreSQL_select_Query = "select num_renglones from metadatos.load where\
        nombre_archivo='On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_"+ str(anio) +"_"+ str(mes) + ".csv"+"';"
        cursor.execute(postgreSQL_select_Query)
        select_Query = cursor.fetchone()
        tam = int(select_Query[0])
        cursor.close()
        connection.close()

        # probamos el numero de renglones del archivo vs los que se subieron a rds
        self.assertEqual(numero_renglones,tam)
