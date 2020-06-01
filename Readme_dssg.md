# Retrasos en vuelos de la base de datos RITA

**Este proyecto automatizan la predicción de retrasos o cancelaciones de los
vuelos de la base de datos denominada conocida como [RITA](http://stat-computing.org/dataexpo/2009/the-data.html) (ver también [transtats.bts.gov](https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp))**. Esta base agrupa una serie de datos de vuelos que incluyen salidas a tiempo, llegadas a tiempo, demoras, vuelos cancelados de todo Estados Unidos del Departamento de Transporte. Dado que los tiempos de viaje de los usuarios se encuentran sujetos a la disponibilidad y viabilidad de los vuelos de las aerolíneas comerciales, los cuales a su vez se encuentran estrechamente ligados a otros factores (por ejemplo, políticas comerciales, incidentes de seguridad o eventos climáticos), los pasajeros experimentan cierto nivel de incertidumbre sobre si sus vuelos serán retrasados o cancelados en definitiva. La automatización de las predicciones como se plantean en este proyecto permite no solo que los usuarios prevean la administración de su tiempo al realizar viajes, sino que puedan diseñar estrategias que les permita continuar con su viaje en caso de una probable cancelación de un vuelo.

## Tabla de contenidos

1. [Introducción](https://github.com/dssg/usal_echo#introduction)
2. [Consideraciones](https://github.com/dssg/usal_echo#overview)
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

## Consideraciones

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



**Metadatos**

En complemento a lo anterior, en la base de datos PostgreSQL alojada en AWS RDS
se incorporan una serie de tablas que reúnen los metadatos generados en cada una
de las etapas del pipeline, que para mejor referencia se resumen a continuación:

| Tabla       | Descripción de metadatos                                                                                            |
|-------------|---------------------------------------------------------------------------------------------------------------------|
| "extract"   | Información extraída de la pagina electrónica de Rita, en archivos .zip correspondientes a un mes y año específicos |
| load        | Corresponde a los datos que se cargan hacia RDS en esquema raw                                                      |
| clean       | Relativo a la información de la etapa de limpieza de los datos desde el esquema raw                                 |
| semantic    | Reúne la información de la etapa de feature engineering con vista hacia el modelado predictivo                                                                                                                          |
| models      | Incorpora los metadatos de la etapa de modelado                                                                     |
| bias        | Reúne la información de bias de los modelos predictivos                                                             |
| predictions | Considera la información generada para realizar predicciones                                                        |

**Consideraciones éticas**

Se identificaron posibles implicaciones éticas del producto de datos materia de este proyecto

**Eje de usuarios:**

* Hacer que pierdan vuelos y deban hacer doble gasto en un viaje,
* Sesgar a que los usuarios viajen o no en una aerolínea,

**Eje de aerolíneas:**

* Perjudicar la reputación  de una aerolínea,
* Proyectar la responsabilidad de eventos fuera de su control,
* Dañar su estabilidad económica y empleos,
* Aumentar quejas injustificadas del servicio.


## Requerimientos de infraestructura

Para el manejo y procesamiento de los datos este proyecto usa infraestructura en
 la nube basada en servicios de Amazon Web Services (AWS). Concretamente, se
 emplean tres buckets de AWS S3 (denominados *models-dpa*, ) y una instancia AWS EC2 para ejecutar todo el
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

Para conectarse hacia la máquina virtual que servirá como bastión:

```
ssh -i mi-llave.pub ubuntu@endopoint-de-mi-instancia
```

Considerando lo anterior, dentro de bastión se de contar con docker:

```
sudo apt update
sudo apt-get install docker.io git
```


[Pendiente: Leon documentar estructura de carpetas]

```
mkidr [alguna carpeta]
```


#### 1.

Clone the TensorFlow Python3 conda environment in your GPU instance set up with AWS Deep Learning AMI and activate it.
```
conda create --name usal_echo --clone tensorflow_p36
echo ". /home/ubuntu/anaconda3/etc/profile.d/conda.sh" >> ~/.bashrc
source ~/.bashrc
conda activate usal_echo
```

#### 2. Clonar el repositorio de github

Para clonar el repositorio de trabajo del proyecto ejecutar:

```
mkdir dpa_rita
cd dpa_rita
git clone https://github.com/paola-md/dpa_rita/
```

#### 3. Archivos de credenciales

Para ejecutar el pipeline, se deben especificar las credenciales para su infraestructura en AWS y postgres, puesto que el primero busca archivos de credenciales en ubicaciones específicas. Debería crearlos ahora si aún no existen

##### aws credentials   
Se ubican en `~/.aws/credentials` y deben ser generadas como sigue
```
mkdir ~/.aws
nano ~/.aws/credentials

# Luego se debe pegar la identificación de acceso y la clave a
# continuación en dicho archivo
[dpa]
aws_access_key_id=your_key_id
aws_secret_access_key=your_secret_key
```
El pipeline usa las credenciales del usuario `dpa`.

##### Credenciales de postgres

Modifique las credenciales de postgres en `.rita/conf/path_parameters.yml`. Este archivo debe existir para ejecutar el pipelone. Se crea un ejemplo durante la instalación y debe modificarlo para su configuración.
```
cd .rita/conf/
nano path_parameters.yml

# Modifa la informacion en estas líneas

user: "postgres"
password : "mi-password"
host : "mi-endpoint-de-rds"
port : "5432"
database: "postgres"
```

#### 4. Specify data paths

pendiente

#### 5. Crear el esquema de las bases de datos

As per the requirements listed in [Infrastructure requirements](https://github.com/dssg/usal_echo#infrastructure-requirements) you require a database indtallation with credentials stored as described above. After the database has been created, you need to run the script that creates the different schema that we require to persist the outputs from the different pipeline processes: classification, segmentation and measurements. The database schema is stored in `usr/usal_echo/conf/models_schema.sql` and must be set up by running the following command (change psswd, user, database and host to correspond with your setup):
```
PGPASSWORD=psswd psql -U user -d database_name -h host -f '/home/ubuntu/usr/usal_echo/conf/models_schema.sql'
```

## Correr el pipeline

The final step is to run the `inquire.py` script which can be called from within the `usal_echo` directory using the short cut usal_echo:
```
usal_echo
```

Running `usal_echo` will launch a questionnaire in your command line that takes you through the setup options for running the pipeline. The options are discussed in detail below.

### Pipeline options
To navigate through the options in the command line prompt hit `spacebar` to check or uncheck multiple choice options and `Enter` to select an option. Navigate between options with the `up` and `down` arrows. You can abort the process with `Ctrl+C`.

### Notebooks
Existe un conjunto de cuadernos en el directorio `notebooks` de este repositorio. Contienen las funciones para cada uno de los pasos de la tubería, así como algunos análisis de datos elementales y se pueden usar para experimentar.

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
