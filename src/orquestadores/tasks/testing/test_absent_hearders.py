from marbles.mixins import mixins
import marbles.core
import pandas as pd
import os

class TestingHeaders(marbles.core.TestCase):
    '''
    Prueba si los csv descargados de RITA tienen diferente estructura
    '''

    def test_create_resource(self):

        #Subimos de archivos csv
        dir_name = "./src/data/"
        extension_csv = ".csv"

        for item in os.listdir(dir_name):
            if item.endswith(extension_csv):

                # Numero de columnas
                df = pd.read_csv(dir_name + item, low_memory=False)

                if df.shape[1]!=110:
                    mensaje="Archivo "+str(item)+" con distinta estructura de columnas"
                    self.assertEqual(df.shape[1],110,note=mensaje)

        self.assertEqual(110,110)
