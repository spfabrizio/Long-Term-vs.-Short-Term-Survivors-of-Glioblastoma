#
# Resets the contents of the LTSvsSTSapp database back
# 0 jobs.
#

import json
import boto3
import os
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: ltsvssts_reset**")
    
    # setup AWS based on config file:
    config_file = 'ltsvsstsapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)

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

    # open connection to the database:
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    # delete all rows from jobs:
    print("**Deleting jobs**")

    sql = "SET FOREIGN_KEY_CHECKS = 0;"
    datatier.perform_action(dbConn, sql)

    sql = "TRUNCATE TABLE jobs;"
    datatier.perform_action(dbConn, sql)

    sql = "SET FOREIGN_KEY_CHECKS = 1;"
    datatier.perform_action(dbConn, sql)

    sql = "ALTER TABLE jobs AUTO_INCREMENT = 1001;"
    datatier.perform_action(dbConn, sql)

    # delete all json files created in these folders
    prefixes = [
      'LTSvsSTS1-Template/',
      'LTSvsSTS2-Template/',
      'LTSvsSTS3-Template/',
      'LTSvsSTS4-Template/',
      'LTSvsSTS-Result/'
    ]

    print("**Deleting files in specified S3 prefixes**")
    for prefix in prefixes:
        bucket.objects.filter(Prefix=prefix).delete()
        
    print("**DONE, returning success**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("success")
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }