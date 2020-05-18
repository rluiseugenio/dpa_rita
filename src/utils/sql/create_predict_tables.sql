CREATE SCHEMA IF NOT EXISTS predictions;

CREATE TABLE IF NOT EXISTS predictions.train(
  originwac FLOAT,
  distance INT,
  label_value FLOAT,
  score FLOAT,
  s3_name VARCHAR
);

CREATE TABLE IF NOT EXISTS predictions.test(
  fecha VARCHAR,
  s3_name VARCHAR
  model TEXT,
  target TEXT,
  flight_number INT,
  prediction VARCHAR
);

DROP TABLE metadatos.bias;
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
