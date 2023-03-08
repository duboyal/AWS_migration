# Provisioning self contained AWS migration including VPC
```
├── my-infrastructure
│   ├── codebuild
│   │   ├── Dockerfile
│   │   ├── buildspec.yaml
│   │   ├── codebuild-project.yaml
│   │   ├── requirements.txt
│   │   ├── table_module.py
│   │   └── main.py
│   ├── ecr
│   │   └── ecr-repository.yaml
│   ├── ecs
│   │   └── ecs-cluster.yaml
│   ├── fargatetask
│   │   └── fargate-task.yaml
│   ├── iam-roles
│   │   ├── codebuild-role.yaml
│   │   ├── ecs-task-role.yaml
│   │   ├── glue-crawler-role.yaml
│   │   ├── s3-access-role.yaml
│   │   └── step-functions-role.yaml
│   ├── s3
│   │   ├── datasync-task.yaml
│   │   └── glue-crawler-s3.yaml
│   ├── stepfunction
│   │   └── stepfunction_statemachine.yaml
│   ├── network
│   │   ├── vpc.yaml
│   │   ├── subnet.yaml
│   │   ├── security-group.yaml
│   │   ├── nat-gateway.yaml
│   │   └── internet-gateway.yaml
│   ├── serverless.yaml
│   └── package.json

```

#### disclaimer : testing was limited for this pipeline and is mainly just an overall big picture of a potentially deployable self contained infrastructure as code , even the dockerfile and container registry is mocked up in theory to be pushed as IaC yaml , by potentially terraform/serverless framework etc. I have deployed similar stacks - using AWS CloudFormation or AWS CDK to deploy the infrastructure in a test environment first, and then gradually adding more resources as I go.

## Steps in Pipeline:
#### 1. [AWS Data Sync to "Raw" S3 Bucket](README.md#DataSync)
#### 2. [Event on S3 bucket](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/s3/raw/datasync-task-s3.yaml) to trigger [step function state machine](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/stepfunction/stepfunction_statemachine.yaml) 
When an S3 bucket receives an object, it can trigger an S3 event notification. However, this event notification alone cannot directly trigger a Fargate task. Instead, you can create a Step Function that listens to the S3 event notification and then triggers the Fargate task. This way, the Step Function acts as an intermediary that can coordinate multiple AWS services to accomplish the desired outcome.

#### 3. [step function state machine](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/stepfunction/stepfunction_statemachine.yaml) launches fargate task (python data-processing code is on the docker container used for fargate task - we have IaC to create/launch this ecr/container from scratch via [buildspec.yaml](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/buildspec.yaml) and [codebuild-project.yaml](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/codebuild-project.yaml)
#### 4. fargate task proccesses and updates data and saves induvidual parquet files in "Transformed" S3 Bucket
#### 5. Glue Service (ran on a cron job or ran manually) crawls transformed bucket and creates appropriate athena tables from each parquet file. schema meta data is saved 

#### data processing code : [main.py](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/main.py) which imports [table_module.py](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/table_module.py)

