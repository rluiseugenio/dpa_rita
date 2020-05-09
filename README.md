# Arquitectura de Productos de Datos
## Proyecto - Retrasos en vuelos de la DB RITA


**Profesora:** Arquitectura de Productos de Datos

**Fecha:** 9 de febrero de 2020

**Integrantes del equipo:**

| # | Alumn@                            |
|---|-----------------------------------|
| 1 | Danahi Ayzailadema Ramos Martínez |
| 2 | Paola Mejía Domenzaín             |
| 3 | León Manuel Garay Vásquez         |
| 4 | Luis Eugenio Rojón Jiménez        |
| 5 | Cesar Zamora Martínez             |


***

### 1. Descripción del repositorio

El presente repositorio contiene los archivos asociados al proyecto de la materia de Arquitectura de Productos de Datos, el cual versa sobre la predicción de retraso o cancelación de los vuelos de la base de datos denominada conocida como [RITA](http://stat-computing.org/dataexpo/2009/the-data.html) (ver también [transtats.bts.gov](https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp)); esta agrupa una serie de datos de vuelos que incluyen salidas a tiempo, llegadas a tiempo, demoras, vuelos cancelados de todo Estados Unidos del Departamento de Transporte.

Cabe destacar que RITA posee una frecuencia de actualización mensual, con datos desde junio del 2003.

En este sentido, para facilitar el entendimiento de los documentos y acciones desarrolladas para llevar a cabo este proyecto, la información del repositorio se ha organizado en la estructura de carpetas que se resume en seguida:

| # | Carpeta                           | Descripción  |
|---|-----------------------------------|--------------|
| 1 | Docs | Refiere la documentación de los pasos realizados para las diferentes etapas del proyecto. |
| 2 | Diseño | Contiene un documento *mock-up* con de la conceptualización del proyecto a realizar. |
| 3 | EDA | Análisis exploratorio preeliminar para identificar potenciales transformaciones. |
| 4 | ETL | Primera versión del ETL, considerando la etapa de Luigi. |
| 5 | sql | Contiene propuestas para hacer la carga a una base PostgreSQL de los datos desde csv. |
| 6 | Linaje | Presenta una serie de esquemas que describe tanto los metadatos que se recopilarán en las diferentes fases del proyecto, así como el linaje de los datos generados en cada una de dichas etapas. |
| 7 | UTILS | Esta carpeta contiene las instrucciones necesarias para crear el ambiente virtual donde se correrá luigi con el resto de los paquetes para el pipeline |

**Nota:** La estructura del repositorio y su contenido se irá actualizando conforme el equipo avance en el desarrollo del multi-citado proyecto.

Descripción del proyecto

Los datos se obtuvieron a través de una API (https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp) en la cual utilizamos como parámetros mes y año para la descarga de datos; posteriormente esos datos son ingestados en un bucket en fromato csv para posteriormente cargarlos a Postgres.

Posteriormente realizamos un análisis EDA para ver la estructura de los datos.

El siguiente paso fue realizar el ETL;

* Extract: en esta etapa se plantea la descarga de los datos de la base de RITA.

* Load: en esta etapa se cargan los datos descargados en formato zip en una cubeta S3.

* Transform:

EL siguiente proceso es el modeling

Descripción detallada del ETL
___

# ETL para el proyecto de la base de datos RITA

25 de febrero de 2019

## 1. Introducción

Este documento tiene como objetivo de describir, a manera de *mock-up*, el ETL para la ingestión de los datos de RITA para el diseño de un producto de datos encaminado a predecir intervalos de retraso de los vuelo de los usuarios de aerolíneas en Estados Unidos.

Dicho proceso se realizará con base en una serie especificaciones que se plantearán, a manera de preguntas, y que serán las directrices de ésta etapa del proyecto, mismas que se exponen a continuación.

## 2. Especificaciones para la definición del ETL y la ingesta de datos

**1) ¿Con qué frecuencia se publican los datos?**
  - Para esta base se realizan actualizaciones de datos de manera mensual. Sin embargo se identificó que la última publicación de los mismos se realizó hasta Noviembre de 2019. Esto añade un punto a considerar en el proyecto sobre la disponibilidad de la información, y los periodos en que se tiene que consultar para obtener el último tren de información disponible en razón de que se deberá realizar consultas periódicas en busca de nuevos trenes de datos disponibles, cuales podrían estar listos con un cierto desfase.

  En cualquier caso, el proceso de ingesta de datos se realizará con base en la información disponible más reciente.

