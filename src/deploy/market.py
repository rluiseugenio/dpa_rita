from io import StringIO
import pandas as pd
from src.utils.db_utils import get_select

def get_prediction(flight_number):
    """ Regresa la prediccion
        Args:
            flight_number (float): número de vuelo
        Returns:
            delay (boolean): valor predecido
    """
    try:
        query = "select prediction from predictions.test where \
        flight_number = {} limit 1;".format(flight_number)

        records =get_select(query)
        delay = records[0][0]

        return delay
    except (Exception) as error :
        print ("Error while fetching data from PostgreSQL", error)
        return "Flight not found"
