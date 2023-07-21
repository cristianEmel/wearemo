# Use a base image with Python
FROM python:3.9

# Set the working directory in the container
WORKDIR /wearemo

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the requirements.txt file to the container
# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application code to the container
COPY . .

RUN python wearemo/manage.py test 
