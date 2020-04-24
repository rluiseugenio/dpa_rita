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
