#
# Client-side python app for LTSvsSTS app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The functions analyze 20 large CSV files using thresholds
# and phenotypes to extract data summarizing each sample.
#

import requests
import jsons
import json

import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import pandas as pd

from configparser import ConfigParser


############################################################
#
# classes
#

class Job:

  def __init__(self, row):
    self.jobid = row[0]
    self.computeid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]


###################################################################
#
# web_service_get
#
def web_service_get(url):
  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        break;

      retries = retries + 1
      if retries < 3:
        time.sleep(retries)
        continue

      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => get template")
    print("   2 => upload and compute")
    print("   3 => reset database")
    print("   4 => view current jobs")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1

############################################################
#
# reset
#
def reset(baseurl):
  """
  Resets the database back to initial state.

  Parameters - baseurl: baseurl for web service
  Returns - nothing
  """

  try:
    api = '/reset'
    url = baseurl + api

    res = requests.delete(url)

    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        body = res.json()
        print("Error message:", body)
      return

    body = res.json()

    msg = body

    print(msg)
    return

  except Exception as e:
    logging.error("**ERROR: reset() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# template
#
def template(baseurl):
  """
  Gives user template to enter thresholds and phenotypes to analyze.
  Starts with default values if user is not sure where to start.

  Parameters - baseurl: baseurl for web service
  Returns - nothing
  """
  
  try:
    res = None
    api = '/template'
    url = baseurl + api

    res = web_service_get(url)

    if res.status_code == 200: #success
      raw_content = res.text  
      filename = "template.json"
      with open(filename, "w", encoding="utf-8") as f:
        f.write(raw_content)
    
      print("JSON data saved to", filename)
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        body = res.json()
        print("Error message:", body)
          
    return

  except Exception as e:
    logging.error("**ERROR: download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

############################################################
#
# jobs
#
def jobs(baseurl):
  """
  Prints out all the jobs in the database

  Parameters - baseurl: baseurl for web service
  Returns - nothing
  """

  try:
    api = '/jobs'
    url = baseurl + api

    res = web_service_get(url)

    if res.status_code == 200: #success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        body = res.json()
        print("Error message:", body)
      return

    body = res.json()

    jobs = []
    for row in body:
      job = Job(row)
      jobs.append(job)
    if len(jobs) == 0:
      print("no jobs...")
      return

    for job in jobs:
      print(job.jobid)
      print(" ", job.computeid)
      print(" ", job.status)
      print(" ", job.originaldatafile)
      print(" ", job.datafilekey)
      print(" ", job.resultsfilekey)
    return

  except Exception as e:
    logging.error("**ERROR: jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# upload and compute
#
def upload_and_compute(baseurl):
  """
  Prompts the user for template file and compute id then prints result
  and downloads as a CSV or JPG depending on compute function

  Parameters - baseurl: baseurl for web service
  Returns - nothing
  """
  
  try:
    print("Enter json filename>")
    local_filename = input()

    if not pathlib.Path(local_filename).is_file():
      print("JSON file '", local_filename, "' does not exist...")
      return

    print("Enter compute id>")
    print("1: Compute absolute counts of phenotypes per sample")
    print("2: Compute phenotypes as a proportion of total cell count per sample")
    print("3: Compute cell counts per sample")
    print("4: Compute co-occurence matrices separated by LTS vs STS samples")

    computeid = int(input())

    if computeid > 4 or computeid < 1:
      return

    # Open JSON file and load contents
    with open(local_filename, "r") as infile:
      json_data = json.load(infile)

    data = {"filename": local_filename,
            "data": json_data}
    
    # Call the web service:
    res = None
    
    api = '/upload/' + str(computeid)
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code == 200: #success
      pass
    elif res.status_code == 400: # no such user
      body = res.json()
      print(body)
      return
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      return

    # success, extract jobid:
    body = res.json()

    jobid = body

    print("Computation job ID:", jobid)

    while True:
      if computeid not in [1, 2, 3, 4]:
        break
      api = '/results/' + str(jobid)
      url = baseurl + api
      res = web_service_get(url)
      body = res.json()
      status = body

      if res.status_code >= 500:
        break

      print("Status code:", res.status_code)
      if res.status_code == 200:
        if computeid==1:
          df = pd.DataFrame.from_dict(body, orient='index')
          df.to_csv('LTSvsSTS-Phenotype-Counts.csv')
        elif computeid==2:
          df = pd.DataFrame.from_dict(body, orient='index')
          df.to_csv('LTSvsSTS-Phenotype-Proportions.csv')
        elif computeid==3:
          df = pd.DataFrame.from_dict(body, orient='index')
          df.to_csv('LTSvsSTS-Cell-Counts.csv')
        elif computeid==4:
          base64_string = body['heatmap_image']
          image_bytes = base64.b64decode(base64_string)
          output_file = "LTSvsSTS-Co-Occurence-Matrices.jpg"
          with open(output_file, "wb") as f:
              f.write(image_bytes)
          
        print("Job Complete")
        break
      print("Job status:", status)

      if "error" in status:
        break

      duration = ((int(time.time() * 1000) % 10000) % 5) + 2
      time.sleep(duration)
    return

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
# main
#
try:
  print('** Welcome to LTSvsSTS Data Analysis Tool **')
  print()

  sys.tracebacklimit = 0

  config_file = 'ltsvssts-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":
    pass
  else:
    config_file = s

  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  # main processing loop:
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      template(baseurl)
    elif cmd == 2:
      upload_and_compute(baseurl)
    elif cmd == 3:
      reset(baseurl)
    elif cmd == 4:
      jobs(baseurl)
    else:
      print("** Unknown command, try again...")
    cmd = prompt()

  # done
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)