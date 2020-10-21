# Semesterarbeit CAS BGD FS20

## Intro
Im Spitzenfussball gehört es heute zum Standard, dass die Spielerdaten während eines Spiels auf-gezeichnet und ausgewertet werden. Nach dem Spiel können so Leistungsdaten je Spieler (Lauf-wege, Ballkontakte, gewonnene/verlorene Zweikämpfe etc.) ermittelt werden. Ein immer wichtigerer Teil nimmt dabei die Analyse von Datenströmen zu Echtzeit ein.
Im Rahmen dieser Semesterarbeit wollen wir die einzelne Komponente der Stream-Analyse und der Event-Detection an konkreten Spieldaten anzuwenden und erste Erfahrungen zu sammeln.

## Ziel der Semesterarbeit
Wir gehen die Projektarbeit aus Sicht «Data Scientist» an und weniger
als «Informatiker». Uns ist wichtig zu erfahren, wie mit den Werkzeugen
eines Data Scientist eine Stream-Verarbeitung sinnvoll gestaltet werden
kann. Der Fokus liegt dabei auf folgenden Themen:

-   Event-Detection\
    > Erkennen von Spielsituationen auf Basis der Positionsdaten (x/y)
    > von Spieler und Ball

-   Einsetzen von Stream Processing Tools\
    > Anwenden von ksql und Python/Faust (Data Scientist Toolset) sowie
    > die Einbindung bereits bekannter Technologien (C\#/.net)

-   Erstellen von Producer und Consumer\
    Input: Sensorsimulator (Python)\
    Output: Datenablage in externer Datenbank (.net)

-   Aufbau Kafka-Streaming-Plattform\
    Im Zentrum steht die Systembereitstellung in einer
    Entwicklungsumgebung auf einem lokalen Windows-System, basierend auf
    Docker. Die Partitionierung und Replikation der Daten steht dabei
    nicht im Fokus.

## Einführung
Die vorliegende Arbeit basiert auf den individuellen
Positionsdatenströme der 22 Spieler und des Balls aus dem UEFA Nations
Leauge Spiel zwischen Portugal und der Schweiz vom Juni 2019. Infos zu
Spiel sind auf der Website der UEFA[^1] zu finden:

In diesem Kapitel werden einige Grundlagen rund um das Spielfeld
definiert und die Inputdaten erklärt

### Input Daten
Basis für die Event-Detection sind die Positionsdaten des Balls sowie
der 22 Spieler (1 Torhüter und 10 Feldspieler je Team). Die
Positionsdaten der 23 Objekte werden alle 40ms ermittelt, was einer
Sampling-Rate von 25Hz entspricht.

Die Daten stehen als CSV-Datei zur Verfügung. Je Objekt eine Datei. Zur
Simulation eines Live-Spiels werden die Objektdaten mit Hilfe eines
Simulator-Scripts in das System eingespeist.

Beispieldaten (CSV); Positionsdaten eines Spielers mit drei Messwerten:

Timestamp,\"X\",\"Y\",\"Z\",\"ID\"

40,50.92,1.15,0.0,101

80,50.86,1.16,0.0,101

120,50.79,1.14,0.0,101

Ein Datenpaket (Zeile) je Objekt umfasst folgende Informationen:

[]{#_Toc52468119 .anchor}Tabelle : Input Daten Informationen

+-----------+----------+---------------------------------------------+
| Datenfeld | Datentyp | Beschreibung                                |
+===========+==========+=============================================+
| Timestamp | Integer  | Synchronisierter Zeitstempel in \[ms\] für  |
|           |          | alle Objekte eines Spiels; Start bei 0;     |
|           |          | Frequenz 25 Hz                              |
+-----------+----------+---------------------------------------------+
| X         | Float    | X-Achsenwert der Objektposition in Meter    |
|           |          | \[m\]                                       |
+-----------+----------+---------------------------------------------+
| Y         | Float    | Y-Achsenwert der Objektposition in Meter    |
|           |          | \[m\]                                       |
+-----------+----------+---------------------------------------------+
| Z         | Float    | Nicht verwendet; fix 0                      |
+-----------+----------+---------------------------------------------+
| ID        | Integer  | SensorId; Eindeutige Kennung des Objekts    |
|           |          | (Spieler, Ball)                             |
|           |          |                                             |
|           |          | Konvention:                                 |
|           |          |                                             |
|           |          | ID \< 100 Spieler Heimteam\                 |
|           |          | ID \> 100 Spieler Gastteam\                 |
|           |          | ID = 200 Ball Ball                          |
+-----------+----------+---------------------------------------------+
