#
# Downloads the requested job from the LTSvsSTSapp DB, checks
# the status, and based on the status returns results
# to the client. The status can be: uploaded or completed
# completed, or error. In the case of completed, the 
# analysis results are returned as a json file or bytestring depending
# on the type of job. In the case of error, the error message from the 
# results file is returned.
#

import json
import boto3
import os
import base64
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: ltsvssts_download**")

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
    bucket = s3.Bucket(bucketname)
    
    # configure for RDS access
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    # jobid from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    if "jobid" in event:
      jobid = event["jobid"]
    elif "pathParameters" in event:
      if "jobid" in event["pathParameters"]:
        jobid = event["pathParameters"]["jobid"]
      else:
        raise Exception("requires jobid parameter in pathParameters")
    else:
        raise Exception("requires jobid parameter in event")
        
    print("jobid:", jobid)

    # does the jobid exist?  What's the status of the job if so?
    # open connection to the database:
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    print("**Checking if jobid is valid**")
    
    sql = "SELECT * FROM jobs WHERE jobid = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [jobid])
    
    if row == ():  # no such job
      print("**No such job, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such job...")
      }
    
    print(row)
    
    status = row[2]
    original_data_file = row[3]
    results_file_key = row[5]
    
    print("job status:", status)
    print("original data file:", original_data_file)
    print("results file key:", results_file_key)
    
    # what's the status of the job? There should be 4 cases:
    #   uploaded
    #   processing - ...
    #   completed
    #   error

    if status == "uploaded":
      print("**No results yet, returning...**")
      return {
        'statusCode': 480,
        'body': json.dumps(status)
      }

    if status.startswith("processing"):
      print("**No results yet, returning...**")
      return {
        'statusCode': 481,
        'body': json.dumps(status)
      }

    if status == 'error':
      if results_file_key == "":
        print("**Job status 'unknown error', returning...**")
        return {
          'statusCode': 482,
          'body': json.dumps("error: unknown")
        }
      
      print("**Job status 'error', downloading error results from S3**")
      bucket.download_file(results_file_key, local_filename)
      infile = open(local_filename, "r")
      lines = infile.readlines()
      infile.close()
      
      if len(lines) == 0:
        print("**Job status 'unknown error', given empty results file, returning...**")
        return {
          'statusCode': 482,
          'body': json.dumps("error: unknown, results file was empty")
        }
        
      msg = "error: " + lines[0]
      print("**Job status 'error', results msg:", msg)
      print("**Returning error msg to client...")
      return {
        'statusCode': 482,
        'body': json.dumps(msg)
      }
    
    # completed or something unexpected occured:
    if status != "completed":
      print("**Job status is an unexpected value:", status)
      print("**Returning to client...**")
      msg = "error: unexpected job status of '" + status + "'"
      return {
        'statusCode': 482,
        'body': json.dumps(msg)
      }
      
    # job should be completed
    local_filename = "/tmp/results.json"
    
    print("**Downloading results from S3**")
    
    bucket.download_file(results_file_key, local_filename)
    
    with open(local_filename, "r") as infile:
      results_json = json.load(infile)

    return {
      'statusCode': 200,
      'body': json.dumps(results_json)
    }

  # we end up here if an exception occurs:
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }