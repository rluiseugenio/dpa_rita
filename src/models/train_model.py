

from src.features.build_features import clean
from src.utils.db_utils import execute_sql,insert_query
from src.models.save_model import save_upload

from datetime import date, datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, DoubleType
from pyspark.sql.functions import monotonically_increasing_id, countDistinct, approxCountDistinct, when

from pyspark.ml.feature import OneHotEncoder, StringIndexer, Imputer, VectorAssembler, StandardScaler, PCA
from pyspark.ml import Pipeline
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.ml.classification import LogisticRegression, DecisionTreeClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics

from collections import defaultdict

import pandas as pd
import time
import json



def get_data(luigi):
    #El parametro luigi es True si se corre en luigi (y docker)
    import os
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(dir_path)

    if luigi:
        direccion =  "/home/data/raw/prueba.csv"
    else:
        direccion = "./../data/raw/prueba.csv"


    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

    df = spark.read.csv(direccion, header="true", inferSchema="true").limit(20000)
    df = clean(df)
    return df


def imputa_categoricos(df, ignore,data_types):
    strings_used = [var for var in data_types["StringType"] if var not in ignore]

    missing_data_fill = {}
    for var in strings_used:
        missing_data_fill[var] = "missing"

    df = df.fillna(missing_data_fill)
    return df

def ignore_list(df, data_types):
    counts_summary = df.agg(*[countDistinct(c).alias(c) for c in data_types["StringType"]])
    counts_summary = counts_summary.toPandas()

    counts = pd.Series(counts_summary.values.ravel())
    counts.index = counts_summary.columns

    sorted_vars = counts.sort_values(ascending = False)
    ignore = list((sorted_vars[sorted_vars >100]).index)
    return ignore

def get_data_types(df):
    data_types = defaultdict(list)
    for entry in df.schema.fields:
        data_types[str(entry.dataType)].append(entry.name)
    return data_types


def create_pipeline(df, ignore):
    # Esto lo ponemos aqui para poder modificar las
    #variables de los estimadores/transformadores
    data_types = get_data_types(df)
    #--------------------------------------

    # -------------- STRING --------------
    strings_used = [var for var in data_types["StringType"] if var not in ignore]

    # -------------- DOUBLE --------------
    numericals_double = [var for var in data_types["DoubleType"] if var not in ignore]
    numericals_double_imputed = [var + "_imputed" for var in numericals_double]

    # -------------- INTEGERS --------------
    from pyspark.sql.types import IntegerType, DoubleType
    numericals_int = [var for var in data_types["IntegerType"] if var not in ignore]

    for c in numericals_int:
        df = df.withColumn(c, df[c].cast(DoubleType()))
        df = df.withColumn(c, df[c].cast("double"))

    numericals_int_imputed = [var + "_imputed" for var in numericals_int]
    # =======================================

    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    ##            P I P E L I N E
    ## %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # ============= ONE HOT ENCODING ================
    from pyspark.ml.feature import OneHotEncoder, StringIndexer
    stage_string = [StringIndexer(inputCol= c, outputCol= c+"_string_encoded") for c in strings_used]
    stage_one_hot = [OneHotEncoder(inputCol= c+"_string_encoded", outputCol= c+ "_one_hot") for c in strings_used]

    # =============== IMPUTADORES ====================
    from pyspark.ml.feature import Imputer
    stage_imputer_double = Imputer(inputCols = numericals_double,
                                   outputCols = numericals_double_imputed)
    stage_imputer_int = Imputer(inputCols = numericals_int,
                                outputCols = numericals_int_imputed)

    # ============= VECTOR ASESEMBLER ================
    from pyspark.ml.feature import VectorAssembler

    features =  numericals_double_imputed \
              + [var + "_one_hot" for var in strings_used]
    stage_assembler = VectorAssembler(inputCols = features, outputCol= "assem_features")

    # ==================== SCALER =======================
    from pyspark.ml.feature import StandardScaler
    stage_scaler = StandardScaler(inputCol= stage_assembler.getOutputCol(),
                                  outputCol="scaled_features", withStd=True, withMean=True)

    # ================== PIPELINE ===================
    stages= stage_string + stage_one_hot +  [             # Categorical Data
                               stage_imputer_double,
                               stage_imputer_int,        # Data Imputation
                               stage_assembler,          # Assembling data
                               stage_scaler]

    ## Tenemos que regesar el df porque las variables int las combierte en double
    print(stages)
    return  stages , df


def get_models_params_dic():
    stage_pca = PCA(k = 15,inputCol = "scaled_features",
                        outputCol = "features")


    lr = LogisticRegression()

    lr_paramGrid = ParamGridBuilder() \
    .addGrid(stage_pca.k, [1]) \
    .addGrid(lr.maxIter, [1]) \
    .build()

    dt = DecisionTreeClassifier()

    dt_paramGrid = ParamGridBuilder() \
    .addGrid(stage_pca.k, [1]) \
    .addGrid(dt.maxDepth, [2]) \
    .build()

    paramGrid_dic= {"LR":lr_paramGrid,"DT":dt_paramGrid}
    model_dic = {"LR":lr,"DT":dt}

    return model_dic,paramGrid_dic


