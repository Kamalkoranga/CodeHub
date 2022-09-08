# start by pulling the python image
FROM python:3.8-alpine

# copy the requirements file into the image
COPY ./requirements.txt /codehub/requirements.txt

# switch working directory
WORKDIR /codehub

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /codehub

# configure the container to run in an executed manner
CMD [ "python", "./app.py"]