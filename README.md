# AWS migration 


#### disclaimer : testing was limited for this pipeline and is mainly just an overall big picture of a potentially deployable self contained infrastructure as code , even the dockerfile and container registry is mocked up in theory to be pushed as IaC yaml , by potentially terraform/serverless framewwork etc.

## Steps in Pipeline:
1. [AWS Data Sync to "Raw" S3 Bucket](README.md#problem)
2. [Event on S3 bucket to trigger step function state machine](README.md#Dataset)
3. [step function state machine launches fargate task](README.md#File-Descriptions)
4. [fargate task proccesses and updates data and saves to parquet files in "Transformed" S3 Bucket](README.md#LSUN)
5. [Glue Service (run on a cron job or ran manually) crawls transformed bucket and creates appropriate athena tables](README.md#Plugin)

## Other considerataions:

Thought about use of lambda , but lambda's limitations are that it will time out after 15 minutes and also cannot hold pandas library without implementing lambda layers. In retrospect I could have used SQS or lambda to trigger the fargate task instead of state functions, I chose state fucntions because you seem to have more control

#### thoughts on scalability:
If I really needed to "scale up" I would do the following, though it would have taken me too long to figure this out and provision for this exercise but here is what I would do .

I would set up an s3 bucket that could take files and send batches of rows from the files to SQS queue events that would then send their respective "batches" to an instance of lamda fucnction (or lambda handler) to conduct the transforming the data. all these instances would save to a parquet file to a "transformed" s3 bucket that has a glue crawler attached to it where the glue crawler would be set up to read data from multiple files within the transformed s3 bucket . the file format of parquet is especially useful here because it is the safest for when multiple functions need to add to a file at once .



## Problem:



## Dataset:

The datasets website and information:
http://lsun.cs.princeton.edu/2017/

Instructions on how to download the dataset:
https://github.com/fyu/lsun



## General Structure:

The directory structure for your repo should look like this:
```
      ├── LSUN
      │     └──.ipynb_checkpoints
      │     └──utils
      │     │   └──LSUNDataloader.py
      │     └──Baseline_vs_meta.ipynb
      │     └──ConvertToTar.ipynb
      │     └──Dummy.ipynb
      │     └──ExperimentLog.csv
      │     └──LSUNGetTrainValFiles.ipynb
      │     └──LSUNResultsVisualization.ipynb
      │     └──PreprocessingLSUN.ipynb
      │     └──QueryDatastore.py
      │     └──Results_LSUN.csv
      ├── Plugin 
      │     └──content.js
      │     └──jquery-3.3.1.min.js	
      │     └──manifest.json
      │     └──popup.html
      │     └──popup.js
      │     └──script_deselect.php
      │     └──script_lasso.php
      ├── Plugin2
      │     └──content.js
      │     └──jquery-3.3.1.min.js	
      │     └──manifest.json
      │     └──popup.html
      │     └──popup.js
      │     └──script_deselect.php
      │     └──script_lasso.php
      ├── ActivationVisualization.ipynb
      ├── README.md 
      
```
      

# File Descriptions: 
## ./
### ./ActivationVisualization.ipynb
This is a nice visulaization of performing t-sne (similar to Principal component analysis) to see how well the model is able to seperate out the different classes. This is also very integral in showing us how likely the user is to pick up other 'classes' when trying to only select one class. in this case we encourage the user to select a small amount of classes at once when they are "lassoing" images

## LSUN/
### LSUN/utils/LSUNDataloader.py
This file defines the dataloader class, has class variable of a list of csvs saved, then has the get item attribute for a single image at once based on index, where the batch size is a variable defined in the code found in Baseline_vs_meta.ipynb, in which case the data loader would execute "get_item" that determined number of times.

### LSUN/Baseline_vs_meta.ipynb
This file is where the main network training happens and also communicates with the data loader. 
