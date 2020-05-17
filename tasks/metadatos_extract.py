import luigi.contrib.postgres
#from tasks.extract import Extraction

class Metadata_Extract(luigi.contrib.postgres.CopyToTable):
    '''
    Task de luigi para insertar renglones en renglones en tabla de metadatos
    de la extraccion y load de metadatos a S3
    '''
    def requires(self):
        return Extraction()

    # Lectura de archivo de credenciales
    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST

    # Nombre de tabla donde se inserta info. Notas:
    # 1) si la tabla (sin esquema) no existe, luigi la crea con esquema publico,
    # 2) si el esquema de la tabla no existe, luigi devuelve error :(
    table = 'metadatos.extract'

    # Estructura de las columnas que integran la tabla (ver esquema)
    columns = [("fecha", "VARCHAR"),\
            ("nombre_task", "VARCHAR"),\
            ("year","VARCHAR"),\
            ("month","VARCHAR"),\
            ("usuario","VARCHAR"),\
            ("ip_ec2","VARCHAR"),\
            ("tamano_zip","VARCHAR"),\
            ("nombre_archivo","VARCHAR"),\
            ("ruta_s3","VARCHAR"),\
            ("task_status", "VARCHAR")]

    def rows(self):
        # Funcion para insertar renglones en tabla

        # Renglon o renglones (separados por coma) a ser insertado
        r = meta_extract # arreglo definio en extract

        # Insertamos renglones en tabla
        for element in r:
            yield element
        print('\n---Fin de  carga de metadatos de extract ---\n')
