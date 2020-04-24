from pyspark.sql import functions as f
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, lower, regexp_replace, split
!wget https://jdbc.postgresql.org/download/postgresql-9.4.1207.jar
!export SPARK_CLASSPATH=postgresql-9.4.1207.jar

def clean(df):
    #Pasar a minusculas los nombres de columnas
    for col in df.columns:
        df = df.withColumnRenamed(col, col.lower())

    #Seleccionar columnas no vacias
    base = df.select(df.year,df.quarter, df.month, df.dayofmonth, df.dayofweek, df.flightdate, df.reporting_airline, df.dot_id_reporting_airline, df.iata_code_reporting_airline, df.tail_number, df.flight_number_reporting_airline, df.originairportid, df.originairportseqid, df.origincitymarketid, df.origin, df.origincityname, df.originstate, df.originstatefips, df.originstatename, df.originwac, df.destairportid, df.destairportseqid, df.destcitymarketid, df.dest, df.destcityname, df.deststate, df.deststatefips, df.deststatename, df.destwac, df.crsdeptime, df.deptime, df.depdelay, df.depdelayminutes, df.depdel15, df.departuredelaygroups, df.deptimeblk, df.taxiout, df.wheelsoff, df.wheelson, df.taxiin, df.crsarrtime, df.arrtime, df.arrdelay, df.arrdelayminutes, df.arrdel15, df.arrivaldelaygroups, df.arrtimeblk, df.cancelled, df.diverted, df.crselapsedtime, df.actualelapsedtime, df.airtime, df.flights, df.distance, df.distancegroup, df.divairportlandings )

    #agregar columna con clasificación de tiempo en horas de atraso del vuelo 0-1.5, 1.5-3.5,3.5-, cancelled

    from pyspark.sql import functions as f
    base = base.withColumn('rangoatrasohoras', f.when(f.col('cancelled') == 1, "cancelled").when(f.col('depdelayminutes') < 90, "0-1.5").when((f.col('depdelayminutes') > 90) & (f.col('depdelayminutes')<210), "1.5-3.5").otherwise("3.5-"))

    from pyspark.sql.functions import udf
    from pyspark.sql.types import StringType
    from pyspark.sql.functions import col, lower, regexp_replace, split

    #Función limpieza
    def clean_text(c):
        c = lower(c)
        c = regexp_replace(c, " ", "_")
        c = f.split(c, '\,')[0]
        return c


    # Aplicación de la función limpieza texto
    string_cols = [item[0] for item in base.dtypes if item[1].startswith('string')]
    for x in string_cols:
        base = base.withColumn(x, clean_text(col(x)))
       
    return base
def get_data():
    
    url = 'jdbc:postgresql://rita-1.ENDPOINT.com/postgres'
    properties = {'user': 'XXXX', 'password': 'SECRETO'}
        
    spark = SparkSession.builder.config('spark.driver.extraClassPath', 'postgresql-9.4.1207.jar').getOrCreate()

    df = spark.read.jdbc(url=url, table='raw.rita_light', properties=properties)
    return df

def init_data_luigi():
    df = get_data()
    return df
