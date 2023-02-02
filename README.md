# AWS migration 


#### disclaimer : testing was limited for this pipeline and is mainly just an overall big picture of a potentially deployable self contained infrastructure as code , even the dockerfile and container registry is mocked up in theory to be pushed as IaC yaml , by potentially terraform/serverless framework etc.

## Steps in Pipeline:
1. [AWS Data Sync to "Raw" S3 Bucket](README.md#DataSync)
2. Event on S3 bucket to trigger step function state machine
3. step function state machine launches fargate task (python data-processing code is on container used for fargate task and we have IaC to create this container)
4. fargate task proccesses and updates data and saves to parquet files in "Transformed" S3 Bucket
5. Glue Service (ran on a cron job or ran manually) crawls transformed bucket and creates appropriate athena tables

#### data processing code : [main.py](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/main.py) which imports [table_module.py](https://github.com/duboyal/AWS_migration/blob/main/my-infrastructure/codebuild/table_module.py)

should be found within the [codebuild](https://github.com/duboyal/AWS_migration/tree/main/my-infrastructure/codebuild) folder under main.py, and table_module imported into that. In that directory you'll also find the docker file which runs main and reads in the input file name as one of its environment variables that is defined in the fargate task IaC yaml files . 

parquet files are my chosen filetype to to save things to because they are good if multiple actions or functions need to read/write to the file at once it is safer against data corruption , perhaps not in this pipeline but in alternate more scalable pipelines that implement fanning out lambda functions 

## Other considerataions:

I thought about the use of lambda , but lambda's limitations are that it will time out after 15 minutes and also cannot hold pandas library without implementing lambda layers. In retrospect I could have used SQS or lambda to trigger the fargate task instead of state functions, I chose state fucntions because you seem to have more control over the flow of the job, and will have more options to handle errors and retries.

#### thoughts on scalability:
If I really needed to "scale up" I would do the following, (it would have taken me a while to configure and provision for this exercise but here is what I would do)

I would set up an s3 bucket that could take files and send rows from the csv over in "batches" (like 10 rows would be a batch) from the files to SQS queue events. I would design a python class framework extract these batches from the csv file , ( say 10 lines from a csv would be a batch of size 10 and this number could be dynamic)

that would then send these "batches" to an instance of lamda fucnction (or lambda handler) to conduct the transforming the data. these sqs events would spin up lambdas for processing and All these lambda instances would save to a parquet file to a "transformed" s3 bucket that has a glue crawler attached to it where the glue crawler would be set up to read data from multiple files within the transformed s3 bucket . the file format of parquet is especially useful here because it is the safest for when multiple functions need to add to a file at once .

I am also interested into looking at AWS Batch that natively integrates with S3, it allows you to configure S3 events to trigger batch jobs. AWS Batch can automatically create the necessary resources (Fargate task, etc) and schedule the job to run.



## DataSync:

Data sync would require the installation of a "data sync agent" on the source machine and have access to the destination s3 bucket through VPN or make your bucket public but it is more secure to configure the allowed traffic into the bucket through VPN
[https://docs.aws.amazon.com/datasync/latest/userguide/deploy-agents.html]