should be found within the [codebuild](https://github.com/duboyal/AWS_migration/tree/main/my-infrastructure/codebuild) folder under main.py, and table_module imported into that. In that directory you'll also find the docker file which runs main and reads in the input file name as one of its environment variables that is defined in the fargate task IaC yaml files . 

parquet files are my chosen filetype to to save things to because they are good if multiple actions or functions need to read/write to the file at once it is safer against data corruption , if not totally relevant in this pipeline definitley a good practice in alternate more scalable pipelines that implement fanning out lambda functions 

## Other considerataions:

I thought about the use of lambda , but lambda's limitations are that it will time out after 15 minutes and also cannot hold pandas library without implementing lambda layers. In retrospect I could have used SQS or lambda to trigger the fargate task instead of state functions, I chose state fucntions because you seem to have more control over the flow of the job, and will have more options to handle errors and retries.

#### thoughts on scalability:
If I really needed to "scale up" I would do the following, (it would take a while to configure and provision for the scope exercise but here is what I would do)

I would set up an event-triggered s3 bucket that would take files and (lambda python code) would send rows from the csv over in "batches" (like 10 rows would be a batch) from the files to SQS queue events. I would design a python class framework extract these batches from the csv file , ( say 10 lines from a csv would be a batch of size 10 - this number could be dynamic)

that would then send these "batches" to an instance of lamda fucnction (or lambda handler) to conduct the transforming the data. these sqs events would spin up lambdas for processing and All these lambda instances would save to a parquet file to a "transformed" s3 bucket that has a glue crawler attached to it where the glue crawler would be set up to read data from multiple files within the transformed s3 bucket . the file format of parquet is especially useful here because it is the safest for when multiple functions need to add to a file at once .

I am also - for a project like this - interested into looking at AWS Batch that natively integrates with S3, it allows you to configure S3 events to trigger batch jobs. AWS Batch can automatically create the necessary resources (Fargate task, etc) and schedule the job to run.



## DataSync:

Data sync would require the installation of a "data sync agent" on the source machine and have access to the destination s3 bucket through VPN or make your bucket public but it is more secure to configure the allowed traffic into the bucket through VPN
[https://docs.aws.amazon.com/datasync/latest/userguide/deploy-agents.html]

## the "Serverless Framework" as an IaaC tool:

The Serverless Framework is a popular open-source tool that supports multiple cloud platforms and languages, and allows you to define your infrastructure using YAML or JSON files.

To use the Serverless Framework with your YAML files, you would typically follow these steps:

#
To deploy this with Serverless Framework, you would need to do the following:

Install the Serverless Framework CLI by running npm install -g serverless in your terminal.

Set up your AWS credentials in your terminal using the aws configure command. This will allow the Serverless Framework to access your AWS account.

Create a new Serverless service by running serverless create --template aws-python3 --path my-service in your terminal. This will create a new Serverless service with a basic serverless.yml file.

Copy the contents of your infrastructure YAML files into your serverless.yml file, replacing the existing resources section.

Update your serverless.yml file to include any necessary environment variables, deployment options, and Serverless Framework plugins or settings in the provider and plugins sections.

Run sls deploy in your terminal to deploy your service to AWS.

Note that this assumes that you have already set up the necessary dependencies, such as Docker and AWS CLI, on your local machine.

#--more generally

Install the Serverless Framework: Install the Serverless Framework on your local machine or on your deployment server, following the installation instructions for your platform.

Configure your Serverless project: Create a new Serverless project, or configure an existing project to work with your YAML files. This involves setting up your project structure, defining your AWS account credentials, and specifying any necessary plugins or dependencies.

Write your Serverless YAML files: Create your YAML files that define your infrastructure components, such as your serverless functions, event triggers, and associated resources. Each YAML file should contain the necessary configuration settings for the component you want to deploy.

Define your Serverless deployment: Write a Serverless deployment script that specifies how to deploy your infrastructure components using the Serverless Framework. This script should reference your individual YAML files and specify any necessary deployment options or variables.

Deploy your infrastructure: Run your Serverless deployment script using the Serverless Framework. This will read in your individual YAML files and deploy your infrastructure components to your AWS account.

By following these steps, you can use the Serverless Framework to deploy your YAML files containing infrastructure as code, while also taking advantage of the tool's other features and benefits.

# VPC network design :
Based on the steps you described in your pipeline, here's what your VPC, network, and gateways might look like:

1) VPC: You would need a VPC to isolate your resources and create a private network for your data processing pipeline. This VPC should have at least two private subnets and two public subnets (for Fargate and Glue), and it should be configured with appropriate network ACLs and security groups to control traffic to and from your resources. You may also need to configure a VPC endpoint for S3 to allow your resources to access the "Raw" and "Transformed" S3 buckets without going over the public internet.

2) Internet Gateway: To allow your resources in the public subnets to access the internet, you would need to attach an Internet Gateway to your VPC. This would allow you to route traffic from your public subnets to the internet and back.

3) NAT Gateway: To allow your resources in the private subnets to access the internet (for example, to download packages or updates), you would need to set up a NAT Gateway in your public subnets. This would allow your resources to send traffic to the internet through the NAT Gateway, which would then translate the traffic and send it back to your resources.

4) Route Tables: You would need to configure your VPC with appropriate route tables to direct traffic between your subnets and gateways. For example, you would need to route traffic from your private subnets to the NAT Gateway and traffic from your public subnets to the Internet Gateway.

Overall, your VPC, network, and gateways would need to be designed to support the traffic flow and security requirements of your data processing pipeline. The specific configuration would depend on the size and complexity of your pipeline, as well as any additional requirements you may have for security, compliance, or performance.
