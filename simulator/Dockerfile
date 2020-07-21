###############################################################################
# use an existing docker image 
#alpine image latest
FROM alpine:edge

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

###############################################################################
# download and instll dependencies

# install git
#RUN apk add --update git

# install python 3
RUN apk add --update python3
#install pip
RUN apk add --update py3-pip

RUN apk update && apk add --no-cache python3 librdkafka && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache

# clone repository with data
#RUN git clone https://github.com/pascalhubacher/SemesterarbeitCASBGD.git

#copy the simulator.py
COPY ./simulator.py .

#copy the list of all packages to be installed
COPY ./requirements.txt .

#copy all the game data to the image
COPY ./data/ ./data/

#RUN pip3 install --no-cache-dir -r requirements.txt

# change directory to the simulator folder 
#WORKDIR "/usr/src/app/simulator"

###############################################################################
# start the simulator
#CMD [ "python3", "./simulator/simulator.py" ]

#docker build -t pascalhubacher/simulator:latest .
#docker run -it pascalhubacher/simulator sh