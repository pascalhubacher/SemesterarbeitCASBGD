# Semesterarbeit CAS BGD FS20

## Goal
Wir gehen die Projektarbeit aus Sicht «Data Scientist» an und weniger als «Informatiker». Uns ist wichtig zu erfahren, wie mit den Werkzeugen eines Data Scientist eine Stream-Verarbeitung sinnvoll gestaltet werden kann. Der Fokus liegt dabei auf folgenden Themen:
•	Event-Detection
Erkennen von Spielsituationen auf Basis der Positionsdaten (x/y) von Spieler und Ball

•	Einsetzen von Stream Processing Tools 
Anwenden von ksql und Python/Faust (Data Scientist Toolset) sowie die Einbindung bereits bekannter Technologien (C#/.net)

•	Erstellen von Producer und Consumer
Input: Sensorsimulator (Python)
Output: Datenablage in externer Datenbank (.net)

•	Aufbau Kafka-Streaming-Plattform
Im Zentrum steht die Systembereitstellung in einer Entwicklungsumgebung auf einem loka-len Windows-System, basierend auf Docker. Die Partitionierung und Replikation der Daten steht dabei nicht im Fokus.

## Tools

### Simulator
