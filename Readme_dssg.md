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

![Diagrama de flujo del ELT](reports/figures/ETL.jpeg?raw=true "Title")

En la etapa de Extract, se descargan los datos de Rita a través de un task de Luigi, posteriormente en la etapa de Load los datos se transforman a csv en la instancia y se guardan en una tabla de la RDS llamada raw.rita a través de un task de Luigi, finalmente en la etapa Transform los datos se extraen de la tabla raw.rita y son limpiados dando formato a columnas y eliminando columnas vacías guardandose en la tabla clean.rita de la RDS a través de un task Luigi. De cada etapa se realizan dos pruebas unitarias y se genera una tabla de metadata.


![Diagrama de flujo de Modelado](reports/figures/Models.jpeg?raw=true "Title")

Para la etapa de modelado los datos se obtienen de la tabla clean.rita de la RDS, posteriormente se realiza feature engineering creándose y transformándose nuevas variables y se guardan en la tabla semantic.rita a través de un task de luigi,a continuación  se realizan dos pruebas unitarias y se genera metadata. Una vez obteniéndose los datos de la tabla semantic.rita se realiza la generación de modelos, una vez elegido el mejor modelo se mide el bias y fairness del modelo y se genera metadata. Posteriormente se realizan las predicciones y de estas se realizan dos pruebas unitarias y se genera metadata. Una vez obtenidas las predicciones se envían a una tabla de la RDS llamada predictions.test. Finalmente con las tablas de prediction.test y de la metadata de las precicciones genera una API y un dashboard.


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

Considerando lo anterior, se necesita un par de herramientas adicionales:

```
sudo apt update
sudo apt-get install docker.io git
```

Se crean las siguientes carpetas en las cuales estarán las credenciales necesarias para correr el proyecto.

```
mkidr ~/.aws
mkdir ~/.rita
mkdir ~/.rita/conf ~/.rita/keys ~/.rita/logs
mkdir dpa_rita
```
#### 1. Guardar llaves secretas
Para re-utilizar las credenciales de la base de datos, de la región de las cubetas y otras configraciones de AWS al igual que para homogeneizar los nombres en todos los archivos creamos el archivo path_parameters.yml


cd $HOME
nano path_parameters.yml

# Este es un pequeño ejemplo

bucket: "un nombre"
region: "us-east-1"
profile: "dpa"
key: 'ec2-keypair'
ami: "ami-0d1cd67cxxxxxxxx"
vpc: "vpc-0cffc8f1xxxxxxxx"
gateway: "igw-08da14e5xxxxxxxx"
subnet: "subnet-087d35xxxxxxxx"
group: "sg-0fa1c8589xxxxxxxx"
user: "postgres"
password : "xxxxxxxx"
host : "xxxxxxxx.us-east-1.rds.amazonaws.com"
port : "5432"
database: "postgres"

#### 2.

Clone the TensorFlow Python3 conda environment in your GPU instance set up with AWS Deep Learning AMI and activate it.
```
conda create --name usal_echo --clone tensorflow_p36
echo ". /home/ubuntu/anaconda3/etc/profile.d/conda.sh" >> ~/.bashrc
source ~/.bashrc
conda activate usal_echo
```

#### 3. Clonar el repositorio de github

Para clonar el repositorio de trabajo del proyecto ejecutar:

```
cd dpa_rita
git clone https://github.com/paola-md/dpa_rita/
```

#### 4. Archivos de credenciales

Para ejecutar el pipeline, se deben especificar las credenciales para su infraestructura en AWS y postgres, puesto que el primero busca archivos de credenciales en ubicaciones específicas. Debería crearlos ahora si aún no existen

##### aws credentials   
Se ubican en `~/.aws/credentials` y deben ser generadas como sigue
```

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

# Modifica la información en estas líneas

user: "postgres"
password : "mi-password"
host : "mi-endpoint-de-rds"
port : "5432"
database: "postgres"
```

#### 4. Docker

