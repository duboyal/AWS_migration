import glob
import os
import sys
from os import environ as env
import uuid 
import boto3
import io
import pandas as pd
import pyarrow as pa   #pip install --upgrade mock need to put this on the dicker container
import json
import openpyxl
import smart_open
import awswrangler as wr
import time, datetime

sys.path.append(".")
import table_module as tm



# Create a session to interact with Secrets Manager
session = boto3.Session()
client = session.client('secretsmanager')
# Get the secret value
response = client.get_secret_value(SecretId='SECRET_NAME')
secret_value = response['SecretString']

# Parse the secret value to get the access key and secret key
# assumes the secret is set up accordingly on AWS

secret_json = json.loads(secret_value)
access_key = secret_json['access_key']
secret_key = secret_json['secret_key']

raw_bucket =  env["RAW_BUCKET_NAME"]  
transformed_bucket = env["TRANSFORMED_BUCKET_NAME"] 


raw_object_key = env["RAW_OBJECT_KEY"] 
transformed_object_key = env["TRANSFORMED_OBJECT_KEY"] 

s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)


sheet_name_bor = env["SHEETNAME_1"] #"borrower"
sheet_name_rp = env["SHEETNAME_2"] #"role_profile"

df_bor = wr.s3.read_excel(path=f's3://{raw_bucket}/{raw_object_key}', sheet_name=sheet_name_bor)
df_rp = wr.s3.read_excel(path=f's3://{raw_bucket}/{raw_object_key}', sheet_name=sheet_name_rp)

new_df_dict = tm.create_seperate_dfs(df_bor, df_rp) # I should make them key word args to be explicit


prefix = '' #env["PREFIX"]

# Use the list_objects method to get a list of files from transformed
result = s3.list_objects(Bucket=transformed_bucket, Prefix=prefix)
# Extract the files from the response
files = result.get('Contents', [])
extension = ".parquet"
filtered_files = [file for file in files if file['Key'].endswith(extension)]
par_files = [file['Key'] for file in filtered_files]


old_df_dict = tm.dfs_from_parquets(par_files)

# compare and aggregate dfs
# for each item in dict, compare the two dfs

df_final_dict = {}

for key, value in new_df_dict.items():
    if key in old_df_dict.keys():
        df_final = tm.aggregate_df(new_df_dict,old_df_dict)
        df_final_dict[key] = df_final

# lastly saving to parquet using the keys
tm.dfs_to_parquets(df_final_dict)

