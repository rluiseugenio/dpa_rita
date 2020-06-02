# Retrasos en vuelos de la base de datos RITA

**Este proyecto automatiza la predicción de retrasos o cancelaciones de los
vuelos de la base de datos denominada conocida como [RITA](http://stat-computing.org/dataexpo/2009/the-data.html) (ver también [transtats.bts.gov](https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp))**. Dicha base agrupa una
serie de datos de vuelos que incluyen salidas a tiempo, llegadas a tiempo,
demoras, vuelos cancelados de todo Estados Unidos del Departamento de
Transporte. Dado que los tiempos de viaje de los usuarios se encuentran sujetos
a la disponibilidad y viabilidad de los vuelos de las aerolíneas comerciales,
los cuales a su vez se encuentran estrechamente ligados a otros factores (por
  ejemplo, políticas comerciales, incidentes de seguridad o eventos climáticos),
   los pasajeros experimentan cierto nivel de incertidumbre sobre si sus vuelos
   serán retrasados o cancelados en definitiva. La automatización de las
   predicciones como se plantean en este proyecto permite no solo que los
   usuarios prevean la administración de su tiempo al realizar viajes, sino que
   puedan diseñar estrategias que les permita continuar con su viaje en caso de
   una probable cancelación de un vuelo.

## Tabla de contenidos

1. [Introducción](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#introducción)
2. [Consideraciones](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#consideraciones)
3. [Requerimientos de infraestructura](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#requerimientos-de-infraestructura)
4. [Instalación y setup](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#instalación-y-setup)
5. [Corriendo el Pipeline](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#correr-el-pipeline)
6. [Organización del proyecto](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#organización-del-proyecto)
7. [Contributors](https://github.com/paola-md/dpa_rita/blob/master/Readme.md#contributors)

## Introducción

### Proyecto de arquitectura de producto de datos.
Este proyecto se desarrolla en el marco de la materia arquitectura de producto
de datos impartida por Msc. Liliana Millán Nuñez, como parte del programa de
maestría en Ciencia de Datos del Instituto Tecnológico Autónomo de México, para
 el primer semestre de 2020.

 ### Sobre base de datos RITA

 Como se ha mencionado previamente, el interés de este proyecto gira en torno a
 la base de datos denominada conocida como RITA, la cual provee una serie de
 datos de vuelos que incluyen salidas a tiempo, llegadas a tiempo, demoras,
 vuelos cancelados de todo Estados Unidos del Departamento de Transporte,
 poseyendo una frecuencia de actualización mensual, con datos históricos desde
 junio del 2003.

Ahora bien, dado que los tiempos de viaje de los usuarios se encuentran sujetos
a la disponibilidad y viabilidad de los vuelos de las aerolíneas comerciales,
los cuales a su vez se encuentran estrechamente ligados a otros factores (por
ejemplo, políticas comerciales, incidentes de seguridad o eventos climáticos),
los pasajeros experimentan cierto nivel de incertidumbre sobre si sus vuelos
serán retrasados o cancelados en definitiva. Una forma de poder atacar la
incertidumbre de los viajeros, sería contar con una sistema que pueda dar
elementos a los usuarios acerca de 1) si existirá retraso en su vuelo, 2) en
caso de que exista retraso, pueda informar el lapso de tiempo equivalente a
dicho evento, o 3) indique si su vuelo se cancelará. Esto permitirá no solo que
los usuarios prevean la administración de su tiempo al realizar viajes, sino que
 puedan diseñar estrategia que les permita continuar con su viaje en caso de una
  probable cancelación de un vuelo.

Con ello en mente, el problema que pretende abordar el presente proyecto, a
través del desarrollo de producto de datos, es la incertidumbre de los viajeros
ante retraso en los vuelos, siendo la pregunta que guía el proyecto es ¿que
intervalo de tiempo se va a retrasar mi vuelo, o si bien será cancelado?. El
objetivo, por tanto, será desarrollar un sistema que permita predecir retrasos
en vuelos de forma precisa para que los viajeros puedan planear su agenda de
viaje de acuerdo a los probables retrasos o cancelaciones de las aerolíneas.
Este sistema estará dirigido a los pasajeros de la aerolínea. Es decir, el
público en general que va a viajar dentro de Estados Unidos.

## Consideraciones

El proceso de predicción  de retrasos o cancelaciones de los vuelos se basa
fundamentalmente en las siguientes ideas:

1. **Predicción en retrasos** basada en intervalos que indican la cantidad de horas
 de retraso en un vuelo; a saber de i) 0 a 1.5 horas de retraso, ii) 1.5 a 3.5
 horas de retraso, y iii) más de 3.5 horas de retraso.
2. **Cancelación** representado como una variable binaria que indica si un vuelo
fue o no cancelado.
3. Calculo de medidas de **bias** y **fairness**: se considera como variable
protegida a la distancia recorrida por los vuelos, empleando la métrica
**False Positive Parity**.

Nuestro pipeline ha sido diseñado para funcionar de forma modular usando la
librería *Luigi* de Python, considerando la ingestión de datos, su limpieza,
creación de nuevas *features* así como predicción se pueden ejecutar de manera
independientemente.

El pipeline descrito corresponde a la siguiente estructura:

![Diagrama de flujo del ELT](reports/figures/ETL.jpeg?raw=true "Title")

En la etapa de Extract, se descargan los datos de Rita a través de un task de
Luigi, posteriormente en la etapa de Load los datos se transforman a csv en la
instancia y se guardan en una tabla de la RDS llamada raw.rita a través de un
task de Luigi, finalmente en la etapa Transform los datos se extraen de la tabla
 raw.rita y son limpiados dando formato a columnas y eliminando columnas vacías
 guardándose en la tabla clean.rita de la RDS a través de un task Luigi. De cada
  etapa se realizan dos pruebas unitarias y se genera una tabla de metadata.


![Diagrama de flujo de Modelado](reports/figures/Models.jpeg?raw=true "Title")

Para la etapa de modelado los datos se obtienen de la tabla clean.rita de la
RDS, posteriormente se realiza feature engineering creándose y transformándose
nuevas variables y se guardan en la tabla semantic.rita a través de un task de
Luigi, a continuación  se realizan dos pruebas unitarias y se genera metadata.
Una vez obteniéndose los datos de la tabla semantic.rita se realiza la
generación de modelos, una vez elegido el mejor modelo se mide el bias y
fairness del modelo y se genera metadata. Posteriormente se realizan las
predicciones y de estas se realizan dos pruebas unitarias y se genera metadata.
Una vez obtenidas las predicciones se envían a una tabla de la RDS llamada
predictions.test. Finalmente con las tablas de prediction.test y de la metadata
de las predicciones genera una API y un dashboard.

Para facilitar el entendimiento de las etapas recién descritas a continuación
se presentan los esquemas de tablas de RDS que involucran en el proyecto:


| Tabla             | Descripción                                                                                                                                                                                             |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| raw.rita          |                                                                       Reune la Informacion de la base de datos Rita, sin procesar.                                                                      |
| clean.rita        | Corresponde al procesamiento de la información de la tabla raw.rita para limpieza de los datos (considerando transformaciones tales como pasar a minúsculas, eliminar estaciones, guiones, entre otros  |
| semantic.rita     |                                Relativa a la etapa de feature engineering, donde se consolidad variables útiles para los ejercicios de predicción materia de este modelo                                |
| predictions.train |                                                                      Tabla que reúne las predicciones de retraso o la cancelación del vuelo de los datos de entrenamiento                                                                     |
| models            |                                                                         Tabla que reúne las predicciones de los datos de prueba                                                                         |

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


**Pruebas unitarias**

Para asegurar la consistencia y robustez del proyecto, el diseño del pipeline consideró una serie de pruebas unitarias entre las que destacan:

* **Prueba de extracción/carga:** verifica si los csv descargados de RITA tienen el número esperado de columnas (180)
* **Prueba de consistencia de columnas tras limpieza:** comprueba que la cantidad de columnas en clean.rita sean las esperadas
* **Prueba de creación de categorías de rango de horas de retraso:** prueba verifica que los valores de la columna *rangoatrashoras* sean los indicados.
* **Prueba Semantic:** comprueba que la cantidad de columnas en semantic.rita sean las esperadas.

Al respecto, también se guardan metadatos de todas las pruebas unitarias, tal
como se listan a continuación:

* metadatos.testing_load,
* metadatos.testing_clean_columns,
* metadatos.testing_clean_rangos,
* metadatos.testing_semantic,
* metadatos.testing_predict_types,
* metadatos.testing_predict_cols

**Consideraciones éticas**

Se identificaron posibles implicaciones éticas del producto de datos materia de este proyecto

*Eje de usuarios:*

* Hacer que pierdan vuelos y deban hacer doble gasto en un viaje,
* Sesgar a que los usuarios viajen o no en una aerolínea,

*Eje de aerolíneas:*

* Perjudicar la reputación  de una aerolínea,
* Proyectar la responsabilidad de eventos fuera de su control,
* Dañar su estabilidad económica y empleos,
* Aumentar quejas injustificadas del servicio.

**Consideraciones sobre Bias y Fairness**

Tomando en cuenta las implicaciones éticas, se seleccionó la *distancia* como variable protegida, con lo cual el objetivo es que el modelo haga predicciones justas sin importar que el vuelo sea corto o largo. En este sentido, al ser dicha variable continua, se estimó pertinente dividirla en quartiles para su análisis.

Dado que uno de los objetivos de este proyecto es predecir el retraso de un vuelo, tras el análisis se identificó realizó una valoración de las consecuencias negativas de tener un falso positivo (esto es, predecir que un vuelo se va a retrasar, cuando en los hechos no sucede), estimándose que son muchas más graves que en un falso negativo (predecir que un vuelo no se va a retrasar y que se retrase). Ello en razón de que el hecho de que un usuario espere tiempo extra en el aeropuerto redunda en menos costos de que no llegué a su vuelo porque tuvo información inexacta de que se iba a retrasar. Es por eso que cobran interés los falsos positivos más que los falsos negativos.

Como consecuencia, la métrica que nos interesa es *False Positive Parity* porque queremos que todas las zonas geográficas de Estados Unidos y grupos de distancia tengan el mismo FPR (false positive rate). Es decir, presentar equivocaciones en las mismas proporciones para etiquetas positivas que eran negativas.

Para el proyecto se escogió esta métrica ya que se necesita que el modelo a desarrollar sea bueno detectando la etiqueta positiva y no hay (mucho) costo en introducir falsos negativos al sistema. El costo de un falso negativo es que usuarios esperen en el aeropuerto a su vuelo retrasado y este sería el status-quo sin el modelo o producto de datos. Asimismo, ésta se consideró adecuada toda vez la variable *target* no es subjetiva: si un vuelo se retrasa sabemos exactamente cuánto se retrasó y no depende de la percepción del usuario.

![False Positive Parity Distancia](reports/figures/fpr_distance.png?raw=true "Title")

## Requerimientos de infraestructura

Para el manejo y procesamiento de los datos este proyecto usa infraestructura en
 la nube basada en servicios de Amazon Web Services (AWS). Concretamente, se
 emplean tres buckets de AWS S3 (denominados *models-dpa* y *preds-dpa* ) y una
 instancia AWS EC2 para ejecutar todo el código. Los resultados para cada capa
 de procesamiento se almacenan en un base de datos basada en PostgreSQL en AWS
 RDS. Cabe destacar que toda la infraestructura debe pertenecer a la región
*us-east-1*.

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
Este proyecto asume que se tiene acceso a tales servicios y que se han configurado
oportunamente.

## Instalación y setup

#### 1. Requerimientos

Para conectarse hacia la máquina virtual que servirá como bastión:

```
# Modificar datos segun corresponda
ssh -i <mi-llave> ubuntu@<endpoint-de-mi-instancia>
```

Considerando lo anterior, se necesita un par de herramientas adicionales:

```
sudo apt update
sudo apt-get install docker.io git
```

Se crean las siguientes carpetas en las cuales estarán las credenciales
necesarias para correr el proyecto.

```
mkidr ~/.aws
mkdir ~/.rita
mkdir ~/.rita/conf ~/.rita/keys ~/.rita/logs
```
#### 2. Guardar llaves secretas
Para re-utilizar las credenciales de la base de datos, de la región de las
cubetas y otras configraciones de AWS al igual que para homogeneizar los nombres
 en todos los archivos creamos el archivo path_parameters.yml

```
cd $HOME
nano path_parameters.yml

# Modificar los datos de ejemplo en la parte inferior

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
```

#### 3.Clonar el repositorio de github

Para clonar el repositorio de trabajo del proyecto ejecutar:

```
git clone https://github.com/paola-md/dpa_rita/
```

#### 4. Archivos de credenciales

Para ejecutar el pipeline, se deben especificar las credenciales para su
infraestructura en AWS y postgres, puesto que el primero busca archivos de
credenciales en ubicaciones específicas. Debería crearlos ahora si aún no
existen.

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

Modifique las credenciales de postgres en `.rita/conf/path_parameters.yml`. Este
 archivo debe existir para ejecutar el pipelone. Se crea un ejemplo durante la
 instalación y debe modificarlo para su configuración.

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

Una vez en dicha instancia de docker nos desplazaremos para activar el demonio
de Luigi:

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
necesario hacer el *port forwarding* del puerto 8082 del bastión hacia la máquina
local en donde estamos trabajando. Para tal efecto se debe ejecutar el comando:

```
# Modificar el contenido con los datos de la llave ssh y endpoint del bastion
ssh -i <mi-llave> -N -f -L localhost:8082:localhost:8082 ubuntu@<mi-endpoint>
```

Así en nuestra máquina local debemos abrir un navegador empleando la dirección:

```
localhost:8082
```


#### 5. Creación de esquemas en base de datos

Según los requisitos enumerados en [Requisitos de infraestructura] (https://github.com/dssg/usal_echo#infrastructure-requirements), necesita una instalación de la base de
datos de nombre postgres con credenciales.

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

Dentro de una terminal que refleje la instancia del contenedor de Docker del
proyecto (ver numeral 4.4), la siguiente instrucción se debe ejecutar para
cargar la librería src con los archivos del proyecto.

```
python3 setup.py install
```

A continuación, dentro de la carpeta orquestadores se corre el pipeline.

```
cd src/orquestadores
```

Existen dos vertientes, una para entrenar y otra para predecir. El parámetro
*type* indica cual rama correr. La rama de predict, requiere que se haya
entrenado (type = train) con los datos y se haya guardado un modelo.

**Rama para entrenar:**

```
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline  --type train
```

**Rama para predecir:**
```
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module luigi_main  Pipeline  --type predict
```

![Pipeline](reports/figures/pipeline.jpg?raw=true "Title")

## API

Se construyó un API utilizando la biblioteca *flask* y *flask_restx* de Python
para la documentación con Swagger. A saber, el endpoint local es:

http://127.0.0.1:5000/predicts/1609

Donde el 1609 es cualquier vuelo del cuál se desee saber si se va a retrasar más
 de una hora y media o no. Se realiza una operación GET, la cuál recibe el
 parámetro flight identifier y regresa la predicción (200) o (404) en caso de no
  encontrar ese vuelo.

A continuación se muestra el swagger.json:

```
{
    "swagger": "2.0",
    "basePath": "/",
    "paths": {
        "/predicts/{flight_number}": {
            "parameters": [
                {
                    "in": "path",
                    "description": "The flight identifier",
                    "name": "flight_number",
                    "required": true,
                    "type": "integer"
                }
            ],
            "get": {
                "responses": {
                    "200": {
                        "description": "Delay prediction"
                    },
                    "404": {
                        "description": "Delay not found"
                    }
                },
                "summary": "Fetch a given resource",
                "operationId": "get_predict",
                "tags": [
                    "predicts"
                ]
            }
        }
    },
    "info": {
        "title": "Delay API",
        "version": "1.0",
        "description": "A RITA Delay API"
    },
    "produces": [
        "application/json"
    ],
    "consumes": [
        "application/json"
    ],
    "tags": [
        {
            "name": "predicts",
            "description": "FLIGHTS operations"
        }
    ],
    "responses": {
        "ParseError": {
            "description": "When a mask can't be parsed"
        },
        "MaskError": {
            "description": "When any error occurs on mask"
        }
    }
}
```

En este sentido, para poder acceder al API de predicciones se debe llevar a cabo
el siguiente proceso:

**Instala flask**

Dentro de una terminal que refleje la instancia del contenedor de Docker del
proyecto (ver numeral 4.4):

```
pip install flask_restx
```
**Crea el port forwarding para ver predicciones localmente**

Posteriormente en dicha terminal, se debe hacer el puenteo que permite visualizar
las predicciones del modelo, a través del puerto 5000 de la maquina local con
que el usuario accede al bastion.

Para ello se de correr **en la máquina local**:

```
ssh -i <mi-llave> -N -f -L localhost:5000:localhost:5000 ubuntu@<mi-endpoint>
``
**Corre app***

Posteriormente dentro de una terminal que refleje la instancia del contenedor de
Docker del proyecto (ver numeral 4.4) se debe ejecutar lo siguiente para correr
la app de predicciones:

```
cd src/deploy
python3 app.py
```

**Ver predicciones**

El paso anterior, permite ver las predicciones del proyecto, para ello en la
máquina local con que se accede a bastión, basta acceder desde un navegador a
la dirección:

```
http://127.0.0.1:5000/predicts/1609
``

Se reitera que 1609 es cualquier vuelo del cuál se desee saber si se va a
retrasar más de una hora y media o no. Se realiza una operación GET, la cuál
recibe el parámetro flight identifier y regresa la predicción (200) o (404) en
 caso de no encontrar ese vuelo.

**Ver swagger**

También se puede visualizar el swagger descrito previamente accediendo desde un
navegador máquina local con que se accede a bastión a la dirección:

```
http://127.0.0.1:5000/swagger.json
```



## Dashboard de monitoreo
Con el objetivo de monitorear el desempeño del modelo en tiempo real se
construyó un dashboard en donde es posible revisar en tiempo real las
predicciones que devuelve el modelo después de hacer una consulta al API.
Además, actualizará los valores observado en cuanto estén disponibles.

El dashboard cuenta con tres pestañas:

1. *Información*: Aquí se muestra la información del modelo usado para generar
las predicciones, que por construcción es el modelo con mejor desempeño.

2. *Modelos*: En esta pestaña se monitorean las predicciones en tiempo real para
 un número de vuelo y una distancia en particular, se alerta cuando las
 observaciones no coinciden con las predicciones de forma que es fácil determinar
  si el desempeño del modelo ha degenerado, se extraen los datos de las
  predicciones para los parámetros de vuelo y distancia seleccionados y se tiene
   visibilidad de las distribuciones de la variable distancia en los conjuntos
   de entrenamiento y prueba de forma que se garantiza que no haya cambios tan
   notables al momento de actualizar los datos.

3. *Fairness & Bias*: Finalmente en la última pestaña se presenta un resumen del
 reporte de Fairness& Bias para nuestras variables críticas. Este resumen consta
  de una tabla con los valores de disparidad en los rangos de distancias, una
  gráfica de barras con una visualización de estos valores y una matriz de
  confusión para inspeccionar el desempeño del modelo a través de los códigos de
 origen y las distancias seleccionadas en la sección de parámetros.

Para correr el dashboard, se deben seguir los pasos descritos a continuación:

**Crear el port forwarding para ver dashboard**

Para ello se de correr **en la máquina local**:

```
ssh -i <mi-llave> -N -f -L localhost:4809:localhost:4809 ubuntu@<mi-endpoint>
``

**Activando el dashboard**

Dentro de una terminal que refleje la instancia del contenedor de Docker del
proyecto (ver numeral 4.4), basta con colocarse a través de la terminal en el
irectorio principal del proyecto (dpa_rita/) e indicar las siguientes
instrucciones:

```
cd dashboard/MonitoreoModelos
R
shiny::runApp()
```
**Visualizando el dashboard**

A continuación, se abrir una ventana del navegador con la dirección

```
http://127.0.0.1:4809/
```

## Organización del proyecto


```
├── Diseño
│   ├── Imagenes
│   └── Readme.md
├── Dockerfile
├── EDA
│   ├── Imagenes
│   └── Readme.md
├── LICENSE
├── Linaje
│   └── Readme.md
├── Makefile
├── README.md
├── README2.md
├── README3.md
├── Readme_dssg.md
├── alter_orq.py
├── alter_orq_sep.py
├── clean_luigi.py
├── dashboard
│   └── MonitoreoModelos
├── docs
│   ├── 1.1_Bastion_configuracionAWS.md
│   ├── 1.2_Bastion_conexionesSSH.md
│   ├── Makefile
│   ├── commands.rst
│   ├── conf.py
│   ├── getting-started.rst
│   ├── index.rst
│   └── make.bat
├── final_requirements.txt
├── metadata
├── metadatos_rds_extract.py
├── models
├── notebooks
│   ├── 0.1-liliana-pyspark.ipynb
│   ├── 0.2-danahi-clean.ipynb
│   ├── 0.3-paola-modelling.ipynb
│   ├── 0.4-paola-pipeline.ipynb
│   ├── 0.5-luis-feature-engineering.ipynb
│   ├── 0.5-paola-save-model.ipynb
│   ├── 0.6-paola-bias-metadatos.ipynb
│   ├── 0.6-paola-reporte-fairness.ipynb
│   ├── 0.7-paola-predict.ipynb
│   ├── 0.9-final-checkpoint.ipynb
│   └── zepelling
├── postgresql-9.4.1207.jar
├── references
├── reports
│   └── figures
├── requirements.txt
├── setup.py
├── src
│   ├── __init__.py
│   ├── credentials_psql.txt
│   ├── data
│   ├── deploy
│   ├── features
│   ├── models
│   ├── orquestador-clean.py
│   ├── orquestador-modelling.py
│   ├── orquestador.py
│   ├── orquestadores
│   ├── postgresql-9.4.1207.jar
│   ├── pruebas.py
│   ├── unit_tests
│   ├── utils
│   └── visualization
├── target
├── tasks
│   ├── all_targets.py
│   ├── bucket.py
│   ├── clean.py
│   ├── clean_column_testing.py
│   ├── clean_rango_testing.py
│   ├── extract.py
│   ├── load.py
│   ├── load_test.py
│   ├── metadatos_clean.py
│   ├── metadatos_extract.py
│   ├── metadatos_load.py
│   ├── metadatos_semantic.py
│   ├── modeling.py
│   ├── semantic.py
│   ├── semantic_column_testing.py
│   ├── semantic_type_testing.py
│   ├── target_a.py
│   ├── target_b.py
│   ├── target_c.py
│   └── target_d.py
├── test_environment.py
├── testing
│   ├── test_absent_hearders.py
│   ├── test_clean_columns.py
│   ├── test_clean_rangos.py
│   ├── test_semantic_column_types.py
│   └── test_semantic_columns.py
└── tox.ini
```

## Contributors

**Technical mentors:**

Danahi Ayzailadema Ramos Martínez, Paola Mejía Domenzaín, León Manuel Garay
Vásquez, Luis Eugenio Rojón Jiménez y Cesar Zamora Martínez
