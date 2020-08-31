###############################################################################
# use an existing docker image 
FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

###############################################################################
# download and instll dependencies (to be able to use netcat)
RUN echo 'deb [check-valid-until=no] http://archive.debian.org/debian jessie-backports main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install dos2unix
RUN apt-get install -y netcat && apt-get autoremove -y && apt-get install dos2unix -y

# clone repository with data
#RUN git clone https://github.com/pascalhubacher/SemesterarbeitCASBGD.git

#copy the list of all packages to be installed
COPY ./requirements.txt .

#copy all the game data to the image
#COPY ./data/ ./data/

#update pip
RUN pip install --upgrade pip

#install the needed packages
RUN pip install --no-cache-dir -r ./requirements.txt

# copy wait for Kafka and Schema Registry  
COPY ./wait_for_services.sh .
# convert the file from windows format to unix format
RUN dos2unix -ascii wait_for_services.sh

#copy python faust worker script
#create the topic if needed for the faust listener because if it does not exist the faust listener stops 
COPY ./create_topic.py .
#faust listener
COPY ./worker_1.py .

#to create an event manually with faust (testing)
#faust -A create_event send @greet '{"ts": "40", "x": "-0.38", "y": "-2.23", "z": "0.0", "id": "10"}'
COPY ./create_event.py .

###############################################################################
ENTRYPOINT ["./wait_for_services.sh"]

# start the a script
#CMD ["python3", "./worker_test.py"]

#docker build -t pascalhubacher/faust:latest .
#docker run -it pascalhubacher/faust bash