def prepare_data(df):
    data_types = get_data_types(df)
    ignore =   ignore_list(df, data_types)
    illegal = [s for s in df.columns if "del" in s]
    extra_illegal = ['cancelled', 'rangoatrasohoras']
    legal = [var for var in df.columns if (var not in ignore and var not in illegal and var not in extra_illegal)]
    lista_objetivos = df.select('rangoatrasohoras').distinct().rdd.map(lambda r: r[0]).collect()

    df = imputa_categoricos(df, ignore,data_types)

    df_legal = df[legal]
    y = df[['rangoatrasohoras']]

    df_legal = df_legal.withColumn("id", monotonically_increasing_id())
    y = y.withColumn("id", monotonically_increasing_id())

    stages, df_new = create_pipeline(df_legal, ignore)

    df_junto = df_new.join(y, "id", "outer").drop("id")

    return  stages,df_junto



def run_model(objetivo, model_name, hyperparams, luigi= False, test_split = 0.2):
    df = get_data(False)
    first_stages,df = prepare_data(df)

    df = df.withColumn("label",  when(df.rangoatrasohoras == objetivo, 1.0).otherwise(0.0))

    # Selecciona el modelo
    model_dic, paramGrid_dic  = get_models_params_dic()
    clr_model = model_dic[model_name]

    # Parametros especificos
    num_it = int(hyperparams["iter"])
    if num_it > 0:
        clr_model.setMaxIter(num_it)

    # Adds new stages
    num_pca = int(hyperparams["pca"])
    if num_pca > 0:
        stage_pca = PCA(k = num_pca,inputCol = "scaled_features",
                            outputCol = "features")
    else:
        stage_pca = PCA(k = 8,inputCol = "scaled_features",
                    outputCol = "features")

    # Checar que no se haya corrido este modelo

    print("Modelo evaluado: ", clr_model, "con params: ", clr_model.explainParams())

    # Creates Pipeline
    pipeline = Pipeline(stages= first_stages + [stage_pca, clr_model])

    df_train, df_test = df.randomSplit([(1-test_split),test_split ], 123)

    start = time.time()
    cvModel  = pipeline.fit(df_train)
    end = time.time()

    prediction = cvModel.transform(df_test)
    log = evaluate(prediction)

    #Guarda en s3
    save_upload(cvModel, objetivo, model_name, hyperparams)

    # Sube metadatos a RDS
    # --- Metadata -----
    train_time = end - start
    train_nrows = df_train.count()
    # -------------------
    add_meta_data(objetivo, model_name,hyperparams, log,train_time, test_split, train_nrows)



def evaluate(predictionAndLabels):
    log = {}

    # Show Validation Score (AUROC)
    evaluator = BinaryClassificationEvaluator(metricName='areaUnderROC')
    log['AUROC'] = "%f" % evaluator.evaluate(predictionAndLabels)
    print("Area under ROC = {}".format(log['AUROC']))

    # Show Validation Score (AUPR)
    evaluator = BinaryClassificationEvaluator(metricName='areaUnderPR')
    log['AUPR'] = "%f" % evaluator.evaluate(predictionAndLabels)
    print("Area under PR = {}".format(log['AUPR']))

    # Metrics
    predictionRDD = predictionAndLabels.select(['label', 'prediction']) \
                            .rdd.map(lambda line: (line[1], line[0]))
    metrics = MulticlassMetrics(predictionRDD)

    # Confusion Matrix
    print(metrics.confusionMatrix().toArray())

    # Overall statistics
    log['precision'] = "%s" % metrics.precision()
    log['recall'] = "%s" % metrics.recall()
    log['F1 Measure'] = "%s" % metrics.fMeasure()
    print("[Overall]\tprecision = %s | recall = %s | F1 Measure = %s" % \
            (log['precision'], log['recall'], log['F1 Measure']))

    # Statistics by class
    labels = [0.0, 1.0]
    for label in sorted(labels):
        log[label] = {}
        log[label]['precision'] = "%s" % metrics.precision(label)
        log[label]['recall'] = "%s" % metrics.recall(label)
        log[label]['F1 Measure'] = "%s" % metrics.fMeasure(label,
                                                           beta=0.5)
        print("[Class %s]\tprecision = %s | recall = %s | F1 Measure = %s" \
                  % (label, log[label]['precision'],
                    log[label]['recall'], log[label]['F1 Measure']))

    return log



def add_meta_data(objetivo, model_name,hyperparams, log,train_time, test_split, train_nrows):
    AUROC = log['AUROC']
    AUPR = log['AUPR']
    precision = log['precision']
    recall = log['recall']
    f1 =log['F1 Measure']
    today = date.today()
    d1 = today.strftime("%d%m%Y")

    query = """ INSERT INTO metadatos.models (fecha, objetivo, model_name, hyperparams, AUROC, AUPR, precision, recall, f1, train_time, test_split, train_nrows ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s  ) """
    values = (d1,
             objetivo, model_name,
             json.dumps(hyperparams),
             AUROC, AUPR, precision, recall, f1, train_time, test_split, train_nrows)
    insert_query(query, values)
