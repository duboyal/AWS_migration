FROM python:3.8-slim-buster

COPY requirements.txt .
COPY main.py .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "main.py"]


# FROM python:3

# RUN pip3 install pandas boto3

# CMD ["python3"]

# ok basically you need to figure out if the 
# code will run from a docker image
# like say this docker file will excute the python program maybe it 
# Will just run python3 code.py

# yeah and that code will run taking in things from environment variables
# so need to googlebbt when a fargate task runs a task does it just run an 
# image or docker file that creates an image that executes code

# and how are variables passed to the fragate task

# ----
# some progress i can do is to try to set up mega environment variables in yaml


# try to code the python using real nimage environment vars
# remember that env vables come from probably env in this file and MyFargateTask in main 

# try to  code the env variables at the top of each yaml file for now
# using parameters or env: similar to the other 

# basically you are done after that 
# you just need the two   s3 buckets, one that takes in the xlsx files as raw data 
# wish there was a csv bucket but its overkill
# and then antother that  puts it into parquet 

# so 

# two  s3 buckets 
