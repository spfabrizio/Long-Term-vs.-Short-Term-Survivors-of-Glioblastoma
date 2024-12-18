# AWS Setup for LTSvsSTS Application

## S3 Setup

1. **Create S3 Bucket**
   - Create a new bucket in S3 named **ltsvsstsapp**.
   - Uncheck the option to block all public access to make the bucket publicly accessible.
   - Enable ACLs (Access Control Lists) for the bucket.

2. **Configure ACLs**
   - Allow public access by enabling the “List” and “Read” permissions for “Everyone (public access).”

3. **Create Folders**
   - Create two folders inside the S3 bucket:
     - **LTSvsSTS-Data/**: Upload all 20 CSV files produced by following the steps in **Data-Collection.md**.
     - **LTSvsSTS-Template/**: Upload `template.json` found in **LTSvsSTS-AWS/Client/**.
<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-s3.png" alt="Description of image" width="550"/>
</div>
<br>

## IAM Setup

1. **Create CLI User**
   - Create a new user named **mycli**.
   - Attach the **AdministratorAccess** policy.
   - Retrieve the user’s access and secret key to use for CLI.
   - Install AWS CLI SDK v2 using [this guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

2. **Create Read-Only User**
   - Create a new user named **s3readonly**.
   - Attach the **AmazonS3ReadOnlyAccess** policy.
   - Retrieve the user’s access and secret keys for "Application running outside AWS."

3. **Create Read-Write User**
   - Create a new user named **s3readwrite**.
   - Create and attach a custom policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR_BUCKET_NAME"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR_BUCKET_NAME/*"
            ]
        }
    ]
}
```

4. **Attach Custom Policy**
   - Name the policy **S3-YOUR-NAME-Read-Write-Policy**.
   - Attach it to the **s3readwrite** user.
   - Retrieve the user’s access and secret keys.

## RDS Setup

1. **Create RDS Database**
   - Use **RDS** to create a MySQL database named **mysql-ltsvssts**.
   - Select **Standard create** and **MySQL**.
   - Configure the database to use the free tier with minimum storage.
   - Ensure the database server is **publicly accessible**.
   - Change **Database authentication** to **Password and IAM database authentication**.

2. **Configure Inbound Rules**
   - Click on **VPC security group** and then go to the **Inbound rules** tab.
   - Click **Edit inbound rules** and add a rule with type **MySQL/Aurora** and source **Anywhere-IPv4**.

3. **Database Setup**
   - Connect to the database using the provided AWS endpoint, username, and password.
   - Run the following SQL commands to create the necessary tables and users:

```sql
CREATE DATABASE IF NOT EXISTS ltsvsstsapp;
USE ltsvsstsapp;

DROP TABLE IF EXISTS jobs;
CREATE TABLE jobs (
    jobid INT NOT NULL AUTO_INCREMENT,
    computeid INT NOT NULL,
    status VARCHAR(256) NOT NULL,
    originaldatafile VARCHAR(256) NOT NULL,
    datafilekey VARCHAR(256) NOT NULL,
    resultsfilekey VARCHAR(256) NOT NULL,
    PRIMARY KEY (jobid),
    UNIQUE (datafilekey)
);

ALTER TABLE jobs AUTO_INCREMENT = 1001;

DROP USER IF EXISTS 'ltsvsstsapp-read-only';
DROP USER IF EXISTS 'ltsvsstsapp-read-write';

CREATE USER 'ltsvsstsapp-read-write' IDENTIFIED BY 'def456!!';
CREATE USER 'ltsvsstsapp-read-only' IDENTIFIED BY 'abc123!!';

GRANT SELECT, SHOW VIEW ON ltsvsstsapp.* TO 'ltsvsstsapp-read-only';
GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ON ltsvsstsapp.* TO 'ltsvsstsapp-read-write';

FLUSH PRIVILEGES;
```
4. **Config File Setup**
  - In any **ltsvssts_/** folder find `ltsvsstsapp-config.ini` and fill in missing details for RDS connection.
  - Fill in missing details with keys for users created.

## Lambda Setup

1. **Upload Lambda Functions**
   - Zip folders **ltsvssts_compute1/**, **ltsvssts_compute2/**, and **ltsvssts_compute3/**.
   - Create corresponding Lambda functions for each of these zipped folders.
   - Set runtime to **Python 3.12** and architecture to **x86-64**.

2. **Add Lambda Layers**
   - Use **KLayers** for Pandas and Numpy with these ARNs:
     - **Pandas**: `arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p312-pandas:11`
     - **Numpy**: `arn:aws:lambda:us-east-2:770693421928:layer:Klayers-p312-numpy:9`

3. **Create Custom Layer**
   - Use AWS CloudShell to create a custom layer for pymysql:

```bash
mkdir python
cd python
pip3 install pymysql typing_extensions==4.6.1 -t .
cd ..
zip -r pymysql-layer.zip python
aws s3 cp pymysql-layer.zip s3://bucket-name
```

4. **Upload Layer**
   - Add this layer to your bucket and copy its S3 link.
   - Select **x86_64** architecture with **Python 3.12** runtime.

5. **Set Ephemeral Storage and Memory**
   - Set **Ephemeral Storage** to **2048 MB**.
   - Set **Memory** to **2048 MB**.
   - Set **Timeout** to **10 minutes**.

6. **Add S3 Triggers**
   - For each compute function, add S3 triggers:
     - **ltsvssts_compute1**: Prefix `LTSvsSTS1-Template/`, Suffix `.json`
     - **ltsvssts_compute2**: Prefix `LTSvsSTS2-Template/`, Suffix `.json`
     - **ltsvssts_compute3**: Prefix `LTSvsSTS3-Template/`, Suffix `.json`
7. **Upload Additional Lambda Functions**
   - Zip folders **ltsvssts_download/**, **ltsvssts_jobs/**, **ltsvssts_reset/**, **ltsvssts_template/**, and **ltsvssts_upload/**.
   - Create lambda functions for each of them with runtime Python 3.12 and architecture x86-64.
   - Add **pymysql-layer** to all of them.
   - Set **Ephemeral Storage** to **512 MB**, **Memory** to **512 MB**, and Timeout to **5 minutes**.
8. **Elastic Container Registry (ECR)**
   - Follow the [ECR tutorial](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-base) to create a Docker iamge for the **ltsvssts_compute4** folder.
   - Create a new lambda function with the created image.
   - Add an S3 trigger with Prefix `LTSvsSTS3-Template/` and Suffix `.json`.

## API Gateway Setup

1. **Create a REST API**
   - Create a REST API with the following triggers:
     - **/jobs**: Triggers **ltsvssts_jobs** lambda.
     - **/reset**: Triggers **ltsvssts_reset** lambda.
     - **/results/{jobid}**: Triggers **ltsvssts_download** lambda.
     - **/template**: Triggers **ltsvssts_template** lambda.
     - **/upload/{computeid}**: Triggers **ltsvssts_upload** lambda.

<br>
<div align="center">
  <img src="/LTSvsSTS-Docs/images/LTSvsSTS-API.png" alt="Description of image" width="200"/>
</div>
<be>

## Client Setup

1. **Client Configuration**
   - Update `ltsvssts-client-config.ini` to include the API Gateway URL.

2. **Run Client**
   - Use Docker to build and run the client:

```bash
docker-build.bat
docker-run.bat
python3 main.py
```
