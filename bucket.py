import os, boto3

def upload_object(file_name, object_name):
    s3 = boto3.client('s3')
    with open(file_name, "rb") as f:
        s3.upload_fileobj(f, os.environ.get('S3_BUCKET'), object_name)

def download_object(file_name, object_name):
    s3 = boto3.client('s3')
    s3.download_file(os.environ.get('S3_BUCKET'), object_name, file_name)