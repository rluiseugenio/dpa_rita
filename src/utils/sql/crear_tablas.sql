--- Crea esquemas del proyecto
CREATE SCHEMA IF NOT EXISTS metadatos;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS clean;
CREATE SCHEMA IF NOT EXISTS semantic;

---- Crea tabla metadatos.extract
--DROP TABLE IF EXISTS metadatos.extract;

CREATE TABLE IF NOT EXISTS metadatos.extract(
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

GRANT ALL ON  metadatos.extract to postgres;

---- Crea tabla metadatos.load
--DROP TABLE IF EXISTS metadatos.extract;

CREATE TABLE IF NOT EXISTS metadatos.load(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  tamano_csv VARCHAR,
  nombre_archivo VARCHAR,
  num_columnas VARCHAR,
  num_renglones VARCHAR
);

GRANT ALL ON  metadatos.load to postgres;
--- Crea tabla metadatos.clean

--DROP TABLE IF EXISTS metadatos.clean;

CREATE TABLE IF NOT EXISTS metadatos.clean(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  num_columnas_modificadas VARCHAR,
  num_filas_modificadas VARCHAR,
  variables_limpias VARCHAR,
  task_status VARCHAR
);

GRANT ALL ON  metadatos.clean to postgres;
-- Crea tabla metadatos.testing_extract

CREATE TABLE IF NOT EXISTS metadatos.testing_extract(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  year VARCHAR,
  month VARCHAR,
  task_status VARCHAR
);

GRANT ALL ON  metadatos.testing_extract to postgres;

-- Crea tabla metadatos.testing_load

CREATE TABLE IF NOT EXISTS metadatos.testing_load(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  year VARCHAR,
  month VARCHAR,
  task_status VARCHAR
);

GRANT ALL ON  metadatos.testing_load to postgres;

-- Crea tabla metadatos.testing_clean_columns

CREATE TABLE IF NOT EXISTS metadatos.testing_clean_columns(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  task_status VARCHAR
);

GRANT ALL ON  metadatos.testing_clean_columns to postgres;

-- Crea tabla metadatos.testing_clean_columns

CREATE TABLE IF NOT EXISTS metadatos.testing_clean_rangos(
  fecha VARCHAR,
  nombre_task VARCHAR,
  usuario VARCHAR,
  ip_ec2 VARCHAR,
  task_status VARCHAR
);

GRANT ALL ON  metadatos.testing_clean_rangos to postgres;

--- Crea tabla metadatos.semantic

--DROP TABLE IF EXISTS metadatos.semantic;

CREATE TABLE IF NOT EXISTS metadatos.semantic (num_filas_modificadas VARCHAR, fecha VARCHAR, nombre_task  VARCHAR, usuario VARCHAR, year VARCHAR, month VARCHAR, ip_ec2 VARCHAR, variables VARCHAR, ruta_s3 VARCHAR, task_status  VARCHAR);

GRANT ALL ON  metadatos.semantic to postgres;

--- Crea tabla metadatos.modeling

--DROP TABLE IF EXISTS metadatos.models;

CREATE TABLE IF NOT EXISTS metadatos.models(
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

GRANT ALL ON  metadatos.models to postgres;
---
--DROP TABLE IF EXISTS raw.rita;

CREATE TABLE IF NOT EXISTS raw.rita (
	year text,
	quarter text,
	month text,
	dayofmonth text,
	dayofweek text,
	flightdate text,
	reporting_airline text,
	dot_id_reporting_airline text,
	iata_code_reporting_airline text,
	tail_number text,
	flight_number_reporting_airline text,
	originairportid text,
	originairportseqid text,
	origincitymarketid text,
	origin text,
	origincityname text,
	originstate text,
	originstatefips text,
	originstatename text,
	originwac text,
	destairportid text,
	destairportseqid text,
	destcitymarketid text,
	dest text,
	destcityname text,
	deststate text,
	deststatefips text,
	deststatename text,
	destwac text,
	crsdeptime text,
	deptime text,
	depdelay text,
	depdelayminutes text,
	depdel15 text,
	departuredelaygroups text,
	deptimeblk text,
	taxiout text,
	wheelsoff text,
	wheelson text,
	taxiin text,
	crsarrtime text,
	arrtime text,
	arrdelay text,
	arrdelayminutes text,
	arrdel15 text,
	arrivaldelaygroups text,
	arrtimeblk text,
	cancelled text,
	cancellationcode text,
	diverted text,
	crselapsedtime text,
	actualelapsedtime text,
	airtime text,
	flights text,
	distance text,
	distancegroup text,
	carrierdelay text,
	weatherdelay text,
	nasdelay text,
	securitydelay text,
	lateaircraftdelay text,
	firstdeptime text,
	totaladdgtime text,
	longestaddgtime text,
	divairportlandings text,
	divreacheddest text,
	divactualelapsedtime text,
	divarrdelay text,
	divdistance text,
	div1airport text,
	div1airportid text,
	div1airportseqid text,
	div1wheelson text,
	div1totalgtime text,
	div1longestgtime text,
	div1wheelsoff text,
	div1tailnum text,
	div2airport text,
	div2airportid text,
	div2airportseqid text,
	div2wheelson text,
	div2totalgtime text,
	div2longestgtime text,
	div2wheelsoff text,
	div2tailnum text,
	div3airport text,
	div3airportid text,
	div3airportseqid text,
	div3wheelson text,
	div3totalgtime text,
	div3longestgtime text,
	div3wheelsoff text,
	div3tailnum text,
	div4airport text,
	div4airportid text,
	div4airportseqid text,
	div4wheelson text,
	div4totalgtime text,
	div4longestgtime text,
	div4wheelsoff text,
	div4tailnum text,
	div5airport text,
	div5airportid text,
	div5airportseqid text,
	div5wheelson text,
	div5totalgtime text,
	div5longestgtime text,
	div5wheelsoff text,
	div5tailnum text,
	fffff text
);

GRANT ALL ON  raw.rita to postgres;

--- Crea tabla clean.rita

--DROP TABLE IF EXISTS clean.rita;

CREATE TABLE IF NOT EXISTS clean.rita (
	year int,
	quarter int,
	month int,
	dayofmonth int,
	dayofweek int,
	flightdate text,
	reporting_airline text,
	dot_id_reporting_airline text,
	iata_code_reporting_airline text,
	tail_number text,
	flight_number_reporting_airline int,
	originairportid text,
	originairportseqid text,
	origincitymarketid text,
	origin text,
	origincityname text,
	originstate text,
	originstatefips text,
	originstatename text,
	originwac text,
	destairportid text,
	destairportseqid text,
	destcitymarketid text,
	dest text,
	destcityname text,
	deststate text,
	deststatefips text,
	deststatename text,
	destwac text,
	crsdeptime text,
	deptime text,
	depdelay text,
	depdelayminutes text,
	depdel15 text,
	departuredelaygroups text,
	deptimeblk text,
	taxiout text,
	wheelsoff text,
	wheelson text,
	taxiin text,
	crsarrtime text,
	arrtime text,
	arrdelay text,
	arrdelayminutes text,
	arrdel15 text,
	arrivaldelaygroups text,
	arrtimeblk text,
	cancelled text,
	diverted text,
	crselapsedtime text,
	actualelapsedtime text,
	airtime text,
	flights text,
	distance text,
	distancegroup text,
	divairportlandings text,
	rangoatrasohoras text

);

GRANT ALL ON  clean.rita to postgres;

--- Crea tabla semantic.rita
--DROP TABLE IF EXISTS semantic.rita;

CREATE TABLE IF NOT EXISTS semantic.rita(
year INT,
quarter INT,
month INT,
dayofmonth INT,
dayofweek INT,
flightdate TEXT,
reporting_airline TEXT,
dot_id_reporting_airline INT,
iata_code_reporting_airline TEXT,
tail_number TEXT,
flight_number_reporting_airline INT,
originairportid INT,
originairportseqid INT,
origincitymarketid INT,
origin TEXT,
origincityname TEXT,
originstate TEXT,
originstatefips INT,
originstatename TEXT,
originwac INT,
destairportid INT,
destairportseqid INT,
destcitymarketid INT,
dest TEXT,
destcityname TEXT,
deststate TEXT,
deststatefips INT,
deststatename TEXT,
destwac INT,
crsdeptime VARCHAR,
deptime VARCHAR,
depdelay FLOAT,
depdelayminutes FLOAT,
depdel15 FLOAT,
departuredelaygroups INT,
deptimeblk TEXT,
taxiout FLOAT,
wheelsoff INT,
wheelson INT,
taxiin FLOAT,
crsarrtime INT,
arrtime INT,
arrdelay FLOAT,
arrdelayminutes FLOAT,
arrdel15 FLOAT,
arrivaldelaygroups INT,
arrtimeblk TEXT,
cancelled FLOAT,
diverted FLOAT,
crselapsedtime FLOAT,
actualelapsedtime FLOAT,
airtime FLOAT,
flights FLOAT,
distance VARCHAR,
distancegroup INT,
divairportlandings VARCHAR,
rangoatrasohoras VARCHAR,
findesemana INT,
quincena FLOAT,
dephour FLOAT,
seishoras FLOAT
);

GRANT ALL ON  semantic.rita to postgres;