**2) ¿Cada cuánto ingestaremos los datos?**
  - Considerando a la respuesta al pregunta previa, se plantea hacer una consulta de nuevos de manera semanal, para que una vez que se encuentren nuevas cargas de trenes de datos, podamos ingestar los procesos que permiten el funcionamiento del producto de datos.

**3) ¿Cómo ingestaremos los datos?**
  - El proceso de ingesta se plantea llevar a cabo a través de un script de Bash, que se corre semanalmente, se obtienen los datos en formato .zip, para periodos mensuales. Esto con miras a obtener la última información disponible.

**4) ¿Dónde guardaremos los datos?**
  - Se estima pertinente emplear en una cubeta S3 (*bucket*) para conservar historicidad de los mismos y detectar posibles errores en la dinámica del producto de datos. En este sentido, se considera realizar posteriormente transformaciones de este conjunto de datos hacia lam carga de una base de datos empleando PostGreSQL.

**5) ¿En qué formato?**
  -  Tal como se ha mencionado, se plantea guardarlos en el formato original de descarga, el cual corresponde archivos de extensión .zip (en la cubeta S3) los cuales son versiones comprimidas de archivos .csv de la base.
  - Este punto es relevante, dado que nos permitirá administra los nuevos datos correspondientes a entregas mensuales dentro de S3, tomando como referencia las fechas a las que corresponden.
  - Además, como una linea futura de trabajo, se plantea explorar el guardar los datos empleando el formato *parquet*.

**6) ¿Los transformamos antes de guardarlos?**
  - Se considera relevante mantener los datos en el formato y estructura en que son provistos desde la fuente de las aerolíneas, de manera que podamos considerar en el *pipeline* del producto de datos la historicidad de los mismo en una cubeta de S3. Sin embargo, se contempla realizar transformaciones a los mismos en el proceso de carga hacia la base de datos de PostGreSQL.

Con base en los puntos expuestos, a continuación explicaremos cada una de las etapas que integrarán el ETL.

## 3. Descripción de etapas

### 3.1 Extract

En dicha etapa se plantea que a través de una una instancia de Cómputo Elástico en la Nube (EC2, por sus siglas en inglés). A través de ella se correrá  semanalmente un programa de Python, denominado **update.py**, que nos permitirá emplear la herramienta CROM para activar un script de Bash (**download_rita.sh**) el cual se encargará de la descarga de la datos de la base RITA, al tiempo que permitirá determinar si hay actualizaciones de la información histórica, para actualizar el proceso de ingesta del producto de datos. Para ello se plantea la comunicación de una base en PostgresSQL, que contendrá la información que hemos ido agregando de manera histórica.

En este sentido, dicha base de PostgresSQL nos permitirá:

* Poblar la tabla de datos de la base, en su creación (dado que estará vacía en la construcción del primer mes histórico),
* Obtener los parámetros de mes y año respecto a los cuales se cargó la información del último mes, con el propósito de determinar si la ingesta de nuevos datos debe llevarse a cabo en dicho periodo de ejecución de este script. Para llevar a cabo esta acción, se plantea ordenar una tabla de la base de datos con respecto a la fecha, en forma descendente, y tras comparar si el primer dato es igual o diferente; de manera de que al encontrar diferencia entre ambos se extraerán nuevos datos, mismos que en etapas posteriores se añadirán al PostGreSQL.

### 3.2 Load

Este paso consiste en realizar la carga de los datos descargados en formato .zip hacia una cubeta S3 que nos permitirá tener historicidad de la información considerada para la ingesta del producto de datos. Para ello, se plantea emplear periódicamente un script de Bash, en el EC2 de la etapa previa, que permitirá cargar los últimos datos extraídos de la página de aerolíneas para un nuevo periodo, empleando comandos de *awscli*
de manera que sea posible la cargan de estos hacia una cubeta S3, caracterizando los mismos con un formato que considere la fecha en que se obtuvo la información.

Como se ha dicho anteriormente, se plantea realizar una revisión semanal en busca de nuevas publicaciones de datos, por lo que en caso de encontrarse nueva información disponible, con dicho proceso se agregaran a la cubeta de S3 bloques nuevos de datos en formato comprimido.

### 3.3 Transform

En la etapa de transformación de datos, se aplica una serie de reglas o funciones a los datos extraídos para prepararlos para la carga en el destino final, nuestro almacén de datos en PostGreSQL que vivirá en una instancia EC2.

