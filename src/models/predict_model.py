from pyspark.ml.classification import RandomForestClassificationModel, LogisticRegressionModel
from pyspark.ml.feature import OneHotEncoder, StringIndexer, Imputer, VectorAssembler, StandardScaler, PCA
from pyspark.sql.functions import monotonically_increasing_id, countDistinct, approxCountDistinct, when, lit
from pyspark.ml import Pipeline,  PipelineModel
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

from datetime import date, datetime
import zipfile
import os
import shutil

from src.models.bias_model import get_best_model
from src.models.train_model import get_data, prepare_data,get_models_params_dic,get_data_types
from src.models.save_model import  reverse_parse_filename
from src.utils.s3_utils import get_file_from_bucket, upload_file_to_bucket
from src.utils.db_utils import  save_rds_pandas

def get_model(s3_name):
    model_name = s3_name + ".model.zip"
    print(model_name)
    get_file_from_bucket('models-dpa',model_name, 'aux.zip')

    with zipfile.ZipFile("aux.zip", 'r') as zip_ref:
        zip_ref.extractall("model")
    os.remove("aux.zip")

    spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

    model_path = "model/" + s3_name + ".model"
    model = LogisticRegressionModel.load(model_path)
    print(model)

    shutil.rmtree("model", ignore_errors=True)
    return model

def rebuild_pipeline(s3_name, df):

    first_stages, df = prepare_data(df)
    objetivo, model_name, hyperparams = reverse_parse_filename(s3_name)

    data_types = get_data_types(df)
    numericals_double = [var for var in data_types["DoubleType"]]
    numericals_int = [var for var in data_types["IntegerType"]]

    features =  numericals_double+  numericals_int
    #          + [var + "_one_hot" for var in strings_used]
    stage_assembler = VectorAssembler(inputCols = features, outputCol= "assem_features")

    num_pca = int(hyperparams["pca"])
    if num_pca > 0:
        stage_pca = PCA(k = num_pca,inputCol = "assem_features",
                            outputCol = "features")
    else:
        stage_pca = PCA(k = 8,inputCol = "assem_features",
                    outputCol = "features")

    return df, stage_pca, stage_assembler


def save_predictions():
    df_pred, s3_name = get_predictions()

    # Save to RDS
    df_pandas = df_pred.toPandas()
    save_rds_pandas(df_pandas , "predictions.test")

    # Save to bucket
    df_pandas.to_csv("aux.csv")
    key_name = s3_name + ".preds"

    # Upload file
    upload_file_to_bucket("aux.csv", "preds-dpa", key_name)
    os.remove("aux.csv")
    #Return metadata
    tam = len(df_pandas)
    percentage_bin = sum(df_pandas.prediction) / tam
    today = date.today()
    d1 = today.strftime("%d%m%Y")

    data_list = [d1, s3_name, key_name, tam, percentage_bin ]
    return data_list

def get_predictions():
    s3_name = get_best_model()
    model = get_model(s3_name)

    df = get_data()
    df, stage_pca, first_stages = rebuild_pipeline(s3_name, df)
    print("Modelo evaluado: ",model, "con params: ", model.explainParams())

    df_assem = first_stages.transform(df)
    model_pca = stage_pca.fit(df_assem)

    # Creates Pipeline
    pipeline = PipelineModel(stages= [first_stages, model_pca, model])
    prediction = pipeline.transform(df)

    #vars_pred = ['rawPrediction','probability', 'prediction', 'distance', 'flight_number_reporting_airline']
    vars_pred = ['prediction', 'distance', 'flight_number_reporting_airline']
    df_pred = prediction.select([c for c in prediction.columns if c in vars_pred])
    df_pred = df_pred.withColumn('s3_name', lit(s3_name))

    return df_pred, s3_name


#get_predictions()
def rebuild_pipeline2(s3_name, df):

    first_stages, df = prepare_data(df)
    objetivo, model_name, hyperparams = reverse_parse_filename(s3_name)

    from pyspark.ml.feature import VectorAssembler
    data_types = get_data_types(df)
    numericals_double = [var for var in data_types["DoubleType"] if var not in ignore]
    features =  numericals_double+  numericals_int
    #          + [var + "_one_hot" for var in strings_used]
    stage_assembler = VectorAssembler(inputCols = features, outputCol= "features")


    num_pca = int(hyperparams["pca"])
    if num_pca > 0:
        stage_pca = PCA(k = num_pca,inputCol = "assem_features",
                            outputCol = "features")
    else:
        stage_pca = PCA(k = 8,inputCol = "scaled_features",
                    outputCol = "features")

    return df, stage_pca, first_stages
