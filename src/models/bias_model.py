
from aequitas.group import Group
from aequitas.bias import Bias
from aequitas.fairness import Fairness
from aequitas.plotting import Plot
from aequitas.preprocessing import preprocess_input_df

import pandas as pd
import seaborn as sns
import numpy as np

from src.utils.db_utils import get_dataframe

def get_best_model():
    query = "select s3_name from metadatos.models order by f1 desc limit 1;"
    best_s3 = get_dataframe(query)
    return best_s3['s3_name'][0]

def get_bias_stats():
    best_s3 = get_best_model()
    query = "select originwac, distance, label_value, score from predictions.train where s3_name = '" + \
    best_s3 +  "';"
    predictions = get_dataframe(query)
    df = preprocess_df(predictions)

    g = Group()
    xtab, _ = g.get_crosstabs(df)
    #  group selection based on sample majority (across each attribute)
    majority_bdf = b.get_disparity_major_group(xtab, original_df=df, mask_significance=True)
    results = majority_bdf[['attribute_name', 'attribute_value'] +  calculated_disparities + disparity_significance]
    #Falta extraer lo que queremos. No sé qué queramos
    return results


def preprocess_df(df_pandas, cheat = 1):
    if cheat:
        df_pandas = df_pandas.append(df_pandas).append(df_pandas).append(df_pandas).append(df_pandas)
        df_pandas['label_value'] = np.random.choice([0,1], df_pandas.shape[0])
        df_pandas['score'] = np.random.choice([0,1], df_pandas.shape[0])

    # preprocess
    df_pandas['originwac'] = df_pandas['originwac'].astype(str)
    df_pandas['distance'] = df_pandas['distance'].astype(int)
    df, _ = preprocess_input_df(df_pandas)
    return df

def add_metadata_fairness(objetivo, model_name,hyperparams, log,train_time, test_split, train_nrows):
    AUROC = log['AUROC']
    AUPR = log['AUPR']
    precision = log['precision']
    recall = log['recall']
    f1 =log['F1 Measure']
    today = date.today()
    d1 = today.strftime("%d%m%Y")

    query = """ INSERT INTO metadatos.fairness (fecha, objetivo, model_name, hyperparams, AUROC, AUPR, precision, recall, f1, train_time, test_split, train_nrows ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  ) """
    values = (d1,
             objetivo, model_name,
             json.dumps(hyperparams),
             AUROC, AUPR, precision, recall, f1, train_time, test_split, train_nrows)
    #insert_query(query, values)

#get_bias_stats()
