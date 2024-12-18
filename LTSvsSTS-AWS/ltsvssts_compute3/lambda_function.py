#
# Python program to open and process 20 large CSV file, extracting
# all numeric values from the document for counting number of cells
#

import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier
import urllib.parse
import string
import pandas as pd
import numpy as np
from io import StringIO

from configparser import ConfigParser

def count_matrix(s3_client, bucket, filelist, bucketkey, dbConn):
    count_matrix = {}
    row_names = ["Cells"]

    total = len(filelist)
    filenum = 1
    for file_key in filelist:
        print(f"Processing file: {file_key}")

        obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        csv_body = obj['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_body))

        column_name = pathlib.Path(file_key).stem
        row_count = len(df.index)
        count_matrix[column_name] = row_count

        status = 'processing - ' + str(file_key[14:]) + ' ' + str(filenum) + '/20 processed'
        filenum += 1
        sql = "update jobs set status = %s where datafilekey = %s"
        modified = datatier.perform_action(dbConn, sql, [status, bucketkey])

    return pd.DataFrame(count_matrix, index=row_names)

  
def lambda_handler(event, context):
  dbConn = None
  try:
    print("**STARTING**")
    print("**lambda: ltsvssts_compute3**")
    
    bucketkey_results_file = ""
    
    # setup AWS based on config file:
    config_file = 'ltsvsstsapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    # configure for S3 access:
    s3_profile = 's3readwrite'
    boto3.setup_default_session(profile_name=s3_profile)
    
    bucketname = configur.get('s3', 'bucket_name')
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    bucket = s3.Bucket(bucketname)

    # configure for RDS access
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    # this function is event-driven by a json being
    # dropped into S3. The bucket key is sent to 
    # us and obtain as follows:
    bucketkey = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    print("bucketkey:", bucketkey)
      
    if not bucketkey.startswith("LTSvsSTS3-Template/"):
            raise Exception("File is not in 'LTSvsSTS3-Template/' folder. Ignoring event.")
        
    extension = pathlib.Path(bucketkey).suffix
    
    if extension != ".json" : 
      raise Exception("expecting S3 document to have .json extension")
    
    bucketkey_results_file = "LTSvsSTS-Result/" + bucketkey[19:-5] + ".json"
    
    print("bucketkey results file:", bucketkey_results_file)
      
    # download JSON from S3 to LOCAL file system:
    print("**DOWNLOADING '", bucketkey, "'**")

    local_json = "/tmp/data.json"
    
    bucket.download_file(bucketkey, local_json)


    # open LOCAL json file:
    print("**PROCESSING local JSON**")
    with open(local_json, 'r') as f:
            data = json.load(f)

    thresholddict = data['THRESHOLDS']
    phenotypedict = data['PHENOTYPES']
    filelist = list(thresholddict.keys()) 
    
    # update status column in DB for this job,
    print("**Opening DB connection**")
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    status = 'processing - starting'
    sql = "update jobs set status = %s where datafilekey = %s"
    modified = datatier.perform_action(dbConn, sql, [status, bucketkey])

    df = count_matrix(s3_client, bucketname, filelist, bucketkey, dbConn)

    result_json = df.to_json(orient='index')
    s3_client.put_object(Bucket=bucketname, Key=bucketkey_results_file, Body=result_json)

    status = 'completed'
    datatier.perform_action(dbConn, sql, [status, bucketkey])
    sql = "update jobs set resultsfilekey = %s where datafilekey = %s"
    datatier.perform_action(dbConn, sql, [bucketkey_results_file, bucketkey])
    print("**DONE**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("success")
    }
    
  # on an error, try to upload error message to S3:
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    # update the database if connection is established
    if dbConn is not None:
        status = 'error'
        sql = "update jobs set status = %s, resultsfilekey = %s where datafilekey = %s"
        datatier.perform_action(dbConn, sql, [status, bucketkey_results_file, bucketkey])
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }