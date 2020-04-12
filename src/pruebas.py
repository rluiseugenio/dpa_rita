
import os
import yaml
from pathlib import Path

from src.d00_utils.s3_utils import create_bucket
from src.d00_utils.s3_utils import describe_s3
from src.d00_utils.ec2_utils import describe_ec2
from src.d00_utils.db_utils import execute_query, show_select

usr_dir = os.path.join(str(Path.home()), ".rita")
print(usr_dir)

with open(os.path.join(usr_dir, "conf", "path_parameters.yml")) as f:
    paths = yaml.safe_load(f)

bucket = paths["bucket"]

print(bucket)

#filename = "metada_extract.sql"
#file_dir = "./d00_utils/sql/" + filename

#print(open(file_dir, "r").read())

query = "DROP table metadatos.extract;"
execute_query(query)

query = "INSERT INTO metadatos.extract (fecha, nombre_task, year, month, usuario, ip_ec2, tamano_zip, nombre_archivo, ruta_s3, task_status) VALUES ( '2', '2', '3','3','4','5','5', '6', '6','8' ) ;"
execute_query(query)

query = "SELECT * FROM metadatos.extract ; "
show_select(query)

#describe_s3()
#describe_ec2()
