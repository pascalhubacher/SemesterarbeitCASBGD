###############################################################################
# use an existing docker image 
#alpine image latest
FROM alpine

WORKDIR /usr/src/app

###############################################################################
# download and instll dependencies

# install git
RUN apk add --update git
# install python 3
RUN apk add --update python3
#install pip
RUN apk add --update py3-pip

# clone repository with data
RUN git clone https://github.com/pascalhubacher/SemesterarbeitCASBGD.git

# change directory to the simulator folder 
WORKDIR "/usr/src/app/SemesterarbeitCASBGD/simulator"

###############################################################################
# start the simulator
#CMD [ "python3", "./simulator.py" ]

#docker build -t pascalhubacher/simulator:latest .
#docker run -it pascalhubacher/simulator sh