Una función importante de esta etapa de transformación es la limpieza de datos, que tiene como objetivo pasar solo datos "adecuados" al entorno analítico. Para resolver el desafío de la interacción entre nuestra cubeta de S3 y nuestra base de PostGreSQL se incluirá en la rutina de orquestación de Python una sección con la librería Boto3 de Python, lo que permitirá recuperar los datos crudos, transformarlos con esa misma rutina y después utilizar la librería PsicoPG2 de Python para cargar en nuestro almacén de datos de PostGreSQL en nuestra instancia de EC2 destinada al entorno analítico.

Uno o más de los siguientes tipos de transformación pueden ser necesarios para satisfacer las necesidades del problema en cuestión:

* Seleccionar sólo ciertas columnas para cargar (o seleccionando columnas nulas para no cargar).
* Traducción de valores según su codificación (para hacer entendibles las etiquetas).
* Transformación de valores de forma libre: (por ejemplo, en un mapeo qué permita entender o describir su codificación, como "Macho" a "M").
*	Derivar un nuevo valor calculado: (por ejemplo, *sale_amount = qty * unit_price*).
* Ordenar los datos en función de una lista de columnas para mejorar el rendimiento de búsqueda (i.e.: escoger *sortkeys* y *distkeys* adecuadas).
* Agregación (por ejemplo, resumen - resumen de varias filas de datos - retrasos totales para cada aeropuerto, y para cada región, etc.)
* Transposición o pivote (convertir múltiples columnas en múltiples filas o viceversa).
* Dividir una columna en varias columnas (por ejemplo, convertir una lista separada por comas, especificada como una cadena en una columna, en valores individuales en diferentes columnas).

*  Aplicando cualquier forma de validación de datos; la validación fallida puede dar como resultado un rechazo total de los datos, un rechazo parcial o ningún rechazo y, por lo tanto, ninguno, algunos o todos los datos se transfieren al siguiente paso, según el diseño de la regla y el manejo de excepciones.

 Muchas de las transformaciones anteriores pueden dar lugar a excepciones, por ejemplo, cuando una traducción de código analiza un código desconocido un cambio súbito en los datos extraídos por lo que el último punto de validación es importante.

## 4. Diagrama

Para facilitar el entendimiento del proceso recién descrito, presentamos un diagrama que describe las actividades a realizar en cada una de las etapas del ETL.

