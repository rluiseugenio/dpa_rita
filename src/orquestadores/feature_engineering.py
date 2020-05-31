import luigi
import luigi.contrib.s3
from luigi import Event, Task, build # Utilidades para acciones tras un task exitoso o fallido
import os

# ===============================
CURRENT_DIR = os.getcwd()
# ===============================


class GetFEData(luigi.Task):

	def output(self):
		dir = CURRENT_DIR + "/target/get_fe.txt"
		return luigi.local_target.LocalTarget(dir)

	def run(self):
		z = "Hola"
		with self.output().open('w') as output_file:
			output_file.write(z)
