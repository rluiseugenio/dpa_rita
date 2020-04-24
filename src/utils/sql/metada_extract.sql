CREATE SCHEMA IF NOT EXISTS metadatos;

---- EXTRACT
DROP TABLE IF EXISTS metadatos.extract;

CREATE TABLE metadatos.extract(
  fecha VARCHAR,
  nombre_task VARCHAR,
  year VARCHAR,
  month VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  tamano_zip VARCHAR,
  nombre_archivo VARCHAR,
  ruta_s3 VARCHAR,
  task_status VARCHAR
);

---- EXTRACT
--DROP TABLE IF EXISTS metadatos.models;

--CREATE TABLE metadatos.models(
--  fecha VARCHAR,
--   objetivo VARCHAR,
--   model_name VARCHAR,
--   hyperparams VARCHAR,
--   AUROC VARCHAR,
--   AUPR VARCHAR,
--   precision VARCHAR,
--   recall VARCHAR,
--   f1 VARCHAR,
--   train_time VARCHAR,
--   test_split VARCHAR,
--   train_nrows VARCHAR,
-- );


---- TRANSFORM

-- CREATE TABLE metadatos.transform(
--   fecha DATE,
--   usuario CHAR(20),
--   who_exec CHAR(20),
--   num_obs_clean CHAR(10),
--   status CHAT(10)
-- );
