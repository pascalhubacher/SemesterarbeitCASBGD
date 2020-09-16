-- Script File zur Vorbereitung der Kafka Objekte; Topics, Tables, Streams
-- Ausführen des Scripts via kSQLDB-CLI
-- docker exec -it ksqldb-cli ksql http://ksqldb-server-1:8088

-- Script ausführen; Script muss in das Verzeichnis /data-transfer kopiert werden, damit es im Docker-Container in ksql verfügbar ist
-- RUN SCRIPT '/data-transfer/initKafkaTopics.sql'


-- Sollten beim ausführen des Scripts Fehler auftreten beim löschen der Tagellen und Topics (drop table) weil noch Queries am laufen sind, ist wie folgt vorzugehen
-- Queries abfragen: SHOW QUERIES;
-- Query beenden:    TERMINATE <query name>;

-- ---------------------------------------------
-- MetaDaten

-- Tabellen, Streams und Topics löschen
--DROP TABLE IF EXISTS T_CALCBASEPOS;
--DROP TABLE IF EXISTS t_rawMetaMatch delete topic;
--DROP TABLE IF EXISTS t_rawMetaPlayer delete topic;
--DROP TABLE IF EXISTS t_fbFieldPos delete topic;

-- Tabelle mit Topic rawMetaMatch neu erstellen
CREATE TABLE t_rawMetaMatch (rowKey VARCHAR PRIMARY KEY, gameId BIGINT, pitchXSize DOUBLE, pitchYSize DOUBLE) WITH (KAFKA_TOPIC='rawMetaMatch', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');

-- Tabelle mit Topic fbFieldPos neu erstellen
CREATE TABLE t_fbFieldPos ( rowKey VARCHAR PRIMARY KEY, gameId BIGINT, pitchXmax DOUBLE, pitchYmin DOUBLE, pitchYmax DOUBLE) WITH (KAFKA_TOPIC='fbFieldPos', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');

-- Tabelle mit Topic rawMetaPlayer neu erstellen (Sensor-Objekte; Spieler, Ball)
-- 0=Ball; 1=Player Home Team; 2=Player Away Team 
CREATE TABLE t_rawMetaPlayer (rowKey VARCHAR PRIMARY KEY, gameId BIGINT, sensorId INT, name varchar, alias varchar, objectType int) WITH (KAFKA_TOPIC='rawMetaPlayer', PARTITIONS=1, REPLICAS=1, VALUE_FORMAT='JSON');

--------------------
-- Daten einfügen

-- Daten in Topic fbFieldPos schreiben
CREATE TABLE t_calcBasePos WITH (kafka_topic='fbFieldPos', value_format='JSON', partitions=1) AS SELECT gameId, -(PITCHXSIZE/2) AS pitchXmin, (PITCHXSIZE/2) AS pitchXmax, -(PITCHYSIZE/2) AS pitchYmin, (PITCHYSIZE/2) AS pitchYmax FROM t_rawMetaMatch EMIT CHANGES;

-- Spieldaten in Topic rawMetaMatch einfügen
INSERT INTO t_rawMetaMatch (rowKey, gameId, pitchXSize , pitchYSize ) VALUES ('19060518', 19060518, 105.0, 68.0);

-- Spielerdaten einfügen
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.200', 19060518, 200 , 'Ball' , 'BALL' , 0);

INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.1', 19060518, 1 , 'Patricio' , 'A1' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.3', 19060518, 3 , 'Pepe' , 'A2' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.4', 19060518, 4 , 'Dias' , 'A3' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.5', 19060518, 5 , 'Guerreiro' , 'A4' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.7', 19060518, 7 , 'Ronaldo' , 'A5' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.10', 19060518, 10 , 'Silva' , 'A6' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.14', 19060518, 14 , 'Carvalho' , 'A7' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.16', 19060518, 16 , 'Fernandes' , 'A8' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.18', 19060518, 18 , 'Neves' , 'A9' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.20', 19060518, 20 , 'Semedo' , 'A10' , 1);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.23', 19060518, 23 , 'Felix' , 'A11' , 1);

INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.101', 19060518, 101 , 'Sommer' , 'B1' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.102', 19060518, 102 , 'Mbabu' , 'B2' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.105', 19060518, 105 , 'Akanji' , 'B3' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.108', 19060518, 108 , 'Freuler' , 'B4' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.109', 19060518, 109 , 'Seferovic' , 'B5' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.110', 19060518, 110 , 'Xhaka' , 'B6' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.113', 19060518, 113 , 'Rodriguez' , 'B7' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.114', 19060518, 114 , 'Zuber' , 'B8' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.117', 19060518, 117 , 'Zakaria' , 'B9' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.122', 19060518, 122 , 'Schaer' , 'B10' , 2);
INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.123', 19060518, 123 , 'Shaqiri' , 'B11' , 2);

-- Konfiguration der Tabelle ausgeben
--DESCRIBE EXTENDED t_rawMetaMatch;
--DESCRIBE EXTENDED t_rawMetaPlayer;
--DESCRIBE EXTENDED t_calcBasePos;

-- Daten abfragen
--SELECT * FROM t_fbFieldPos EMIT CHANGES;
--SELECT * FROM t_rawMetaPlayer EMIT CHANGES;
--SELECT * FROM t_calcBasePos EMIT CHANGES;
