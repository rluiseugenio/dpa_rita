from marbles.mixins import mixins
import marbles.core
import pandas as pd
import requests
import unittest
from datetime import date, datetime
import os, subprocess, ast

class CountingMetadatosCsv(unittest.TestCase):
    '''
    Verifica que se la cantidad de metados escritos coincida con la cantidad de
    csv que debieron ser cargados hacia raw
    '''
    
    self.assertEqual(tam1 - tam0, cantidad_zips)
