import pandas as pd
from datetime import datetime 
import time
import uuid
import io
import boto3
from os import environ as env
import smart_open
import awswrangler as wr

raw_bucket =  env["RAW_BUCKET_NAME"]  #'alibucket11'
transformed_bucket = env["TRANSFORMED_BUCKET_NAME"] 
object_key = env["OBJECT_KEY"] 


# ------------- HELPER FUNCTIONS 


def create_seperate_dfs( df_bor , df_rp ): #, created_at, created_by): 
    '''
    takes in dataframes, returns a dict of dataframes
    MAKE IT RETURN A DICT of 9 DFS from our EXCEL DFS 
    df_user_profile, df_user, df_role_profile, df_role_profile_type, df_email, df_email_type, df_address, df_phone_number, df_phone_number_type
    makes dfs from the imported xlsx files 
    takes in two dataframes and returns dict of seperate data frames

    '''
    created_at = datetime.now()
    updated_at = datetime.now()
    created_by = "ADMIN" # default value as admin but get it from AWS ENVIRONMENT VARS LIKE IAM ROLE

    updated_by = "<ENVIRONMENT VAR FROM IAM ROLE>" #this can be set in the fargate task definition!

    data = {'created_date':[created_at], 'created_by':[created_by], 'updated_date':[updated_at], 'updated_by':[updated_by]}
    df_general = pd.DataFrame(data)
    n = len(df_bor)
    rows = [df_general.iloc[i] for i in range(df_general.shape[0])]*n
    df_general = pd.DataFrame(rows)
    df_general.reset_index(drop = True, inplace = True)


    #ok here wwwe need to fix shit 
    # df_general = df_general.reindex(range(len(df_bor))) ## Use the reindex() method to add rows with the same constant values

    df_user_profile = df_general.copy()
    df_user = df_general.copy()
    df_role_profile = df_general.copy()
    df_role_profile_type = df_general.copy()
    df_email  = df_general.copy()
    df_email_type = df_general.copy()
    df_address  = df_general.copy()

    df_phone_cell = df_general.copy()
    df_phone_home = df_general.copy()

    df_phone_number = df_general.copy()
    df_phone_number_type  = df_general.copy()

    try:
        role_profile_id_col = df_rp['borrower_id']
        user_profile_id_col = df_bor['id']


        df_user_profile["user_profile_id"] = user_profile_id_col
        df_user_profile["first_name"] = df_bor['full_name'].apply( lambda x: x.split(" ")[0] ) # split names outof original field  #apply lambda string.split() thing 
        df_user_profile["last_name"] = df_bor['full_name'].apply( lambda x: x.split(" ")[1] )
        #----------------
        df_user["user_id"] = [uuid.uuid4().int for i in range(len(df_bor))] # ... eventually will need a string of uuids like a list comprehension in a range
        df_user["user_profile_id"] = df_user_profile["user_profile_id"]
        #-----------------
        df_role_profile_type["role_profile_type_id"]  = role_profile_id_col
        df_role_profile_type["type"]  = df_rp["role_profile"]
        df_role_profile["role_profile_id"]  = [uuid.uuid4().int for i in range(len(df_rp))]
        df_role_profile["user_id"]  = df_user["user_id"]
        df_role_profile["role_profile_type_id"] = df_role_profile_type["role_profile_type_id"]
        #--------------------
        df_email["email_id"] = [uuid.uuid4().int for i in range(len(df_bor))] #supposedly this increments ok but not by 1 maybe i can make it 
        df_email["role_profile_id"] = df_role_profile["role_profile_id"] 
        df_email["email_type_id"] = [uuid.uuid4().int for i in range(len(df_bor))]
        df_email["value"] = df_bor["email"] 
        #-----------------------
        df_email_type["email_type_id"] = [uuid.uuid4().int for i in range(len(df_bor))] #supposedly this increments ok but not by 1 maybe i can make it 
        df_email_type["type"] = "gmail"
        #---------------------
        df_address["address_id"] = [uuid.uuid4().int for i in range(len(df_bor))] #supposedly this increments ok but not by 1 maybe i can make it 
        df_address["role_profile_id"] = df_role_profile["role_profile_id"] 
        df_address["street"] = df_bor["street"] 
        df_address["city"] = df_bor["city"] 
        df_address["state"] = df_bor["state"] 
        df_address["zip_code"] = df_bor["zip_code"] 


        df_phone_cell['value'] = df_bor["phone_cell"]
        df_phone_cell['role_profile_id'] = df_bor['id']

        cell_type_id = uuid.uuid4()
    
        df_phone_cell['phone_number_type_id'] = [cell_type_id for i in range(len(df_bor))]

        df_phone_home['value'] = df_bor["phone_home"]
        df_phone_home['role_profile_id'] = df_bor['id']
        home_type_id = uuid.uuid4()

        df_phone_home['phone_number_type_id'] = [home_type_id for i in range(len(df_bor))]
        df_phone_number = df_phone_home.append(df_phone_cell)
        df_phone_number['phone_number_id'] = [uuid.uuid4().int for i in range(len(df_phone_number))]

        unique_type_ids = df_phone_number['phone_number_type_id'].unique()
        df_phone_number_type = df_phone_number[df_phone_number['phone_number_type_id'].isin(unique_type_ids)]
        df_phone_number_type['type_id'] = df_phone_number_type['phone_number_type_id']

        df_phone_number_type['type'] = df_phone_number_type['type_id'].map({cell_type_id:'cell', home_type_id:'home'})
    
    except Exception as e:
        print(e)


    df_dict = {"df_user_profile" : df_user_profile,
                "df_user" : df_user,
                "df_role_profile_type" : df_role_profile_type,
                "df_role_profile" : df_role_profile,
                
                "df_email" : df_email,
                "df_email_type" : df_email_type,

                "df_address" : df_address,
                "df_phone_number" : df_phone_number,
                "df_phone_number_type" : df_phone_number_type,
                }
    return df_dict




def dfs_from_parquets(par_files): 
    '''
    pass in a list of files reads them into a dict of data frames
    '''
    parq_to_df_dict = {}
    for item in par_files:
        key1 = item.replace("./", "").replace("_parquet.parquet", "_fromparq") #expecting this formaat could make things better
        # parq_to_df_dict[key1] = pd.read_parquet(item) #oops need to open w smart open
        parq_to_df_dict[key1] = wr.s3.read_parquet(path=f's3://{transformed_bucket}/{item}')

    return parq_to_df_dict



def aggregate_df(df_new,df_parquet ):
    '''
    this function will compare two dfs , one that gets lloaded in 
    and one thats incoming. it will take the difference and will update accordingly 
    I think if it is there in the old one and not in the new one then it should 
    delete from the new one 
    '''
    df = pd.concat([df_new,df_parquet])
    mask = df.duplicated(subset=['A', 'B','C'], keep=False)
    df_duplicate = df[mask].groupby(['A', 'B','C']).agg({'created_at':'first', 'updated_at':'last'}).reset_index()
    df_nonduplicate = df[~mask]
    df_final = pd.concat([df_nonduplicate,df_duplicate])
    df_final.reset_index(inplace=True, drop=True)
    return df_final



def dfs_to_parquets(df_dict):
    '''
    takes in dict of dfs and saves them to parquet files 
    '''
    for key, df in df_dict.items():
        # save as parquet 
        s3 = boto3.client('s3')
        # df.to_parquet(f"{key}_parquet.parquet", engine='pyarrow')
        file_name = f"{key}_parquet.parquet" # could use a key
        wr.s3.to_parquet(df=df, path=f's3://{transformed_bucket}/{file_name}')