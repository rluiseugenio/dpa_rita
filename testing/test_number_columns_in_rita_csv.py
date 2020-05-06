from marbles.mixins import mixins
import marbles.core
import pandas as pd
import requests
import unittest
from datetime import date, datetime
import os, subprocess, ast

class CountingCsv(unittest.TestCase):
    '''
    Verifica que la cantidad de columnas en el archivo a subirse a raw
    coincida con el esquema que se tiene definido
    '''

    def counting_cols(self):
        dir_name = "./src/data/"

        # Numero de columnas
        comando_col = "awk -F, '{ print NF; exit }' " + dir_name + item
        output_c = subprocess.check_output(comando_col, shell=True)
        index = ast.literal_eval(output_c.decode("ascii"))

        self.assertEqual(index,110)
