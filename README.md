# Semesterarbeit CAS BGD FS20

# Stream-Processing als Basis für die taktische Analyse im Spitzenfussball

![](./media/image1.jpg)

## Intro
Im Spitzenfussball gehört es heute zum Standard, dass die Spielerdaten während eines Spiels auf-gezeichnet und ausgewertet werden. Nach dem Spiel können so Leistungsdaten je Spieler (Lauf-wege, Ballkontakte, gewonnene/verlorene Zweikämpfe etc.) ermittelt werden. Ein immer wichtigerer Teil nimmt dabei die Analyse von Datenströmen zu Echtzeit ein.
Im Rahmen dieser Semesterarbeit wollen wir die einzelne Komponente der Stream-Analyse und der Event-Detection an konkreten Spieldaten anzuwenden und erste Erfahrungen zu sammeln.

## Ziel der Semesterarbeit
Wir gehen die Projektarbeit aus Sicht «Data Scientist» an und weniger
als «Informatiker». Uns ist wichtig zu erfahren, wie mit den Werkzeugen
eines Data Scientist eine Stream-Verarbeitung sinnvoll gestaltet werden
kann. Der Fokus liegt dabei auf folgenden Themen:

-   Event-Detection
    > Erkennen von Spielsituationen auf Basis der Positionsdaten (x/y)
    > von Spieler und Ball

