FROM python:3.8-slim-buster

COPY requirements.txt .
COPY main.py .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python3", "main.py"]


# ----- old notes
# FROM python:3
# RUN pip3 install pandas boto3
# CMD ["python3"]

# when you run a Fargate task, it will start a container based on the Docker image you specify in the task definition. 
# The container is responsible for executing the code inside the image. You can specify environment variables in the task 
# definition that will be passed to the container when it starts. These environment variables can be 
# used by your code to configure the behavior of your application.


# ----

# ENV AWS_ACCESS_KEY_ID=your_aws_access_key_id
# ENV AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# those lines are typically not added directly in the Dockerfile. Instead, the credentials or 
# AWS configuration should be passed to the container at runtime, for example via environment variables 
# or using an external secrets manager. This ensures that the sensitive information is not hardcoded in 
# the Dockerfile or the container image itself, which can be a security risk.

# If you are using an AWS service to run your container, such as ECS or EKS, you can also use IAM roles to 
# grant the necessary permissions to your containers without having to pass in AWS credentials directly.
