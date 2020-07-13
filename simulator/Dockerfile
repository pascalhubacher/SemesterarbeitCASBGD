###############################################################################
# use an existing docker image 
FROM python:3

WORKDIR /usr/src/app

###############################################################################
# download and instll dependencies

# install git
RUN apt-get update && apt-get install -y git

# clone repository with data
RUN git clone https://github.com/pascalhubacher/SemesterarbeitCASBGD.git

# change directory to the simulator folder 
WORKDIR "/usr/src/app/SemesterarbeitCASBGD/simulator"

# install the needed python packages 
RUN pip install --no-cache-dir -r requirements.txt

###############################################################################
# start the simulator
CMD [ "python", "./simulator.py" ]

#docker build .