-   Einsetzen von Stream Processing Tools
    > Anwenden von ksql und Python/Faust (Data Scientist Toolset) sowie
    > die Einbindung bereits bekannter Technologien (C\#/.net)

-   Erstellen von Producer und Consumer
    > Input: Sensorsimulator (Python)
    > Output: Datenablage in externer Datenbank (.net)

-   Aufbau Kafka-Streaming-Plattform
    > Im Zentrum steht die Systembereitstellung in einer 
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

### Fussballfeld Koordinatensystem
Der Ursprung des Koordinatensystems liegt auf dem Spielfeldmittelpunkt.

![](./media/image4.png)

**Wichtig**: Die Spielfeldgrösse (Länge und Breite) ist nicht fix
definiert, sondern kann in einem reglementarisch definierten Bereich
variieren. Die Grösse von Strafraum, Torraum und Tor ist jedoch fix
definiert.

Die offizielle Vermassung und die Beschreibung des Fussballfelds sind
auf Wikipedia[^2] zu finden.

## Events

Auf Basis der Positionsdaten der Spieler und des Balls werden
verschiedene Ereignisse erkannt (Event detection). Events können von der
absoluten Spielfeldposition, Laufrichtung und Geschwindigkeit eines
Objekts abhängig sein, der relativen Geschwindigkeit oder des Abstands
zweier Objekte untereinander. Diese Zustände werden dann meist auch in
Abhängigkeit der Zeit betrachtet.

Zum Beispiel ein Ballbesitz kann definiert werden durch einen minimalen
Abstand zwischen zwei Objekten (Ball und Spieler) und der gleichen
Bewegungsrichtung.

Wir unterscheiden zwischen einfachen Events und komplexen Events.

-   Einfache Events: Ein Ereignis trifft ein, unabhängig von anderen
    Ereignissen. Zum Beispiel ein Objekt betritt oder verlässt eine
    bestimmte Spielfeldzone

-   Complex Event: Erkennung von Ereignismustern. Einfache Events werden
    zu Gruppen zusammengefasst und bilden ein übergeordnetes Ereignis.
    Mehrere Objekte stehen in Beziehung zueinander.

### Liste der Events

Die folgenden Events werden im Rahmen dieser Arbeit aus den Datenströmen
gefiltert.

#### Einfache Events; Zoneninformationen

Anhand der eingangs beschriebenen Spielfeldzonen wird erkannt, wann der
Ball eine definierte Zone verlässt oder in sie eindringt. Die
Ballposition(x/y) wird mit den Zonenkoordinaten
verglichen(x~min~/y~min~; x~max~/y~max~)

#### Complex Events; Ballbesitz

Der Ball ist das zentrale Objekt. Seine Position (x/y) wird mit den
Positionen der Spieler(x/y) über einem bestimmte Zeitpunkt verglichen.

Erkennt, ob ein Spieler im Ballbesitz ist und es vorher nicht war. Damit
dieser Event anschlägt, muss die Distanz des Spielers zum Ball unter 3
Meter sein und kein anderer Spieler näher beim Ball sein. Weiter muss
der Spieler innerhalb eines Zeitfensters von 1 Sekunde diesen Zustand
mehr als die Hälfte der Zeit innehalten.

## Infrastruktur

### Übersicht

Damit eine Umgebung ohne grosse Vorkenntnisse eingesetzt werden kann,
ist es wichtig, dass der Aufbau derselben einfach und fehlerresistent
ist. Bereits in einer vorangegangenen Arbeit wurde eine Umgebung
aufgebaut für die Analyse von Fussball Stream Daten. Diese wurde jedoch
lokal auf einem Server installiert und konnte nach der Arbeit nicht mehr
migriert und weiterverwendet werden.

Deshalb ist es ein Kernthema dieser Arbeit, dass die ganze Umgebung
folgende Eigenschaften haben muss:

-   Betriebssystemneutral

-   Einfach portierbar (Lokal/Cloud)
    > Minimalinstallation: Laptop (32GB RAM, Mehrere CPU Kerne)\
    > Maximalinstallation: Server oder Cloud Implementation

-   Schnell einsetzbar (30min)

-   Geringer Speicherbedarf

-   Einfache Erweiterbarkeit (Modularer Aufbau, Python, KSQL)

-   Einfache Entwicklung mit GitHub (Multiuserfähig, Änderungen
    nachverfolgbar)

-   Einfache Automatisierung

-   Kostengünstig

-   Enterprise Support

Aufgrund dieser Anforderungen haben wir uns für Docker entschieden.
Docker lässt sich auf allen gängigen OS installieren. Die Kommandos sind
fast identisch in der Anwendung.

Die hier verwendete Minimalumgebung wird mittels docker-compose
erstellt. Dabei werden die angepassten Images mittels Docker File
erstellt. Somit ist die ganz Umgebung einfach portierbar und
erweiterbar.

Die ganze Semesterarbeit[^3] ist eine Teamarbeit und bedarf, dass jede
Person jederzeit am Projekt arbeiten kann. Deshalb ist die ganze
Umgebung auf GitHub abgelegt und wird auch dort gepflegt.

Auf Windows 10 setzen wir GitHub Desktop ein und als Programmierumgebung
dient Visual Studio Code mit Python 3.7.

### Docker

Damit Docker verwendet werden kann, muss erst die Docker Umgebung
installiert werden. Diese beinhaltet den Docker Server (Docker Prozess)
und den Docker Client (Docker CLI). Mit dieser CLI (Docker und
Docker-Compose) kann anschliessend die ganze Umgebung betrieben werden.

Docker stellt eine Virtualisierung mittels Container dar. Die Container
sind jedoch keine volle OS Virtualisierung und deshalb ist deren
Platzbedarf meist massiv kleiner. Die Container werden immer aus einem
Image gestartet. Das Image stellt ein Filesystem Snapshot einer Unix
Umgebung dar.

Der Docker Hub stellt eine Vielzahl von offiziellen Images und auch
selbstkreierten Images (keine Qualitätskontrolle) bereit, welche direkt
mittels Docker CLI heruntergeladen werden können.

Ein Docker Hub Image dient meist als Basis und wird anschliessend
mittels einer deklarativen Konfigurationsdatei (DOCKERFILE) für die
weitere Verwendung angepasst und kann danach wieder als eigenes Image
lokal abgespeichert werden. Die Container sind untereinander
abgeschottet. Wollen die Container miteinander kommunizieren, müssen sie
dies über freigegebene TCP/IP Ports tun oder den Containern wird ein
geteiltes Verzeichnis im Container angehängt.

Damit nun eine ganze Umgebung, bestehend aus mehreren Containern,
einfach aufgebaut werden kann, braucht es die Docker-Compose CLI. Mit
dem Docker-Compose Kommando kann mittels einer deklarativen
Konfigurationsdatei (Docker-Compose.VML) eine ganze Umgebung in einem
gemeinsamen Netzwerk aufgebaut werden. Diese Umgebung kann danach als
Ganzes gestartet, gestoppt, neu aufgebaut oder abgebaut werden.

### Docker Umgebung

Die verwendete Docker Umgebung basiert auf der Docker-Compose[^4] Datei
von Guido Schmutz. Aufgrund dessen war es uns möglich, innerhalb
kürzester Zeit eine lauffähige Kafka Umgebung bereitzustellen.

Die Docker Umgebung ist in ein internes und ein externes Netzwerk
unterteilt (Internal_IP, External_IP), damit die gesamte Umgebung auch
sicher in der Cloud laufen kann. Durch die Unterteilung ist es möglich,
gewisse Ports der Applikationen nur im Docker Netzwerk verfügbar zu
machen und nur die zwingend benötigten Ports nach aussen zu öffnen.

![](./media/image5.png)