![Diagrama de flujo del ETL](reports/figures/etl3.png?raw=true "Title")
(https://drive.google.com/file/d/1aYgxZ5BnPjNXAMo6qNAPVHjWbP7cOrB9/view?usp=sharing)
(https://www.draw.io/#G17QEIJYjJwGIPJViHqTRJg0UPf8I40m2j)

EL hasta el momento

![Diagrama de flujo del EL](reports/figures/EL.png?raw=true "Title")

## 5. Implicaciones éticas del proyecto

Al respecto, se identifican posibles implicaciones éticas del producto de datos hasta aquí planteando:

**Eje de usuarios:**

* Hacer que pierdan vuelos y deban hacer doble gasto en un viaje,
* Sesgar a que los usuarios viajen o no en una aerolínea,

**Eje de aerolíneas:**

* Perjudicar la reputación  de una aerolínea,
* Proyectar la responsabilidad de eventos fuera de su control,
* Dañar su estabilidad económica y empleos,
* Aumentar quejas injustificadas del servicio.


## 6. Fairness y bias
Tomando en cuenta las implicaciones éticas, seleccionamos dos variables protegidas.
La primera es **originwac** que es la variable que agrupa los aeropuertos de origen por zonas geográficas en Estados Unidos. La variable es protegida porque no queremos que el modelo discrimine por la zone de provencia de los vuelos. Por ejemplo, de los vuelos de sur de Estados Unidos.
Adicionalmente, la segunda variable protegida es la **distancia** al ser una variable continua la dividiremos en quartiles para el análisis. El objetivo es que el modelo haga predicciones justas sin importar que el vuelo sea corto o largo.

En nuestro modelo intentamos predecir el retraso de un vuelo. Las consecuencias negativas de decir que un vuelo se va a retrasar y que no se retrase (falso positivo) son muchas más graves que decir que un vuelo no se va a retrasar y que se retrase (falso negativo). Es decir, que un usuario espere tiempo extra en el aeropuerto es menos grave que no llegué a su vuelo porque “pensó” que se iba a retrasar. Es por eso que nos interesan los falsos positivos más que los falsos negativos.

Como consecuencia, la métrica que nos interesa es **False Positive Parity** porque queremos que todas las zonas geográficas de Estados Unidos y grupos de distancia tengan el mismo FPR (false positive rate). Es decir, nos equivocamos en las mismas proporciones para etiquetas positivas que eran negativas.

Escogimos esta métrica ya que necesitamos que el modelo sea bueno detectando la etiqueta positiva y no hay (mucho) costo en introducir falsos negativos al sistema. El costo de un falso negativo es que usuarios esperen en el aeropuerto a su vuelo retrasado y este sería el status-quo sin el modelo o producto de datos. Asimismo, esta es la métrica adecuada porque  la variable target no es subjetiva. Si un vuelo se retrasa sabemos exactamente cuánto se retrasó y no depende de la persepción del usuario.

![False Positive Parity Distancia](reports/figures/fpr_distance.png?raw=true "Title")
![False Positive Parity Originwac](reports/figures/fpr_origin.png?raw=true "Title")

## 7. Contenido la carpeta

| # | Carpeta                       | Descripción  |
|---|-----------------------------------|--------|
| 1 | download_rita_parquet.py | Archivo que extrae una fracción de los datos, para convertirla a formato .parquet |
| 2 | orquestador.py | Programa que funge como orquestador |
| 3 | prueba.py | Script que lista el contenido del bucket, junto con su peso. No forma parte del pipeline, solo se usa como acción ilustrativa para probar que al bucket se han cargado exitosamentente los datos. |
| 4 | limpia_cubeta.py | Script que vacía el bucket que se ha subido a la cubeta; nuevamente no forma parte del pipeline, solo se emplea como una acción ilustrativa para enseñar en clase el corrector funcionamiento del orquestador |
| 5 | rita_pyenv.sh | Script de Bash para descargar pyenv y pyenv virtualenv, de modo que sea posible crear un ambiente virtial denominado *Rita*, con todas las dependencias de Python necesarias para la ejecución de proyecto.  |




Para correr el orquestador, se debe ejecutar la instrucción:

```
PYTHONPATH='.' AWS_PROFILE=dpa luigi --module orquestador S3Task --local-scheduler
```

**Notas**

* Para la correcta ejecución, se debe asegurar que se ha corrido el archivo *limpia_cubeta.py*, posteriormente correr el orquestador, y verificar el contenido con el script *prueba.py*
* El archivo Bash es un script implementado para instalar un ambiente virtual de Python 3.7.3, denominado "rita" que posee las dependencias necesarias para el proceso recién descrito.


Ello baja un fracción de los datos, para convertirlos a .parquet y subirlos al bucket. Además se debe considerar lo siguiente:




rita
==============================

A short description of the project.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>



## Running with Docker
Set:

```
VERSION=5.0.0
REPO_URL=paolamedo/aws_rita
BUILD_DIR=/home/paola/Documents/MCD/ProductoDatos/PROYECTO/dpa_rita

```
Use:
```
docker pull $REPO_URL:$VERSION
```

Build:

```
docker build $(pwd) --force-rm -t $REPO_URL:$VERSION
```

Upload to Dockerhub:
```
docker login
docker push $REPO_URL:$VERSION
```

Run:

```
docker run --rm -it \
-v $BUILD_DIR:/home  \
-v $HOME/.aws:/root/.aws:ro  \
-v $HOME/.rita:/root/.rita \
--entrypoint "/bin/bash" \
 $REPO_URL:$VERSION

```


Using docker compose (in progress)
```
docker-compose up
docker-compose down --volumes
```

(not necessary) Enter to docker container with:

```
docker exec -it -u=miuser rita bash
```

Stop:

```
docker stop rita
```

Delete (if `--rm` wasn't used):


```
docker rm rita
```

Other useful docker images for development:

Pyspark notebook
```
BUILD_DIR_example=/home/paola/Documents/MCD/ProductoDatos/PROYECTO/dpa_rita
VERSION=latest
REPO_URL=jupyter/pyspark-notebook

docker run --rm -it --name jupyterlab-local \
-p 8888:8888 GRANT_SUDO=yes --user root \
-v $BUILD_DIR:/home/jovyan/work  \
-v $HOME/.aws:/home/jovyan/.aws:ro \
-v $HOME/.rita:/home/jovyan/.rita: \
 $REPO_URL:$VERSION
```

Zepelling
```
VERSION=0.9.0
REPO_URL=apache/zeppelin
docker run --rm -it --name zeppy -p 8080:8080 -v $BUILD_DIR:/notebook $REPO_URL:$VERSION
docker pull $REPO_URL:$VERSION
```

## Running project (in and out of Docker)
```
sudo python setup.py install
```
