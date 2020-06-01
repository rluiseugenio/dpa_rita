# Retrasos en vuelos de la base de datos RITA

**Este proyecto automatizan la predicción de retrasos o cancelaciones de los
vuelos de la base de datos denominada conocida como [RITA](http://stat-computing.org/dataexpo/2009/the-data.html) (ver también [transtats.bts.gov](https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp))**. Esta base agrupa una serie de datos de vuelos que incluyen salidas a tiempo, llegadas a tiempo, demoras, vuelos cancelados de todo Estados Unidos del Departamento de Transporte. Dado que los tiempos de viaje de los usuarios se encuentran sujetos a la disponibilidad y viabilidad de los vuelos de las aerolíneas comerciales, los cuales a su vez se encuentran estrechamente ligados a otros factores (por ejemplo, políticas comerciales, incidentes de seguridad o eventos climáticos), los pasajeros experimentan cierto nivel de incertidumbre sobre si sus vuelos serán retrasados o cancelados en definitiva. La automatización de las predicciones como se plantean en este proyecto permite no solo que los usuarios prevean la administración de su tiempo al realizar viajes, sino que puedan diseñar estrategias que les permita continuar con su viaje en caso de una probable cancelación de un vuelo.

## Tabla de contenidos

1. [Introducción](https://github.com/dssg/usal_echo#introduction)
2. [Overview](https://github.com/dssg/usal_echo#overview)
3. [Requerimientos de infraestructura](https://github.com/dssg/usal_echo#infrastructure-requirements)
4. [Instalación y setup](https://github.com/dssg/usal_echo#installation-and-setup)
5. [Corriendo el Pipeline](https://github.com/dssg/usal_echo#run-the-pipeline)
6. [Organización del código](https://github.com/dssg/usal_echo#code-organisation)
7. [Contributors](https://github.com/dssg/usal_echo#contributors)

## Introducción

### Proyecto de arquitectura de producto de datos.
Este proyecto se desarrolla en el marco de la materia arquitectura de producto
de datos impartida por Msc. Liliana Millán Nuñez, como parte del programa de
maestría en Ciencia de Datos del Instituto Tecnológico Autónomo de México, para
 el primer semestre de 2020.

## Overview

El proceso de predicción  de retrasos o cancelaciones de los vuelos se basa
fundamentalmente en las siguientes ideas:

1. **Predicción en retrasos** basada en intervalos que indican la cantidad de horas
 de retraso en un vuelo; a saber de i) 0 a 1.5 horas de retraso, ii) 1.5 a 3.5
 horas de retraso, y iii) más de 3.5 horas de retraso.
2. **Cancelación** representado como una variable binaria que indica si un vuelo
fue o no cancelado.
3. Calculo de medidas de **bias** y **fairness**: [Pendiente: descripción].

Nuestro pipeline ha sido diseñado para funcionar de forma modular usando la
librería *Luigi* de Python, considerando la ingestión de datos, su limpieza,
creación de nuevas *features* así como predicción se pueden ejecutar de manera
independientemente.

El pipeline descrito corresponde a la siguiente estructura:

![USAL Echo Project Overview](docs/images/usal_echo_pipeline_overview.png?raw=true "USAL Echo Project Overview")

## Requerimientos de infraestructura

Para el manejo y procesamiento de los datos este projecto usa infraestructura en
 la nube basada en servicios de Amazon Web Services (AWS). Concretamente, se
 emplean dos buckets de AWS S3 (denominados **) y una instancia AWS EC2 para ejecutar todo el
 código. Los resultados para cada capa de procesamiento se almacenan en un base
 de datos basada en PostgreSQL en AWS RDS.

```
Infraestructura: AWS

+ AMI: ami-085925f297f89fce1 (64-bit x86), Ubuntu Server 18.04 LTS (HVM), SSD Volume Type
+ instancia EC2: t2.large
      GPU: 1
      vCPU: 2
      RAM: 8 GB
+ OS: Ubuntu 18.04 LTS
+ RDS:
    Engine: PostgreSQL
    Engine version: 11.5
    instancia: db.t2.micro
    vCPU: 1
    Ram: 20 GB
    Almacenamiento: 1000 GB
```

## Instalación y setup

#### 0. Requerimientos

[Pendiente: Leon documentar como conectarse al bastión via SSH y la estructura]


Considerando lo anterior, dentro de bastión se de contar con docker:

```
sudo apt update
sudo apt-get install docker.io git
```


[Pendiente: Leon documentar estructura de carpetas]

#### 1.

Clone the TensorFlow Python3 conda environment in your GPU instance set up with AWS Deep Learning AMI and activate it.
```
conda create --name usal_echo --clone tensorflow_p36
echo ". /home/ubuntu/anaconda3/etc/profile.d/conda.sh" >> ~/.bashrc
source ~/.bashrc
conda activate usal_echo
```

#### 2. Clone and setup repository
After activating your Anaconda environment, clone this repository into your work space. Navigate to `usal_echo` and install the required packages with pip. Then run the setup.py script.
```
git clone https://github.com/dssg/usal_echo.git
cd usal_echo
pip install -r requirements.txt
python setup.py install
```

#### 3. Credentials files
To run the pipeline, you need to specify the credentials for your aws and postgres infrastructure. The pipeline looks for credentials files in specific locations. You should create these now if they do not already exist.

##### aws credentials   
Located in `~/.aws/credentials` and formatted as:
```
mkdir ~/.aws
nano ~/.aws/credentials

# Then paste the access id and key below into the file

[default]
aws_access_key_id=your_key_id
aws_secret_access_key=your_secret_key
```
The pipeline uses the `default` user credentials.

##### postgres credentials  
Modify the postgres credentials in `~/usr/usal_echo/conf/local/postgres_credentials.json`. This file must exist to run the pipeline. An example is created during setup and you must modify it for your configuration.
```
cd ~/usr/usal_echo/conf/
nano postgres_credentials.json

# Then modify the postgres credentials below into the file

{
"user":"your_user",
"host": "your_server.rds.amazonaws.com",
"database": "your_database_name",
"psswd": "your_database_password"
}
```

#### 4. Specify data paths
The parameters for the s3 bucket and for storing dicom files, images and models must be stored as a yaml file in `~/usr/usal_echo/conf/path_parameters.yml`. This file must exist to run the pipeline. An example is created during setup and you must modify it for your configuration.

```
cd ~/usr/usal_echo/conf/
nano path_parameters.yml

# Then modify the paths below in the file

bucket: "your_s3_bucket_name"
dcm_dir: "~/data/01_raw"
img_dir: "~/data/02_intermediate"
segmentation_dir: "~/data/04_segmentation"
model_dir: "~/models"
classification_model: "model.ckpt-6460"
```

The `dcm_dir` is the directory to which dicom files will be downloaded. The `img_dir` is the directory to which jpg images are saved. The `model_dir` is the directory in which models are stored. The classification and segmentation models must be saved in the `model_dir`. Use `~/` to refer to the user directory.

#### 5. Download models
The models used to run this pipeline can be downloaded from s3:  
* [classification](): original from Zhang et al, adapted to our dataset using transfer learning.
* [segmentation](): original from Zhang et al without adaptation

They need to be saved in the `model_dir` that you have specified above, and that `model_dir` needs to already have been created.

#### 6. Create the database schema
As per the requirements listed in [Infrastructure requirements](https://github.com/dssg/usal_echo#infrastructure-requirements) you require a database indtallation with credentials stored as described above. After the database has been created, you need to run the script that creates the different schema that we require to persist the outputs from the different pipeline processes: classification, segmentation and measurements. The database schema is stored in `usr/usal_echo/conf/models_schema.sql` and must be set up by running the following command (change psswd, user, database and host to correspond with your setup):
```
PGPASSWORD=psswd psql -U user -d database_name -h host -f '/home/ubuntu/usr/usal_echo/conf/models_schema.sql'
```

## Run the pipelineent

The final step is to run the `inquire.py` script which can be called from within the `usal_echo` directory using the short cut usal_echo:
```
usal_echo
```

Running `usal_echo` will launch a questionnaire in your command line that takes you through the setup options for running the pipeline. The options are discussed in detail below.

### Pipeline options
To navigate through the options in the command line prompt hit `spacebar` to check or uncheck multiple choice options and `Enter` to select an option. Navigate between options with the `up` and `down` arrows. You can abort the process with `Ctrl+C`.

#### Data ingestion
Select to ingest or not to ingest dicom metadata and the Xcelera database. **NB: ingesting the dicom metadata for 25 000 studies takes ~3 days!**

<p align="left">
<img src="docs/images/inquire_ingest.png" alt="Run pipeline: ingest." width="450" />
</p>

This step includes the following subprocesses:

##### dicom metadata
```
d01_data.ingestion_dcm.ingest_dcm(bucket)
d02_intermediate.clean_dcm.clean_dcm_meta()
```

##### Xcelera data
```
d01_data.ingestion_xtdb.ingest_xtdb(bucket)
d02_intermediate.clean_xtdb.clean_tables()
d02_intermediate.filter_instances.filter_all()
```

#### Dicom image download
This step downloads and decompresses the dicom files. The files to download are determined based on the test/train split ratio and downsample ratio, both of which must be specified if this option is selected.

If `Train test ration = 0`, then all the files are downloaded into the test set.  
If `Train test ratio = 1`, then no files are downloaded into the test set.
If `Downsample ratio = 1`, no downsampling is done.
If `0 < Downsample ratio < 1`, then are portion of files corresponding to the downsample ratio is downloaded.

<p align="left">
<img src="docs/images/inquire_download.png" alt="Run pipeline: download." width="450" />
</p>

The download step executes the following function:
```
d02_intermediate.download_dcm.s3_download_decomp_dcm(train_test_ratio, downsample_ratio, dcm_dir, bucket=bucket)
```
`s3_download_decomp_dcm` executes two processing steps: it downloads files from s3 and then decompresses them. If you already have a directory with dicom files that are not decompressed, you can use `d02_intermediate.download_dcm._decompress_dcm()` to decompress your images. The convention is that decompressed images are stored in a subdirectory of the original directory named `raw` and that filenames are appended with `_raw` to end in `.dcm_raw`.

The naming convention for downloaded files is the following: _test_split[**ratio * 100**]\_downsampleby[**inverse ratio**]_. For example, if `Train test ratio = 0.5` and `Downsample ratio = 0.001` the directory name will be _test_split50_downsampleby1000_.

#### Module selection
Select one or more modules for inference and evaluation.

<p align="left">
<img src="docs/images/inquire_classification.png" alt="Run pipeline: classification." width="700" />
</p>

The following functions are executed in each module. `dir_name` is the directory specified in the next step. `dcm_dir` and `img_dir` are specified in _path_paramters.yml_:

##### classification
```
img_dir_path = os.path.join(img_dir, dir_name)
dcmdir_to_jpgs_for_classification(dcm_dir, img_dir_path)
d03_classification.predict_views.run_classify(img_dir_path, classification_model_path)
d03_classification.predict_views.agg_probabilities()
d03_classification.predict_views.predict_views()
d03_classification.evaluate_views.evaluate_views(img_dir_path, classification_model)
```

##### segmentation
```
dcm_dir_path = os.path.join(dcm_dir, dir_name)
d04_segmentation.segment_view.run_segment(dcm_dir_path, model_dir, img_dir_path, classification_model)
d02_intermediate.create_seg_view.create_seg_view()
d04_segmentation.generate_masks.generate_masks(dcm_dir_path)
d04_segmentation.evaluate_masks.evaluate_masks()
```

##### measurements
```
d05_measurement.retrieve_meas.retrieve_meas()
d05_measurement.calculate_meas.calculate_meas(dir_name)
d05_measurement.evaluate_meas.evaluate_meas(dir_name)
```

#### Specification of image directory
Finally, specify the name of the directory which contains the dicom files and images (ie the name of the subdirectory in `dcm_dir` and `img_dir` that contains the data you want to access). It is important that these two subdirectories have the same name, as the classification module accesses the `img_dir` while the segmentation module accesses the `dcm_dir`.

<p align="left">
<img src="docs/images/inquire_dir.png" alt="Run pipeline: specify directory." width="450" />
</p>

### Log files
The log files are stored in `~/usr/usal_echo/logs`.

### Notebooks
A set of notebooks exists in the `notebooks` directory of this repository. They contain the functions for each of the pipeline steps, as well as some elementary data analysis and can be used to experiment.

## Code organisation
The code is organised as follows:
1. `d00_utils`: Utility functions used throughout the system
2. `d01_data`: Ingesting dicom metadata and XCelera csv files from s3 into database
3. `d02_intermediate`: Cleaning and filtering database tables, downloading, decompressing and extracting images from dicom files for experiments
4. `d03_classification`: Classification of dicom images in image directory
5. `d04_segmentation`: Segmentation of heart chambers
6. `d05_measurements`: Calculation of measurements from segmentations
7. `d06_visualisation`: Generating plots for reporting

## Contributors

**Technical mentors:** Danahi Ayzailadema Ramos Martínez, Paola Mejía Domenzaín, León Manuel Garay Vásquez, Luis Eugenio Rojón Jiménez y Cesar Zamora Martínez
