
import os
import yaml
from pathlib import Path

from src.utils.s3_utils import create_bucket, get_s3_objects, describe_s3
from src.utils.ec2_utils import describe_ec2
from src.utils.db_utils import execute_query, show_select

#delete from metadatos.models ;


""" VER MODELOS """
bucket_name = "models-dpa"
get_s3_objects(bucket_name)

""" METADATA CLEAN  """
#query = "DELETE FROM metadatos.clean where usuario = 'root' "
#execute_query(query)

#query = "select * from metadatos.clean order by fecha desc; "
#show_select(query)

"""  METADATA FE """
#query = "DELETE FROM metadatos.semantic where usuario = 'root' "
#execute_query(query)

#query = "SELECT nombre_task as fecha, year as nombre_task, month as usuario, usuario as year, ip_ec2 as month, tamano_zip as ip_ec2, nombre_archivo as features, ruta_s3, task_status from metadatos.semantic order by fecha desc; "
#show_select(query)


""" METADATS MODELOS """
#query = "select * from metadatos.models order by fecha desc; "
#show_select(query)
