<p align="center">
   <img alt="S3 Inspector" src="https://github.com/kromtech/s3-inspector/blob/logo/logo.png" width="400"/>
</p>

Forked Tool to check AWS S3 bucket permissions

This forked version assumed python prerequisites are installed, doesn't print ok buckets and takes away verbose errors at the end as well as a general refactor.

Also it allows you to add "ignored buckets" that you know are public.

The idea of this fork is that it should run "clean" if configured with expected public buckets.

## What it does
 - Checks all your buckets for public access
 - For "bad" buckets gives you the report with:
   - Indicator if your bucket is public or not
   - Permissions for your bucket if it is public
   - List of URLs to access your bucket (non-public buckets will return Access Denied) if it is public

## Prerequisites
 - **Create IAM user with AmazonS3ReadOnly policy attached**
   - Go to IAM (https://console.aws.amazon.com/iam/home)
   - Click "Users" on the left hand side menu
   - Click "Add user"
   - Fill in user name and check **Programmatic access**
   - Click "Next: Permissions"
   - Click "Attach existing policies directly"
   - Check **AmazonS3ReadOnly** policy
   - Click "Next: Review"
   - Click "Create user"
   - **Copy the credentials**
     - **Access key ID**
     - **Secret access key**
 - **Create ~/.aws/credentials file or paste the credentials in when you run the script**
   - Put the credentials you copied in the previous step here in this format:
```
[default]
aws_access_key_id = <your access key ID goes here>
aws_secret_access_key = <your secret_access_key goes here>
```
## Usage
`python s3inspector.py`

## Report example
![Sample report screenshot](https://github.com/kromtech/s3-inspector/blob/screenshot/samplerun.png "Sample report screenshot")
