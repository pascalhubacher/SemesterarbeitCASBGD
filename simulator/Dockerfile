# use an existing docker image 
FROM python:3

WORKDIR /usr/src/app

# download and instll dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#copy the python script to the simulator
COPY simulator.py .

#copy the data to the simulator
COPY data ./data

# tell the image what to do when it starts
# as a container
#CMD [ "python", "./simulator.py" ]