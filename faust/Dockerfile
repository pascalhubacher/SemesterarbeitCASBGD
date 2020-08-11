###############################################################################
# use an existing docker image 
FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

###############################################################################
# download and instll dependencies (to be able to use netcat)
RUN echo 'deb [check-valid-until=no] http://archive.debian.org/debian jessie-backports main' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y netcat && apt-get autoremove -y

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

#copy script to wait for kafka, schema registry
COPY ./wait_for_services.sh .

# change directory to the simulator folder 
#WORKDIR "/usr/src/app/faust"

###############################################################################
# start the simulator
#CMD [ "python3", "./faust.py" ]

#docker build -t pascalhubacher/faust:latest .
#docker run -it pascalhubacher/faust sh