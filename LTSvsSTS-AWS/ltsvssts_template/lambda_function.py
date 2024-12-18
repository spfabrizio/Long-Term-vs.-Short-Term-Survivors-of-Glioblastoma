#
# Returns the template to enter thesholds for markers
# and phenotypes to analyze marker data from the s3
# LTSvsSTS CSV data
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
    print("**lambda: ltsvssts_template**")

    # setup AWS based on config file:
    config_file = 'ltsvsstsapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    # configure for S3 access:
    s3_profile = 's3readwrite'
    boto3.setup_default_session(profile_name=s3_profile)
    
    s3 = boto3.client('s3') 
    bucketname = configur.get('s3', 'bucket_name')

    object_key = 'LTSvsSTS-Template/ltsvssts-template-defaults.json'

    response = s3.get_object(Bucket=bucketname, Key=object_key)
    file_content = response['Body'].read().decode('utf-8')

    return {
      'statusCode': 200,
      'headers': {
          'Content-Type': 'application/json',
      },
      'body': file_content
    }

  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }