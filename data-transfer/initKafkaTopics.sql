-- Script File zur Vorbereitung der Kafka Objekte; Topics, Tables, Streams
-- Ausführen des Scripts via kSQLDB-CLI
-- docker exec -it ksqldb-cli ksql http://ksqldb-server-1:8088

-- Script ausführen; Script muss in das Verzeichnis /data-transfer kopiert werden, damit es im Docker-Container in ksql verfügbar ist
-- RUN SCRIPT '/data-transfer/initKafkaTopics.sql'


-- Sollten beim ausführen des Scripts Fehler auftreten beim löschen der Tagellen und Topics (drop table) weil noch Queries am laufen sind, ist wie folgt vorzugehen
-- Queries abfragen: SHOW QUERIES;
-- Query beenden:    TERMINATE <query name>;

-- ---------------------------------------------
-- Development options
-- Set 'auto.offset.reset' = 'earliest';
-- unset 'auto.offset.reset';

-- ---------------------------------------------
-- MetaDaten

-- Tabellen, Streams und Topics löschen
--DROP TABLE IF EXISTS T_CALCBASEPOS;
--DROP TABLE IF EXISTS t_rawMetaMatch delete topic;
--DROP TABLE IF EXISTS t_rawMetaPlayer delete topic;
--DROP TABLE IF EXISTS t_fbFieldPos delete topic;



-- Tabelle mit Topic rawMetaMatch neu erstellen
CREATE TABLE t_rawMetaMatch (
  rowKey VARCHAR PRIMARY KEY, 
  matchId BIGINT, 
  pitchXSize DOUBLE, 
  pitchYSize DOUBLE) 
WITH (KAFKA_TOPIC='rawMetaMatch', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');



-- Tabelle mit Topic fbFieldPos neu erstellen
CREATE TABLE t_fbFieldPos 
WITH (KAFKA_TOPIC='fbFieldPos', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON')
as
select
  matchId, 
  STRUCT( Xmin := -(PITCHXSIZE/2), Xmax := (PITCHXSIZE/2), Ymin := -(PITCHYSIZE/2), Ymax := (PITCHYSIZE/2)) AS pitch,
  STRUCT( Xmin := -(PITCHXSIZE/2), Xmax := 0, Ymin := -(PITCHYSIZE/2), Ymax := (PITCHYSIZE/2)) AS pitchLeft, 
  STRUCT( Xmin := 0, Xmax := (PITCHXSIZE/2), Ymin := -(PITCHYSIZE/2), Ymax := (PITCHYSIZE/2)) AS pitchRight, 
  STRUCT( Xmin := -(PITCHXSIZE/2), Xmax := -(PITCHXSIZE/2)+16.5, Ymin := (-20.16), Ymax := 20.16) AS penaltyBoxLeft, 
  STRUCT( Xmin := (PITCHXSIZE/2)-16.5, Xmax := (PITCHXSIZE/2), Ymin := (-20.16), Ymax := 20.16) AS penaltyBoxRight, 
  STRUCT( Xmin := -(PITCHXSIZE/2)-2.0, Xmax := -(PITCHXSIZE/2), Ymin := -3.66, Ymax := 3.66 ) AS goalLeft, 
  STRUCT( Xmin := (PITCHXSIZE/2), Xmax := (PITCHXSIZE/2)+2.0, Ymin := (-3.66), Ymax := 3.66 ) AS goalRight
FROM t_rawMetaMatch
EMIT CHANGES;



-- Tabelle mit Topic rawMetaPlayer neu erstellen (Sensor-Objekte; Spieler, Ball)
CREATE TABLE t_rawMetaPlayer (
  rowKey VARCHAR PRIMARY KEY, 
  matchId BIGINT, 
  sensorId INT, 
  name varchar, 
  alias varchar, 
  objectType int) -- 0=Ball; 1=Player Home Team; 2=Player Away Team 
WITH (KAFKA_TOPIC='rawMetaPlayer', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');



--------------------
-- Daten einfügen




-- Spieldaten in Topic rawMetaMatch einfügen
INSERT INTO t_rawMetaMatch (rowKey, matchId, pitchXSize , pitchYSize ) VALUES ('19060518', 19060518, 105.0, 68.0);

-- Spielerdaten einfügen
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.200', 19060518, 200 , 'Ball' , 'BALL' , 0);

INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.1', 19060518, 1 , 'Patricio' , 'A1' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.3', 19060518, 3 , 'Pepe' , 'A2' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.4', 19060518, 4 , 'Dias' , 'A3' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.5', 19060518, 5 , 'Guerreiro' , 'A4' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.7', 19060518, 7 , 'Ronaldo' , 'A5' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.10', 19060518, 10 , 'Silva' , 'A6' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.14', 19060518, 14 , 'Carvalho' , 'A7' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.16', 19060518, 16 , 'Fernandes' , 'A8' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.18', 19060518, 18 , 'Neves' , 'A9' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.20', 19060518, 20 , 'Semedo' , 'A10' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.23', 19060518, 23 , 'Felix' , 'A11' , 1);

INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.101', 19060518, 101 , 'Sommer' , 'B1' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.102', 19060518, 102 , 'Mbabu' , 'B2' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.105', 19060518, 105 , 'Akanji' , 'B3' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.108', 19060518, 108 , 'Freuler' , 'B4' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.109', 19060518, 109 , 'Seferovic' , 'B5' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.110', 19060518, 110 , 'Xhaka' , 'B6' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.113', 19060518, 113 , 'Rodriguez' , 'B7' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.114', 19060518, 114 , 'Zuber' , 'B8' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.117', 19060518, 117 , 'Zakaria' , 'B9' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.122', 19060518, 122 , 'Schaer' , 'B10' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, matchId, sensorId, name, alias, objectType) VALUES ('19060518.123', 19060518, 123 , 'Shaqiri' , 'B11' , 2);


CREATE STREAM s_rawGames (
    ts VARCHAR,
    x DOUBLE,
    y DOUBLE,
    z DOUBLE,
    id int,
    matchId BIGINT
  ) WITH (
    KAFKA_TOPIC = 'rawGames',
    PARTITIONS=1,
    REPLICAS=1, 
    VALUE_FORMAT='JSON'
);

CREATE STREAM s_fbBallPossession (
    ts VARCHAR,
    x DOUBLE,
    y DOUBLE,
    z DOUBLE,
    id int,
    matchId BIGINT
  ) WITH (
    KAFKA_TOPIC = 'fbBallPossession',
    PARTITIONS=1,
    REPLICAS=1, 
    VALUE_FORMAT='JSON'
);

CREATE STREAM s_fbBallPossessionAggregate (
  ts VARCHAR, 
  eventtype VARCHAR,
  playerId INT,
  matchId BIGINT,
  playerKey VARCHAR) 
WITH (KAFKA_TOPIC='fbBallPossessionAggregate', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');




create stream s_fbBallPossessionEvent
WITH (
    kafka_topic = 'fbBallPossessionEvent',
    PARTITIONS=1, 
    REPLICAS=1,
    VALUE_FORMAT='JSON'
)
as
select
  bp.ts as ts, 
  bp.eventtype as eventtype,
  bp.playerId as playerId,
  bp.matchId as matchId,
  bp.playerKey as playerKey,
  p.name as name,
  p.alias as alias,
  p.objectType as objectType
from s_fbBallPossessionAggregate bp
inner join t_rawMetaPlayer p on p.rowkey = bp.playerKey
partition by cast(p.matchid as varchar)
EMIT CHANGES;

--TERMINATE  CSAS_S_FBBALLPOSSESSIONEVENT_21;
--DROP STREAM IF EXISTS s_fbBallPossessionEvent delete topic;





-- Konfiguration der Tabelle ausgeben
--DESCRIBE EXTENDED t_rawMetaMatch;
--DESCRIBE EXTENDED t_rawMetaPlayer;
--DESCRIBE EXTENDED t_calcBasePos;


-- Daten abfragen
--SELECT * FROM t_fbFieldPos EMIT CHANGES;
--SELECT * FROM t_rawMetaPlayer EMIT CHANGES;
--SELECT * FROM t_calcBasePos EMIT CHANGES;
