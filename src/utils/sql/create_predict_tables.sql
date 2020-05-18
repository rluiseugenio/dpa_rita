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
  model TEXT,
  target TEXT,
  flight_number INT,
  prediction VARCHAR
);

CREATE TABLE IF NOT EXISTS metadatos.bias(
  fecha VARCHAR,
  model TEXT,
  target TEXT,

);
