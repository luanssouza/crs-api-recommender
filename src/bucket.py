import os, boto3
import pickle

s3 = boto3.client('s3')

def save_object(object_name, obj):
    serialized_obj=pickle.dumps(obj)
    s3.put_object(Bucket=os.environ.get('S3_BUCKET'),Key=str(object_name),Body=serialized_obj)

def loads_object(object_name):
    obj = s3.get_object(Bucket=os.environ.get('S3_BUCKET'),Key=str(object_name))
    serialized_obj = obj['Body'].read()
    return pickle.loads(serialized_obj)