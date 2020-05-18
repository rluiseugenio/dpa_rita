
class LocalHelper():
    def __init__(self, values = "None"):
        self.values = values

metadata = LocalHelper()

class SaveMetadataBias(CopyToTable):
    def requires(self):
        return EvaluateBias()

    x = luigi.IntParameter()

    # Lectura de archivo de credenciales
    user = MY_USER
    password = MY_PASS
    database = MY_DB
    host = MY_HOST

    table = 'metadatos.bias'

    columns = [("x", "VARCHAR"),
               ("y", "VARCHAR")]

    def rows(self):
        z = str(self.x + self.x)
        print("########### ", z)
        r = [("test 1", z), ("test 2","45")]
        for element in r:
            yield element


class EvaluateBias(luigi.Task):

	def requires(self):
		return RunModelSimple()

	def output(self):
		objetivo = self.obj
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		output_path = parse_filename(objetivo, model_name, hyperparams)
		output_path = "s3://" + str(self.bucname) +  output_path[1:] + ".model.zip"

		return luigi.contrib.s3.S3Target(path=output_path)

	def run(self):
		objetivo = self.obj
		model_name = self.model
		hyperparams = {"iter": int(self.numIt),
						"pca": int(self.numPCA)}

		run_model(objetivo, model_name, hyperparams, True)
