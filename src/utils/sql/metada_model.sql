CREATE SCHEMA IF NOT EXISTS metadatos;

----MODELLING
DROP TABLE IF EXISTS metadatos.models;

CREATE TABLE metadatos.models(
  fecha VARCHAR,
  objetivo VARCHAR,
  model_name VARCHAR,
  hyperparams VARCHAR,
  AUROC VARCHAR,
  AUPR VARCHAR,
  precision VARCHAR,
  recall VARCHAR,
  f1 VARCHAR,
  train_time VARCHAR,
  test_split VARCHAR,
  train_nrows VARCHAR
);
