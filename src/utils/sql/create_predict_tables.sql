CREATE SCHEMA IF NOT EXISTS predictions;

CREATE TABLE IF NOT EXISTS predictions.train(
  originwac FLOAT,
  distance INT,
  label_value FLOAT,
  score FLOAT,
  s3_name VARCHAR,
  fecha VARCHAR
);

DROP TABLE IF EXISTS predictions.test;
CREATE TABLE IF NOT EXISTS predictions.test(
  flight_number FLOAT,
  distance FLOAT,
  prediction VARCHAR,
  s3_name VARCHAR,
  fecha VARCHAR
);

CREATE TABLE IF NOT EXISTS metadatos.predictions(
  fecha VARCHAR,
  s3_name_model VARCHAR,
  s3_name_pred VARCHAR,
  number_pred INT,
  binary_stats FLOAT
);


--DROP TABLE metadatos.bias;
CREATE TABLE IF NOT EXISTS metadatos.bias(
  fecha VARCHAR,
  s3_name VARCHAR,
  attribute_value_q1 VARCHAR,
  attribute_value_q2 VARCHAR,
  attribute_value_q3 VARCHAR,
  attribute_value_q4 VARCHAR,
  fpr_disparity_q1 FLOAT,
  fpr_disparity_q2 FLOAT,
  fpr_disparity_q3 FLOAT,
  fpr_disparity_q4 FLOAT
);


CREATE TABLE IF NOT EXISTS metadatos.testing_predict_cols(
  fecha VARCHAR,
  nombre_task VARCHAR,
  task_status VARCHAR,
  msg_error VARCHAR
);

GRANT ALL ON  metadatos.testing_predict_cols to postgres;

CREATE TABLE IF NOT EXISTS metadatos.testing_predict_types(
  fecha VARCHAR,
  nombre_task VARCHAR,
  task_status VARCHAR,
  msg_error VARCHAR
);

GRANT ALL ON  metadatos.testing_predict_types to postgres;
