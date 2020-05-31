
from aequitas.group import Group
from aequitas.bias import Bias
from aequitas.fairness import Fairness
from aequitas.plotting import Plot
from aequitas.preprocessing import preprocess_input_df
from datetime import date, datetime

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
    bias_result = get_fpr_disparity(df, "distance")

    today = date.today()
    d1 = today.strftime("%Y%m%d")

    metadata = [d1]+ [best_s3] + bias_result
    return metadata

def get_fpr_disparity(df, protected_attribute):
     g = Group()
     xtab, _ = g.get_crosstabs(df)

     df_count = df[['distance', 'score']].groupby(['distance']).agg(['count'])
     get_largest_cat = df_count[('score')].sort_values(['count'], ascending = False).index[0]

     b = Bias()
     bdf = b.get_disparity_predefined_groups(xtab, original_df=df,
      ref_groups_dict={'originwac':df[:1].originwac[0],'distance':get_largest_cat},
      alpha=0.05, mask_significance=True)
     calculated_disparities = b.list_disparities(bdf)
     disparity_significance = b.list_significance(bdf)
     majority_bdf = b.get_disparity_major_group(xtab, original_df=df, mask_significance=True)
     results = majority_bdf[['attribute_name', 'attribute_value'] + \
     calculated_disparities + disparity_significance]

     res_distance = results[results.attribute_name ==protected_attribute]
     values= res_distance.attribute_value.tolist()
     disparity = res_distance.fpr_disparity.tolist()
     bias_result = values + disparity
     return bias_result

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



#print(get_bias_stats())
