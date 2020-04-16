

from src.features.build_features import clean

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
    stage_string = [StringIndexer(inputCol= c, outputCol= c+"_string_encoded") for c in strings_used]
    stage_one_hot = [OneHotEncoder(inputCol= c+"_string_encoded", outputCol= c+ "_one_hot") for c in strings_used]

    # =============== IMPUTADORES ====================
    stage_imputer_double = Imputer(inputCols = numericals_double, 
                                   outputCols = numericals_double_imputed) 
    stage_imputer_int = Imputer(inputCols = numericals_int, 
                                outputCols = numericals_int_imputed) 

    # ============= VECTOR ASESEMBLER ===============
    features =  numericals_double_imputed \
              + [var + "_one_hot" for var in strings_used]
    stage_assembler = VectorAssembler(inputCols = features, outputCol= "assem_features")

    # ==================== SCALER =======================
    stage_scaler = StandardScaler(inputCol= stage_assembler.getOutputCol(), 
                                  outputCol="scaled_features", withStd=True, withMean=True)

    # ================== PIPELINE ===================
    pipeline = Pipeline(stages= stage_string + stage_one_hot +          # Categorical Data
                              [stage_imputer_double,
                               stage_imputer_int,                       # Data Imputation
                               stage_assembler,                         # Assembling data
                               stage_scaler,                            # Standardize data
                          ])
                          
    ## Tenemos que regesar el df porque las variables int las combierte en double
    return  pipeline , df


def imputa_categoricos(df, ignore,data_types):
    strings_used = [var for var in data_types["StringType"] if var not in ignore]
    
    missing_data_fill = {}
    for var in strings_used:
        missing_data_fill[var] = "missing"

    df = df.fillna(missing_data_fill)
    return df


    
def add_ids(X_train, X_test, y_train, y_test):  
    X_train = X_train.withColumn("id", monotonically_increasing_id())
    X_test = X_test.withColumn("id", monotonically_increasing_id())
    y_train = y_train.withColumn("id", monotonically_increasing_id())
    y_test = y_test.withColumn("id", monotonically_increasing_id())
        
    return X_train, X_test, y_train, y_test



def get_models_params():
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

    paramGrid_list = [lr_paramGrid, dt_paramGrid]
    model_list = [lr,dt]
    
    return model_list,paramGrid_list

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

def cv_stats(cvModel):
    bestModel =  cvModel.bestModel
    print("iter", bestModel.stages[-1]._java_obj.getMaxIter())
    


def get_data():
    direccion = "./../data/raw/prueba.csv"


    spark = SparkSession \
        .builder \
        .appName("Python Spark SQL basic example") \
        .config("spark.some.config.option", "some-value") \
        .getOrCreate()

    df = spark.read.csv(direccion, header="true", inferSchema="true").limit(30000)
    df = clean(df)
    return df


def get_processed_train_test(df):
    data_types = get_data_types(df)
    ignore =   ignore_list(df, data_types) 
    illegal = [s for s in df.columns if "del" in s]
    extra_illegal = ['cancelled', 'rangoatrasohoras']
    legal = [var for var in df.columns if (var not in ignore and var not in illegal and var not in extra_illegal)]
    lista_objetivos = df.select('rangoatrasohoras').distinct().rdd.map(lambda r: r[0]).collect()

    df = imputa_categoricos(df, ignore, data_types)
    X = df[legal]
    y = df[['rangoatrasohoras']]

    pipeline, X = create_pipeline(X, ignore)

    X_train, X_test = X.randomSplit([0.8,0.2], 123)
    y_train, y_test = y.randomSplit([0.8,0.2], 123)

    model = pipeline.fit(X_train)

    X_train = model.transform(X_train)
    X_test = model.transform(X_test)

    X_train, X_test, y_train, y_test = add_ids(X_train, X_test, y_train, y_test)
    return X_train, X_test, y_train, y_test

def init_data_luigi():
    df = get_data()
    df = clean(df)
    X_train, X_test, y_train, y_test = get_processed_train_test(df)
    return X_train, X_test, y_train, y_test

def main():

    df = get_data()
    df = clean(df)

    X_train, X_test, y_train, y_test = get_processed_train_test(df)
    
    lista_objetivos = df.select('rangoatrasohoras').distinct().rdd.map(lambda r: r[0]).collect()

    
    # CREA 4 MODELOS
    for objetivo in lista_objetivos:
        print("objetivo: ", objetivo)

        y_test = y_test.withColumn("label",  when(y_test.rangoatrasohoras == objetivo, 1.0).otherwise(0.0))
        y_train = y_train.withColumn("label",  when(y_train.rangoatrasohoras == objetivo, 1.0).otherwise(0.0))

        df_train = X_train.join(y_train, "id", "outer").drop("id")
        df_test = X_test.join(y_test, "id", "outer").drop("id")

        stage_pca = PCA(k = 15,inputCol = "scaled_features", 
                                outputCol = "features")

    
        # BUSCA EL MEJOR MODELO
        model_list, paramGrid_list  = get_models_params()
        for clr_model, params in zip(model_list, paramGrid_list):
            print("Modelo evaluado: ", clr_model, "con params: ", params)
            pipeline = Pipeline(stages= [stage_pca, clr_model])

            crossval = CrossValidator(estimator=pipeline,
                                      estimatorParamMaps=params,
                                      evaluator=MulticlassClassificationEvaluator(metricName='f1'),
                                      numFolds=2)  # use 3+ folds in practice

            cvModel  = crossval.fit(df_train)
            prediction = cvModel.transform(df_test)
            evaluate(prediction)

main()
    
