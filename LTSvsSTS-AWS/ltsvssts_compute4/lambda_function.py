#
# Python program to open and process 20 large CSV file, extracting
# all numeric values from the document for creating co-occurence matrices
# showing proportional co-expression. Differentiates between LTS vs STS
# samples
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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import StringIO
from io import BytesIO

from configparser import ConfigParser

def threshold_data(df, thresholds):
    thr_series = pd.Series(thresholds)
    mask = df[thr_series.index] >= thr_series
    df[thr_series.index] = mask.astype(int)

def aggregate_co_occurrence(s3_client, bucket, filelist, thresholddict, markers, dbConn, bucketkey):

    total_cells = 0
    co_occ_mat = np.zeros((len(markers), len(markers)), dtype=float)
    
    file_list_name = list(filelist.keys())[0]
    filelist = filelist[file_list_name]
    filenum = 1
    for file_key in filelist:
        print(f"Processing file: {file_key}")

        obj = s3_client.get_object(Bucket=bucket, Key=file_key)
        df = pd.read_csv(obj['Body'])

        thresholds = thresholddict[file_key]
        threshold_data(df, thresholds)

        df = df[markers]

        n_cells = df.shape[0]
        total_cells += n_cells
        
        co_occ_mat_file = (df.T @ df).values
        co_occ_mat += co_occ_mat_file

        status = 'processing - ' + str(file_key[14:]) + ' ' + str(filenum) + '/10 processed for ' + file_list_name
        filenum += 1
        sql = "update jobs set status = %s where datafilekey = %s"
        modified = datatier.perform_action(dbConn, sql, [status, bucketkey])
    
    diag = np.diag(co_occ_mat)
    with np.errstate(divide='ignore', invalid='ignore'):
        normalized_mat = np.divide(co_occ_mat, diag[:, None])
        normalized_mat[~np.isfinite(normalized_mat)] = 0
    
    return normalized_mat, total_cells

def generate_heatmap(lts_mat, sts_mat, markers, lts_cells, sts_cells):
    fig, axes = plt.subplots(ncols=2, figsize=(20,10))
    
    cbar_ticks = np.arange(0, 1.1, 0.1)
    
    # Plot LTS heatmap
    im1 = axes[0].imshow(lts_mat, cmap='viridis', aspect='equal', vmin=0, vmax=1)
    axes[0].set_title(f'LTS Co-occurrence (N={lts_cells} cells)')
    axes[0].set_xticks(range(len(markers)))
    axes[0].set_yticks(range(len(markers)))
    axes[0].set_xticklabels(markers, rotation=90)
    axes[0].set_yticklabels(markers)
    cbar1 = plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04, ticks=cbar_ticks)
    cbar1.ax.set_yticklabels([f'{t:.1f}' for t in cbar_ticks])
    
    # Plot STS heatmap
    im2 = axes[1].imshow(sts_mat, cmap='viridis', aspect='equal', vmin=0, vmax=1)
    axes[1].set_title(f'STS Co-occurrence (N={sts_cells} cells)')
    axes[1].set_xticks(range(len(markers)))
    axes[1].set_yticks(range(len(markers)))
    axes[1].set_xticklabels(markers, rotation=90)
    axes[1].set_yticklabels(markers)
    cbar2 = plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04, ticks=cbar_ticks)
    cbar2.ax.set_yticklabels([f'{t:.1f}' for t in cbar_ticks])
    
    plt.tight_layout()
    
    # Save plot to BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='jpg', dpi=300)
    plt.close(fig)
    buffer.seek(0)
    
    # Encode image to base64
    img_bytes = buffer.read()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return img_base64

def lambda_handler(event, context):
  dbConn = None
  try:
    print("**STARTING**")
    print("**lambda: ltsvssts_compute4**")

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
      
    if not bucketkey.startswith("LTSvsSTS4-Template/"):
            raise Exception("File is not in 'LTSvsSTS4-Template/' folder. Ignoring event.")
        
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
    
    # update status column in DB for this job

    print("**Opening DB connection**")
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    status = 'processing - starting'
    sql = "update jobs set status = %s where datafilekey = %s"
    modified = datatier.perform_action(dbConn, sql, [status, bucketkey])

    any_file = list(thresholddict.keys())[0]
    markers = list(thresholddict[any_file].keys())

    # define LTS and STS files
    LTS_files = {"LTS files":[
      "LTSvsSTS-Data/NU01713.csv", "LTSvsSTS-Data/NU02064.csv", "LTSvsSTS-Data/NU00866.csv", 
      "LTSvsSTS-Data/NU01482.csv", "LTSvsSTS-Data/NU01405.csv", "LTSvsSTS-Data/NU00908.csv", 
      "LTSvsSTS-Data/NU00295.csv", "LTSvsSTS-Data/NU01115.csv", "LTSvsSTS-Data/NU01094.csv", 
      "LTSvsSTS-Data/NU01798.csv"]}
        
    STS_files = {"STS files": ["LTSvsSTS-Data/NU00429.csv", "LTSvsSTS-Data/NU00468.csv", "LTSvsSTS-Data/NU02738.csv", 
      "LTSvsSTS-Data/NU02514.csv", "LTSvsSTS-Data/NU00431.csv", "LTSvsSTS-Data/NU00759.csv", 
      "LTSvsSTS-Data/NU01420.csv", "LTSvsSTS-Data/NU02359.csv", "LTSvsSTS-Data/NU00826.csv", 
      "LTSvsSTS-Data/NU01929.csv"]}

    print("**Aggregating LTS co-occurrence**")
    lts_mat, lts_cells = aggregate_co_occurrence(s3_client, bucketname, LTS_files, thresholddict, markers, dbConn, bucketkey)
        
    print("**Aggregating STS co-occurrence**")
    sts_mat, sts_cells = aggregate_co_occurrence(s3_client, bucketname, STS_files, thresholddict, markers, dbConn, bucketkey)
    
    print("**Generating heatmap image**")
    heatmap_base64 = generate_heatmap(lts_mat, sts_mat, markers, lts_cells, sts_cells)
        
    result = {
            "heatmap_image": heatmap_base64
        }
    result_json = json.dumps(result)
        
    # upload result JSON to S3
    s3_client.put_object(Bucket=bucketname, Key=bucketkey_results_file, Body=result_json)

    status = 'completed'
    sql = "update jobs set status = %s where datafilekey = %s"
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