La ejecución del proyecto se basa en una imagen de Docker que permite emplear
[PySpark](https://spark.apache.org/docs/latest/api/python/pyspark.html), con lo
cual es necesario configuraciones de la misma.

**4.1 Declaramos variables**

En la terminal del bastión ingresamos:

```
VERSION=6.0.1
REPO_URL=paolamedo/aws_rita
BUILD_DIR=/home/ubuntu/dpa_rita
```

**4.2 Descargamos la imagen del repositorio del proyecto en Dockerhub**

Posteriormente descargamos de Dockerhub la imagen de Docker del proyecto que nos
permitirá usar PySpark.

```
docker pull $REPO_URL:$VERSION
```

**4.3 Acceder a la instancia y encender el demonio de Luigi**

El siguiente comando nos dará acceso a una terminal de la instancia de Docker que
permite usar PySpark y además monta los archivos del repositorio de Github para
ejecutar el pipeline.

```
sudo docker run --rm -it \
-v $BUILD_DIR:/home  \
-v $HOME/.aws:/root/.aws:ro  \
-v $HOME/.rita:/root/.rita \
--entrypoint "/bin/bash" \
--net=host \
$REPO_URL:$VERSION
```

Una vez en dicha istancia de docker nos desplazaremos para activar el demonio de
Luigi:

```
cd home
luigid # Activamos el demonio de luigi
```

**4.4 Acceder a más terminales de la instancia de docker**

Es posible acceder con más terminales del bastión a la instancia de Docker que
se ha levantando previamente, emplea el id de ésta que se deriva del comando:

```
docker ps # obtenemos el id del instancia (<id-de-instancia>)
```

Así, para acceder a una nueva terminal que refleje la instancia de nuestro contenedor
basta con usar el comando siguiente:

```
docker exec -it <id-de-instancia> /bin/bash
```

**4.5 Forwardear scheduler de Luigi hacia maquina local**

Para poder visualizar el scheduler del pipeline que correremos con Luigi, es
necesario hacer el portforwarding del puerto 8082 del bastión hacia la máquina
local en donde estamos trabajando. Para tal efecto se debe ejecutar el comando:

```
# Modificar el contenido con los datos de la llave ssh y endpoint del bastion
ssh -i <mi-llave.pem> -N -f -L localhost:8082:localhost:8082 ubuntu@<mi-endpoint>
```

Así en nuestra máquina local debemos abrir un navegador empleando la dirección:

```
localhost:8082
```


#### 5. Creación de esquemas en base de datos

Según los requisitos enumerados en [Requisitos de infraestructura] (https://github.com/dssg/usal_echo#infrastructure-requirements), necesita una instalación de la base de datos de nombre postgres con credenciales.

**5.1 Archivo de credenciales**

Dentro de una terminal que refleje la instancia del contenedor de Docker del
proyecto (ver numeral 4.4) es necesario editar el archivo `.pg_service.conf`
para que `psql` reconozca las credenciales, para ello
se debe seguir el procedimiento siguiente:

```
nano .pg_service.conf

# Modificar el contenido de abajo segun corresponda
[rita]
host=<endopoint-de-mi-base>
port=5432
user=postgres
password=<mi-password>
dbname=postgres

```

**5.2 Creación de esquema con psql**

Para la creación de los respectivos esquemas, ahora se ejecutarán mediante
`psql` una serie de scripts:

```
cd /home/src/utils/sql
psql service=rita -f 'crear_tablas.sql'
psql service=rita -f 'create_predict_tables.sql'
psql service=rita -f 'create_predict_tables.sql'
```

## Correr el pipeline

La siguiente instrucción se debe ejecutar para cargar la libraria src con los archivos del proyecto.

python3 setup.py install


A continuación, dentro de la carpeta orquestadores se corre el pipeline.

cd src/orquestadores


Existen dos vertientes, una para entrenar y otra para predecir. El parámetro type indica cual rama correr. La rama de predict, requiere que se haya entrenado (type = train) con los datos y se haya guardado un modelo.

Rama para entrenar:

PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline  --type train


Rama para predecir:

PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline  --type predict


### Notebooks
Existe un conjunto de cuadernos en el directorio `notebooks` de este repositorio. Contienen las funciones para cada uno de los pasos de la tubería, así como algunos análisis de datos elementales y se pueden usar para experimentar.

## Code organization
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
