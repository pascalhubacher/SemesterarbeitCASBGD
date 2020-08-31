###############################################################################
# use an existing docker image 
FROM python:3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# update python 3
#RUN apk add --update python3

###############################################################################
# download and install dependencies

# GitHub support
# install git
#RUN apk add --update git

# clone repository with data
#RUN git clone https://github.com/pascalhubacher/SemesterarbeitCASBGD.git

# copy the simulator.py application
COPY ./simulator.py .

# copy the list of all packages to be installed
COPY ./requirements.txt .

# copy all the game data to the image
COPY ./data/ ./data/

# update pip
RUN pip install --upgrade pip

# install the needed packages
RUN pip install --no-cache-dir -r requirements.txt

###############################################################################
# start the simulator
#CMD ["python3", "./simulator.py"]

#docker build -t pascalhubacher/simulator:latest .
#docker run -it pascalhubacher/simulator bash